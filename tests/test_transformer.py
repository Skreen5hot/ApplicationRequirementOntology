"""C1 (Plan v1.1 WS-4): the minimal transformer's gates enforce the honesty boundary in code. The model is a stubbed
seam here, so every pin states what the GATES do with a given proposal -- never what a model happens to say."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "spike" / "transformer"))
import transform as t  # noqa: E402

SPEC = """# 1. Intake

The system shall record every submission with its arrival time.
Submissions larger than 10 MB shall be rejected.
For example, a reviewer might sort submissions by size.

# 2. Storage

Records are kept in PostgreSQL for seven years.
The archive must be searchable quickly.
"""


@pytest.fixture
def source(tmp_path):
    p = tmp_path / "spec.md"
    p.write_bytes(SPEC.encode("utf-8"))
    return p, "sha256:" + hashlib.sha256(SPEC.encode("utf-8")).hexdigest()


def _a(statement, line, quote, **kw):
    a = {"type": "Requirement", "role": "Normative", "force": "obligation", "statement": statement,
         "groundedBy": [{"line": line, "quote": quote, "role": "primary"}]}
    a.update(kw)
    return a


def _run(source, by_section):
    """by_section: {section title prefix: proposal dict} -- the stub answers per section."""
    path, digest = source

    def propose(prompt):
        title = prompt.split("\n", 1)[0]
        for prefix, proposal in by_section.items():
            if prefix in title:
                return json.dumps(proposal)
        return json.dumps({"assertions": [], "diagnostics": []})
    return t.transform(path, digest, "src:synthetic", propose)


def _log(result, gate):
    return [e for e in result["manifest"]["gateLog"] if e["gate"] == gate]


def _assertions(result):
    return [a for r in result["graph"]["records"] for a in r["assertions"]]


def test_a_verbatim_primary_citation_is_kept_and_minted_over_exactly_the_quote(source):
    r = _run(source, {"Intake": {"assertions": [_a("Every submission is recorded with its arrival time.", 3,
                                                   "shall record every submission with its arrival time")]}})
    [a] = _assertions(r)
    [f] = r["fragments"]["fragments"]
    start, end = f["locator"]["codepointRange"]
    norm = t.frag.normalize(SPEC)
    assert norm[start:end] == "shall record every submission with its arrival time" == f["text"]
    assert f["textHash"] == t.frag.sha_text(f["text"]) and a["groundedBy"][0]["fragment"] == f["fragmentId"]


def test_G_GROUND_rejects_an_assertion_whose_quote_is_not_on_its_line(source):
    r = _run(source, {"Intake": {"assertions": [
        _a("Submissions are encrypted.", 3, "shall encrypt every submission"),           # invented quote
        _a("Big submissions are rejected.", 3, "larger than 10 MB shall be rejected")]}})  # real text, WRONG line
    assert _assertions(r) == []
    assert [e["reason"] for e in _log(r, "G-GROUND")] == ["no verbatim primary citation"] * 2
    assert r["fragments"]["fragments"] == [], "nothing is minted for a citation that does not match"


def test_a_failed_secondary_citation_is_dropped_and_logged_while_the_assertion_stands(source):
    a = _a("Every submission is recorded.", 3, "shall record every submission")
    a["groundedBy"].append({"line": 4, "quote": "not in the text", "role": "context"})
    r = _run(source, {"Intake": {"assertions": [a]}})
    [kept] = _assertions(r)
    assert len(kept["groundedBy"]) == 1 and _log(r, "G-GROUND")[0]["action"] == "citations dropped"


def test_G_N1_converts_an_unstated_implementation_choice_into_UnsupportedInference(source):
    r = _run(source, {"Storage": {"assertions": [
        _a("The archive is searchable quickly using Elasticsearch and a Redis cache.", 10,
           "The archive must be searchable quickly")]}})
    assert _assertions(r) == []
    [d] = r["graph"]["diagnostics"]
    assert d["@type"] == "UnsupportedInference" and "database: redis" in d["statement"] and d["raisedBy"] == "G-N1"


def test_G_N1_keeps_an_implementation_choice_the_source_STATES(source):
    r = _run(source, {"Storage": {"assertions": [
        _a("Records are kept in PostgreSQL for seven years.", 9, "Records are kept in PostgreSQL for seven years")]}})
    assert len(_assertions(r)) == 1 and r["graph"]["diagnostics"] == []


def test_G_AMBIG_refuses_a_single_reading_ambiguity_and_keeps_an_enumerated_one(source):
    one = {"type": "Ambiguity", "statement": "'quickly' is unquantified", "interpretations": ["under one second"],
           "evidence": [{"line": 10, "quote": "searchable quickly"}]}
    two = dict(one, interpretations=["under one second", "faster than the current system"])
    r = _run(source, {"Storage": {"assertions": [], "diagnostics": [one, two]}})
    [d] = r["graph"]["diagnostics"]
    assert d["interpretations"] == two["interpretations"] and len(d["evidence"]) == 1
    assert _log(r, "G-AMBIG")[0]["action"] == "rejected"


def test_G_SHAPE_rejects_unknown_types_and_empty_statements(source):
    r = _run(source, {"Intake": {"assertions": [_a("x", 3, "shall record every submission", type="Wish"),
                                                _a("", 3, "shall record every submission")],
                                 "diagnostics": [{"type": "Hunch", "statement": "s"}]}})
    assert _assertions(r) == [] and r["graph"]["diagnostics"] == [] and len(_log(r, "G-SHAPE")) == 3


def test_unparseable_model_output_yields_nothing_and_is_logged(source):
    path, digest = source
    r = t.transform(path, digest, "src:synthetic", lambda prompt: "I think the system should...")
    assert _assertions(r) == [] and {e["gate"] for e in r["manifest"]["gateLog"]} == {"PARSE"}


def test_the_wrong_bytes_refuse_the_run(source):
    path, _digest = source
    with pytest.raises(t.Refused, match="refusing to transform the wrong bytes"):
        t.transform(path, "sha256:" + "0" * 64, "src:synthetic", lambda p: "{}")


def test_candidate_facets_are_transformer_origin_unratified_and_coverage_is_not_self_reported(source):
    g = _run(source, {})["graph"]
    assert g["status"] == "candidate" and g["facetsDefault"]["origin"]["kind"] == "transformer"
    assert g["facetsDefault"]["ratification"] == "unratified"
    assert g["coverage"]["detectedClauseCoverage"].startswith("not computed by the transformer")


def test_the_run_is_byte_deterministic_given_the_same_model_outputs(source):
    props = {"Intake": {"assertions": [_a("Every submission is recorded.", 3, "shall record every submission")]}}
    a, b = _run(source, props), _run(source, props)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_sections_cover_every_line_exactly_once():
    norm = t.frag.normalize(SPEC)
    secs = t.sections(norm, max_lines=3)
    covered = [n for s in secs for n in range(s["first"], s["last"] + 1)]
    assert covered == list(range(1, len(norm.split("\n")) + 1))
