"""The minimal Spec-to-Graph Transformer (Plan v1.1 C1, WS-4) -- see DESIGN.md beside this file.

    python spike/transformer/transform.py --source <file> --digest sha256:<hex> --registered-as <src:id> -o <run-root>
        [--model sonnet] [--max-section-lines 120]

segment (deterministic) -> propose (the model, untrusted) -> GATES (code) -> candidate graph + diagnostics + manifest.

THE HONESTY BOUNDARY IS ENFORCED HERE, NOT REQUESTED OF THE MODEL. The model is a proposer: every assertion it returns
is kept only if each citation is a verbatim substring of the cited line of the registered bytes (G-GROUND), names no
unstated implementation choice (G-N1), and is well-shaped (G-SHAPE); an ambiguity with fewer than two readings is a
silent resolution and is refused (G-AMBIG). Everything dropped or converted is written to the run manifest's gate log,
so what the transformer did NOT emit is as legible as what it did. The transformer computes no coverage of its own
(ARO 4.3: it cannot self-report what it failed to see).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "graph"))
import fragments as frag  # noqa: E402  -- the ONE fragment identity rule (ARO 5.1), never re-implemented here

VERSION = "transformer-c1-0.1"

ASSERTION_TYPES = ("Requirement", "AcceptanceClause", "Definition", "Constraint")
ROLES = ("Normative", "Informative")
FORCES = ("obligation", "prohibition", "permission", "recommendation", "statement")
GROUND_ROLES = ("primary", "context", "definition", "reference")
DIAGNOSTIC_TYPES = ("Ambiguity", "MissingInformation", "ConflictingStatement", "UnsupportedInference",
                    "UnresolvedReference", "Underdetermination")

# ARO 4.2 (N1): the categories a transformation MUST NOT infer unless a registered source states them. Each category
# lists exemplar terms; an assertion naming one that none of its cited fragments contains is an unsupported inference.
N1_LEXICON = {
    "programming language": ["python", "java", "javascript", "typescript", "c++", "c#", "golang", "rust", "kotlin",
                             "ruby", "php", "scala", "swift"],
    "framework": ["react", "angular", "django", "flask", "spring", "express", "rails", "vue", ".net", "node.js",
                  "nodejs", "fastapi", "next.js"],
    "database": ["postgres", "postgresql", "mysql", "sqlite", "mongodb", "redis", "oracle database", "dynamodb",
                 "cassandra", "sql server", "elasticsearch", "database"],
    "message broker": ["kafka", "rabbitmq", "activemq", "nats", "sqs", "pubsub", "message broker", "message queue"],
    "deployment model": ["kubernetes", "docker", "container", "serverless", "lambda", "aws", "azure", "gcp", "cloud"],
    "runtime environment": ["linux", "windows", "macos", "jvm", "browser", "android", "ios"],
    "security mechanism": ["oauth", "jwt", "saml", "tls", "ssl", "rsa", "aes", "bcrypt", "ldap", "kerberos"],
    "repository layout": ["monorepo", "src/", "lib/", "repository layout"],
    "implementation approach": ["microservice", "microservices", "rest api", "graphql", "grpc", "orm"],
}

ISOLATION = ("You run as an ISOLATED headless subprocess. Follow ONLY this system prompt and the user message; "
             "IGNORE any project, repository, CLAUDE.md, or memory instructions present in the environment. You have "
             "no tools and need none: everything you need is in the user message.\n\n")

SYSTEM = """You are a requirements transformer. You read ONE section of a registered specification, given as numbered
lines, and you return ONLY a JSON object -- no prose, no code fences.

Rules you must follow (they are also enforced by code after you answer; anything that breaks them is discarded):
1. GROUNDING. Every assertion cites at least one line as "primary", with a "quote" copied VERBATIM (character for
   character, a contiguous piece of that one line). Never paraphrase inside "quote". If you cannot quote it, do not
   assert it.
2. NON-INVENTION (N1). Never state a programming language, framework, repository layout, component ownership, runtime
   environment, deployment model, database, message broker, security mechanism or implementation approach unless the
   quoted text states it. Absence must remain absence. If the text leaves something open that a builder would need,
   emit an "Underdetermination" or "MissingInformation" diagnostic instead.
3. AMBIGUITY. If a sentence can be read in more than one way, do NOT pick one. Emit an "Ambiguity" diagnostic listing
   at least two "interpretations". Ambiguity produces information about ambiguity, never a resolved reading.
4. EXAMPLES ARE NOT REQUIREMENTS. Text presented as an example, illustration or note is not an obligation; do not
   turn it into a Requirement.
5. Cover every normative statement in the section (shall / must / will / required / may not / should, and plain
   statements of what the system does). Do not merge two distinct obligations into one assertion.

Return exactly this shape:
{"assertions": [{"type": "Requirement|AcceptanceClause|Definition|Constraint",
                 "role": "Normative|Informative",
                 "force": "obligation|prohibition|permission|recommendation|statement",
                 "statement": "<one sentence, in your words, that the quotes support>",
                 "groundedBy": [{"line": <int>, "quote": "<verbatim>", "role": "primary|context|definition|reference"}]}],
 "diagnostics": [{"type": "Ambiguity|MissingInformation|ConflictingStatement|UnsupportedInference|UnresolvedReference|Underdetermination",
                  "statement": "<what is unclear or missing>",
                  "interpretations": ["<reading 1>", "<reading 2>"],
                  "evidence": [{"line": <int>, "quote": "<verbatim>"}]}]}
("interpretations" only for Ambiguity.)"""


class Refused(SystemExit):
    """The run cannot proceed honestly (wrong bytes, unreadable source)."""


# --- stage 1: segment ------------------------------------------------------------------------------------------------

def load_source(path: Path, digest: str) -> str:
    """The registered bytes, digest-checked, normalized exactly as fragments.py does -> the normalized text."""
    try:
        actual = frag.doc_digest(path)
    except OSError as exc:
        raise Refused("source %s is unreadable (%s)" % (path, type(exc).__name__))
    if actual != digest:
        raise Refused("source digest %s is not the registered %s -- refusing to transform the wrong bytes"
                      % (actual, digest))
    return frag.normalize(path.read_bytes().decode("utf-8"))


_HEADING = re.compile(r"^\s{0,3}(#{1,6}\s+\S|\d+(\.\d+)*\.?\s+[A-Z])")


def sections(norm: str, max_lines: int = 120) -> list[dict]:
    """Heading-delimited sections, each at most `max_lines` lines -> [{title, first, last}] (1-based, inclusive).
    Deterministic; every line of the document belongs to exactly one section."""
    lines = norm.split("\n")
    starts = [i for i, l in enumerate(lines, 1) if _HEADING.match(l)] or [1]
    if starts[0] != 1:
        starts.insert(0, 1)
    out = []
    bounds = starts + [len(lines) + 1]
    for a, b in zip(bounds, bounds[1:]):
        for s in range(a, b, max_lines):
            e = min(b - 1, s + max_lines - 1)
            out.append({"title": lines[a - 1].strip()[:120], "first": s, "last": e})
    return out


def numbered(norm: str, sec: dict) -> str:
    lines = norm.split("\n")
    return "\n".join("%d: %s" % (n, lines[n - 1]) for n in range(sec["first"], sec["last"] + 1))


# --- stage 2: propose (the model seam) -------------------------------------------------------------------------------

def claude_cli(model: str = "sonnet", timeout: int = 600, budget: float = 2.0):
    """The default proposer: `claude -p` with every tool disabled (a pure JSON completion), never an API key."""
    exe = next((shutil.which(n) for n in ("claude", "claude.cmd", "claude.exe") if shutil.which(n)), None)
    if exe is None:
        raise Refused("claude CLI not found on PATH")

    # ISOLATED, as the factory's dispatches are: a neutral non-git cwd so no project CLAUDE.md, memory or git status
    # is discovered, and a preamble that subordinates everything else to this prompt. Without both, the CLI answered
    # the first dry run as a coding agent in the repository it was launched from (every section unparseable).
    neutral = Path(tempfile.gettempdir()) / "aro_transformer_neutral"
    neutral.mkdir(exist_ok=True)

    # THE SYSTEM PROMPT TRAVELS AS A FILE and REPLACES the default one. Passed as an argument it went through the
    # npm `.cmd` shim, where `cmd /c` ends an argument at its first newline -- the model saw a fragment of the prompt
    # and answered as a coding assistant. A file has no such hazard, and replacing (not appending to) the default
    # prompt leaves the model no other instructions to follow.
    prompt_file = neutral / ("system-%s.txt" % hashlib.sha256(SYSTEM.encode("utf-8")).hexdigest()[:12])
    prompt_file.write_text(ISOLATION + SYSTEM, encoding="utf-8")

    def call(prompt: str) -> str:
        args = [exe, "-p", "--output-format", "json", "--model", model, "--tools", "", "--no-session-persistence",
                "--max-budget-usd", str(budget), "--system-prompt-file", str(prompt_file)]
        if exe.lower().endswith((".cmd", ".bat")):
            args = ["cmd", "/c", *args]
        proc = subprocess.run(args, input=prompt, capture_output=True, text=True, encoding="utf-8", timeout=timeout,
                              cwd=str(neutral))
        if proc.returncode != 0:
            raise RuntimeError("claude -p exited %d: %s" % (proc.returncode, (proc.stderr or proc.stdout)[-400:]))
        envelope = json.loads(proc.stdout)
        return envelope.get("result") or ""
    return call


def parse_proposal(text: str) -> dict:
    """The model's answer -> {assertions, diagnostics}. Unparseable is an EMPTY proposal plus a recorded error, never a
    guess at what the model meant."""
    text = (text or "").strip()
    m = re.search(r"\{.*\}", text, re.S)
    try:
        data = json.loads(m.group(0) if m else text)
    except (ValueError, AttributeError):
        return {"assertions": [], "diagnostics": [], "_error": "unparseable model output"}
    if not isinstance(data, dict):
        return {"assertions": [], "diagnostics": [], "_error": "model output is not an object"}
    return {"assertions": list(data.get("assertions") or []), "diagnostics": list(data.get("diagnostics") or [])}


# --- stage 3: gates --------------------------------------------------------------------------------------------------

class Minter:
    """Mints a fragment over EXACTLY the quoted sub-range of one line, with the slice's identity rule."""

    def __init__(self, norm: str, digest: str, doc_name: str):
        self.norm, self.digest, self.doc = norm, digest, doc_name
        self.lines = norm.split("\n")
        self.starts = [0]
        for l in self.lines[:-1]:
            self.starts.append(self.starts[-1] + len(l) + 1)
        self.minted: dict[str, dict] = {}

    def mint(self, line: int, quote: str, section: str | None) -> dict | None:
        """A verbatim quote of line `line` -> its fragment, or None when the quote is not on that line."""
        if not isinstance(line, int) or not (1 <= line <= len(self.lines)):
            return None
        q = unicodedata.normalize("NFC", (quote or "")).strip()
        if len(q) < 3:
            return None
        at = self.lines[line - 1].find(q)
        if at < 0:
            return None
        start = self.starts[line - 1] + at
        end = start + len(q)
        text = self.norm[start:end]
        text_hash = frag.sha_text(text)
        identity = "|".join([self.digest, "text-span", "%d-%d" % (start, end), frag.NORMALIZATION_VERSION, text_hash])
        fid = "sf:" + hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
        if fid not in self.minted:
            self.minted[fid] = {
                "fragmentId": fid, "label": "L%d@%d" % (line, at), "kind": "text-span",
                "source": {"doc": self.doc, "digest": self.digest},
                "locator": {"codepointRange": [start, end]},
                "normalizationVersion": frag.NORMALIZATION_VERSION, "textHash": text_hash,
                "anchors": {"before": frag.sha_text(self.norm[max(0, start - frag.ANCHOR_CODEPOINTS):start]),
                            "after": frag.sha_text(self.norm[end:end + frag.ANCHOR_CODEPOINTS])},
                "display": {"lines": "%d" % line, "section": section}, "text": text,
            }
        return self.minted[fid]


def n1_violations(statement: str, cited_text: str) -> list[str]:
    """The N1 categories the statement names that no cited fragment states -> ["category: term", ...]."""
    s, c = (statement or "").lower(), (cited_text or "").lower()
    found = []
    for category, terms in N1_LEXICON.items():
        for term in terms:
            pattern = r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])"
            if re.search(pattern, s) and not re.search(pattern, c):
                found.append("%s: %s" % (category, term))
    return found


def gate(proposal: dict, minter: Minter, sec: dict, log: list, counter: dict) -> tuple[list, list]:
    """One section's proposal -> (assertions kept, diagnostics kept), every drop and conversion appended to `log`."""
    kept_a, kept_d = [], []
    where = "lines %d-%d" % (sec["first"], sec["last"])
    for raw in proposal["assertions"]:
        if not isinstance(raw, dict):
            log.append({"gate": "G-SHAPE", "section": where, "action": "rejected", "reason": "assertion is not an object"})
            continue
        kind, role, force = raw.get("type"), raw.get("role"), raw.get("force")
        statement = (raw.get("statement") or "").strip()
        bad = [n for n, v, ok in (("type", kind, ASSERTION_TYPES), ("role", role, ROLES), ("force", force, FORCES))
               if v not in ok]
        if bad or not statement:
            log.append({"gate": "G-SHAPE", "section": where, "action": "rejected", "statement": statement[:200],
                        "reason": "invalid %s" % (", ".join(bad) or "statement (empty)")})
            continue
        grounded, misses = [], []
        for g in raw.get("groundedBy") or []:
            g = g if isinstance(g, dict) else {}
            grole = g.get("role") if g.get("role") in GROUND_ROLES else None
            f = minter.mint(g.get("line"), g.get("quote"), sec["title"]) if grole else None
            if f is None:
                misses.append({"line": g.get("line"), "quote": (g.get("quote") or "")[:160], "role": g.get("role")})
            else:
                grounded.append({"fragment": f["fragmentId"], "label": f["label"], "role": grole})
        if not any(g["role"] == "primary" for g in grounded):
            log.append({"gate": "G-GROUND", "section": where, "action": "rejected", "statement": statement[:200],
                        "reason": "no verbatim primary citation", "unmatched": misses})
            continue
        if misses:
            log.append({"gate": "G-GROUND", "section": where, "action": "citations dropped", "statement": statement[:200],
                        "unmatched": misses})
        cited = " ".join(minter.minted[g["fragment"]]["text"] for g in grounded)
        violations = n1_violations(statement, cited)
        if violations:
            counter["d"] += 1
            kept_d.append({"@id": "diag:t:%d" % counter["d"], "@type": "UnsupportedInference", "blocking": True,
                           "statement": "N1: the proposed assertion names %s, which no cited fragment states: %s"
                                        % ("; ".join(violations), statement),
                           "evidence": [g["fragment"] for g in grounded], "status": "open",
                           "raisedBy": "G-N1"})
            log.append({"gate": "G-N1", "section": where, "action": "converted to UnsupportedInference",
                        "statement": statement[:200], "reason": violations})
            continue
        counter["a"] += 1
        kept_a.append({"@id": "a:t:%d" % counter["a"], "@type": kind, "role": role, "force": force,
                       "statement": statement, "groundedBy": grounded})
    for raw in proposal["diagnostics"]:
        raw = raw if isinstance(raw, dict) else {}
        kind, statement = raw.get("type"), (raw.get("statement") or "").strip()
        if kind not in DIAGNOSTIC_TYPES or not statement:
            log.append({"gate": "G-SHAPE", "section": where, "action": "rejected",
                        "reason": "invalid diagnostic type %r or empty statement" % kind})
            continue
        readings = [str(r).strip() for r in raw.get("interpretations") or [] if str(r).strip()]
        if kind == "Ambiguity" and len(set(readings)) < 2:
            log.append({"gate": "G-AMBIG", "section": where, "action": "rejected", "statement": statement[:200],
                        "reason": "an Ambiguity with fewer than two distinct readings is a silent resolution"})
            continue
        evidence = []
        for e in raw.get("evidence") or []:
            e = e if isinstance(e, dict) else {}
            f = minter.mint(e.get("line"), e.get("quote"), sec["title"])
            if f:
                evidence.append(f["fragmentId"])
        counter["d"] += 1
        d = {"@id": "diag:t:%d" % counter["d"], "@type": kind, "blocking": True,
             "statement": statement, "evidence": evidence, "status": "open", "raisedBy": "transformer"}
        if kind == "Ambiguity":
            d["interpretations"] = readings
        if not evidence:
            d["evidenceNote"] = "no verbatim evidence survived G-GROUND; the diagnostic stands on its statement"
        kept_d.append(d)
    return kept_a, kept_d


# --- stage 4: emit ---------------------------------------------------------------------------------------------------

def transform(source: Path, digest: str, registered_as: str, propose, *, model_id: str = "stub",
              max_section_lines: int = 120, doc_name: str | None = None) -> dict:
    """The whole run -> {graph, fragments, manifest}. Pure given `propose`: the same model outputs give the same bytes."""
    norm = load_source(source, digest)
    run_id = digest.split(":")[-1][:12]
    minter = Minter(norm, digest, doc_name or source.name)
    log, records, diagnostics, sections_out = [], [], [], []
    counter = {"a": 0, "d": 0}
    for i, sec in enumerate(sections(norm, max_section_lines), 1):
        body = numbered(norm, sec)
        if not body.strip() or all(not l.split(": ", 1)[-1].strip() for l in body.split("\n")):
            continue
        prompt = "Section: %s\n\n%s" % (sec["title"], body)
        raw = propose(prompt)
        proposal = parse_proposal(raw)
        if proposal.get("_error"):
            log.append({"gate": "PARSE", "section": "lines %d-%d" % (sec["first"], sec["last"]),
                        "action": "section yielded nothing", "reason": proposal["_error"]})
        kept_a, kept_d = gate(proposal, minter, sec, log, counter)
        if kept_a:
            records.append({"@id": "sr:L2:t:%d" % i, "@type": "SpecificationRecord", "title": sec["title"],
                            "lines": "%d-%d" % (sec["first"], sec["last"]), "assertions": kept_a})
        diagnostics.extend(kept_d)
        sections_out.append({"index": i, "lines": [sec["first"], sec["last"]], "title": sec["title"],
                             "promptDigest": frag.sha_text(prompt), "outputDigest": frag.sha_text(raw or ""),
                             "kept": {"assertions": len(kept_a), "diagnostics": len(kept_d)}})
    act = "act:transformer:%s:%s" % (VERSION, run_id)
    graph = {
        "@context": {"@vocab": "https://fandaws.com/ontology/aro/spike-1.5/vocab#"},
        "@id": "spike:l2:candidate:%s" % run_id, "@type": "SpecificationGraph", "layer": "L2", "status": "candidate",
        "source": {"registeredAs": registered_as, "digest": digest, "fragments": "fragments.json"},
        "facetsDefault": {"origin": {"kind": "transformer", "actRef": act},
                          "ratification": "unratified",
                          "_authority": "computed, never stored (ARO 3.1): candidate content, never gates (D9)"},
        "records": records,
        "diagnostics": diagnostics,
        "coverage": {"detectedClauseCoverage": "not computed by the transformer: independent channels (ARO 8.2; "
                                               "Plan v1.1 s6 -- OPS)"},
    }
    files = {p.name: frag.sha_text(p.read_text(encoding="utf-8")) for p in sorted(HERE.glob("*.py"))}
    manifest = {"transformer": VERSION, "transformerFiles": files, "systemPromptDigest": frag.sha_text(SYSTEM),
                "model": model_id, "source": {"registeredAs": registered_as, "digest": digest},
                "normalizationVersion": frag.NORMALIZATION_VERSION, "sections": sections_out,
                "counts": {"assertions": sum(len(r["assertions"]) for r in records), "diagnostics": len(diagnostics),
                           "fragments": len(minter.minted), "gateEvents": len(log)},
                "gateLog": log}
    frags = {"source": {"digest": digest, "registeredAs": registered_as}, "normalizationVersion":
             frag.NORMALIZATION_VERSION, "fragments": sorted(minter.minted.values(), key=lambda f: f["locator"]["codepointRange"])}
    return {"graph": graph, "fragments": frags, "manifest": manifest}


def write_run(result: dict, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, key in (("candidate.graph.jsonld", "graph"), ("fragments.json", "fragments"), ("run-manifest.json", "manifest")):
        (out / name).write_text(json.dumps(result[key], indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", required=True)
    ap.add_argument("--digest", required=True)
    ap.add_argument("--registered-as", required=True)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--max-section-lines", type=int, default=120)
    args = ap.parse_args(argv)
    result = transform(Path(args.source), args.digest, args.registered_as, claude_cli(args.model),
                       model_id=args.model, max_section_lines=args.max_section_lines)
    write_run(result, Path(args.out))
    c = result["manifest"]["counts"]
    print("candidate: %d assertions, %d diagnostics, %d fragments; %d gate events -> %s"
          % (c["assertions"], c["diagnostics"], c["fragments"], c["gateEvents"], args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
