# SPDX-License-Identifier: Apache-2.0
"""The act tool (Plan v1.1 A5): every refusal pinned, and the one success path, on a copy of the real queue.

Each refusal is a behaviour, and a refusal without a pin is a naked guard (CP/SM v0.4.9 s12.4, R9)."""

from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path

import pytest

from conftest import load_tool

ROOT = Path(__file__).resolve().parents[1]
act = load_tool("aro_act", "tools/act.py")
layout_rule = load_tool("spike_layout_rule_for_act", "spike/graph/rules/layout_rule.py")


@pytest.fixture()
def repo(tmp_path):
    """A copy of the spike tree: the real queue and artifacts, so digests are the real ones."""
    shutil.copytree(ROOT / "spike", tmp_path / "spike", ignore=shutil.ignore_patterns("__pycache__", "out"))
    return tmp_path


def _add_item(repo, **row):
    q = repo / "spike" / "measurements" / "ratification-queue.jsonl"
    q.write_text(q.read_text(encoding="utf-8") + json.dumps(row) + "\n", encoding="utf-8")


def _fresh_item(repo, item_id="rq-900", **extra):
    """A pending item bound to a real record at its real digest (rq-003's record, re-queued)."""
    src = json.loads((repo / act.QUEUE_REL).read_text(encoding="utf-8").splitlines()[2])
    assert src["id"] == "rq-003"
    row = {k: src[k] for k in ("record", "artifact", "recordDigest", "kind")}
    row.update({"id": item_id, "batch": "BX", "queuedAt": "2026-09-29T10:00:00-04:00"}, **extra)
    _add_item(repo, **row)
    return row


def test_the_tool_and_the_projector_compute_the_same_digest_on_every_live_row():
    """The tool restates the projector's canonical form; if they ever disagreed, an act the tool accepts
    would be one the projector refuses. Checked on every live, record-addressed row of the real queue."""
    q = act.Queue(ROOT)
    checked = 0
    dead = q.superseded()
    for _, row in q.rows:
        if row["id"] in dead:
            # A superseded row stays bound to the bytes it was queued against -- that is what superseding means
            # (rq-012 -> rq-013 after an act; rq-017 -> rq-036 before one). Only live rows must match today's bytes.
            continue
        if row.get("recordDigest"):
            rec = act._find(json.loads((ROOT / row["artifact"]).read_text(encoding="utf-8")), row["record"])
            assert act.digest(rec) == layout_rule.digest(rec) == row["recordDigest"], row["id"]
            checked += 1
    assert checked >= 9


def test_list_is_read_only_and_excludes_acted_and_superseded(repo):
    """Asserts the POSITIVE on a seeded queue (IA Ops finding 2026-10-17, HIGH, bullet 4): an implementation
    returning [] unconditionally fails here."""
    _fresh_item(repo, item_id="rq-900")                                          # unacted, live -> listed
    _fresh_item(repo, item_id="rq-901", act="accepted", actedAt="2026-10-17T00:00:00-04:00", actor="Aaron")
    _fresh_item(repo, item_id="rq-902")                                          # superseded by rq-903 -> not listed
    _fresh_item(repo, item_id="rq-903", supersedes="rq-902")                     # unacted, live -> listed
    before = (repo / act.QUEUE_REL).read_bytes()
    ids = [r["id"] for r in act.Queue(repo).pending()]
    assert {"rq-900", "rq-903"} <= set(ids), ids
    assert not {"rq-901", "rq-902"} & set(ids), ids
    assert "rq-002" not in ids, "superseded by rq-012"
    assert not any(i in ids for i in ("rq-003", "rq-011")), "already acted"
    assert (repo / act.QUEUE_REL).read_bytes() == before


@pytest.mark.parametrize("actor", ["", "   ", "claude", "ia-dev", "aro-dev-agent", "Assistant"])
def test_an_act_without_a_human_actor_is_refused(repo, actor):
    _fresh_item(repo)
    with pytest.raises(act.Refused):
        act.act(act.Queue(repo), "rq-900", "accept", actor)


def test_an_item_already_acted_on_is_refused(repo):
    with pytest.raises(act.Refused, match="already acted"):
        act.act(act.Queue(repo), "rq-003", "accept", "Aaron")


def test_a_superseded_item_is_refused(repo):
    with pytest.raises(act.Refused, match="superseded"):
        act.act(act.Queue(repo), "rq-002", "ratify", "Aaron")


def test_a_record_changed_since_it_was_queued_is_refused(repo):
    _fresh_item(repo)
    art = repo / "spike" / "graph" / "l2" / "srs-slice.graph.jsonld"
    data = json.loads(art.read_text(encoding="utf-8"))
    act._find(data, "sr:L2:C-S8")["title"] = "edited after queueing"
    art.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(act.Refused, match="changed since it was queued"):
        act.act(act.Queue(repo), "rq-900", "accept", "Aaron")


def test_decide_needs_a_decision_among_the_options(repo):
    _fresh_item(repo, options=["A: one", "B: two"])
    q = act.Queue(repo)
    with pytest.raises(act.Refused, match="needs --decision"):
        act.act(q, "rq-900", "decide", "Aaron")
    with pytest.raises(act.Refused, match="not one of"):
        act.act(q, "rq-900", "decide", "Aaron", decision="C")


def test_a_decision_on_a_non_decide_verb_is_refused(repo):
    _fresh_item(repo)
    with pytest.raises(act.Refused, match="only meaningful with decide"):
        act.act(act.Queue(repo), "rq-900", "accept", "Aaron", decision="A")


def test_an_accepted_act_is_recorded_bound_to_its_digest_and_nothing_else_moves(repo):
    row = _fresh_item(repo)
    path = repo / act.QUEUE_REL
    before = path.read_text(encoding="utf-8").splitlines(keepends=True)
    when = dt.datetime(2026, 9, 29, 14, 0, tzinfo=dt.timezone(dt.timedelta(hours=-4)))
    out = act.act(act.Queue(repo), "rq-900", "accept", "Aaron", sitting_start="2026-09-29T13:30:00-04:00", now=when)
    assert out["confers"] is True and out["actDigest"] == row["recordDigest"]
    after = path.read_text(encoding="utf-8").splitlines(keepends=True)
    assert after[:-1] == before[:-1], "every other line is byte-identical"
    written = json.loads(after[-1])
    assert written["act"] == "accepted" and written["actor"] == "Aaron"
    assert written["actedAt"] == "2026-09-29T14:00:00-04:00" and written["sittingStart"] == "2026-09-29T13:30:00-04:00"
    with pytest.raises(act.Refused, match="already acted"):
        act.act(act.Queue(repo), "rq-900", "accept", "Aaron")


def test_amend_is_recorded_and_confers_nothing(repo):
    _fresh_item(repo)
    out = act.act(act.Queue(repo), "rq-900", "amend", "Aaron", note="severity values changed")
    assert out["act"] == "amended" and out["confers"] is False


def test_cli_exit_codes_and_json(repo, capsys):
    _fresh_item(repo)
    assert act.main(["--root", str(repo), "--json", "list"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert "rq-900" in [r["id"] for r in listed["pending"]]
    assert act.main(["--root", str(repo), "--json", "act", "rq-900", "accept", "--actor", "claude"]) == 1
    assert "refused" in json.loads(capsys.readouterr().out)
    assert act.main(["--root", str(repo), "act", "rq-900", "bless", "--actor", "Aaron"]) == 2
    assert act.main(["--root", str(repo / "nowhere"), "list"]) == 2
    assert act.main(["--root", str(repo), "act", "rq-900", "accept", "--actor", "Aaron"]) == 0


def test_the_projector_accepts_what_the_tool_records(repo):
    """The end that matters: a row the tool writes is one the projector's eligibility rule honours."""
    project = load_tool("spike_projector_for_act", "spike/projections/project.py")
    row = _fresh_item(repo)
    act.act(act.Queue(repo), "rq-900", "accept", "Aaron")
    queue = [json.loads(l) for l in (repo / act.QUEUE_REL).read_text(encoding="utf-8").splitlines() if l.strip()]
    written = [r for r in queue if r["id"] == "rq-900"]
    rest = [r for r in queue if r.get("record") != row["record"]]
    hit, why = project.act_for(rest + written, row["record"], row["recordDigest"])
    assert hit is not None and hit["id"] == "rq-900", why


def test_the_cli_survives_a_cp1252_console(repo, monkeypatch):
    """Found by the first live dry run: a Windows console is cp1252 and the queue titles carry arrows and em
    dashes, so `list` crashed with UnicodeEncodeError. capsys is UTF-8 and hid it; this pin uses cp1252."""
    import io, sys
    _fresh_item(repo, title="panel → store — a title with arrows")
    for name in ("stdout", "stderr"):
        monkeypatch.setattr(sys, name, io.TextIOWrapper(io.BytesIO(), encoding="cp1252"))
    assert act.main(["--root", str(repo), "list"]) == 0
    assert act.main(["--root", str(repo), "show", "rq-900"]) == 0
    assert act.main(["--root", str(repo), "--json", "list"]) == 0


def test_show_displays_a_field_example_that_is_not_text(repo, capsys):
    """Found by the WS-3 queue pin (2026-10-01): a field example that is a JSON boolean or number made `show` raise
    TypeError on the join, so the operator could not read the item at all."""
    art = repo / "spike" / "graph" / "l2" / "typed-examples.jsonld"
    rec = {"@id": "sr:L2:X", "@type": "SpecificationRecord", "title": "X", "assertions": [
        {"@id": "a:X", "statement": "X carries flag and seq.", "groundedBy": [],
         "fields": [{"name": "flag", "examples": [True]}, {"name": "seq", "examples": [7, "<n>"]}]}]}
    art.write_text(json.dumps({"records": [rec]}), encoding="utf-8")
    _add_item(repo, id="rq-901", batch="BX", queuedAt="2026-10-01T10:00:00-04:00", record="sr:L2:X",
              artifact="spike/graph/l2/typed-examples.jsonld", recordDigest=act.digest(rec), kind="L2")
    assert act.main(["--root", str(repo), "show", "rq-901"]) == 0
    out = " ".join(capsys.readouterr().out.split())
    assert "flag e.g. true" in out and "seq e.g. 7, <n>" in out


def test_show_discloses_a_superseded_item_and_a_stale_one(repo, capsys):
    """IA Ops finding 2026-10-01, bullet 3: a reader must not need to attempt an act to learn an item is dead or
    stale."""
    _fresh_item(repo, item_id="rq-900")
    _fresh_item(repo, item_id="rq-901", supersedes="rq-900")
    assert act.main(["--root", str(repo), "show", "rq-900"]) == 0
    assert "SUPERSEDED by rq-901" in capsys.readouterr().out
    _fresh_item(repo, item_id="rq-902", recordDigest="sha256:" + "0" * 64)
    assert act.main(["--root", str(repo), "show", "rq-902"]) == 0
    out = capsys.readouterr().out
    assert "STALE" in out and "SUPERSEDED" not in out
    assert act.main(["--root", str(repo), "show", "rq-901"]) == 0
    out = capsys.readouterr().out
    assert "STALE" not in out and "SUPERSEDED" not in out


def test_show_renders_the_decision_and_the_note_an_act_recorded(capsys):
    """IA Ops finding 2026-10-01, bullet 4: `show rq-035` printed neither the letter A nor its conditions."""
    assert act.main(["--root", str(ROOT), "show", "rq-035"]) == 0
    out = " ".join(capsys.readouterr().out.split())
    assert "decision: A" in out and "A with conditions" in out
    assert act.main(["--root", str(ROOT), "show", "rq-034"]) == 0
    assert "BLOCKING" in capsys.readouterr().out


def test_list_names_what_an_act_left_owed_until_it_is_requeued(repo, capsys):
    """IA Ops finding 2026-10-01, bullet 3: an amended row owes a re-queue and a diagnostic-opened row a resolution;
    `list` must not read '(no pending items)' as if the sitting left nothing behind."""
    _fresh_item(repo, item_id="rq-900", act="amended", actedAt="2026-10-01T15:00:00-04:00", actor="Aaron")
    assert act.main(["--root", str(repo), "list"]) == 0
    out = capsys.readouterr().out
    assert "owed" in out and "rq-900" in out and "amended" in out
    _fresh_item(repo, item_id="rq-901", supersedes="rq-900")
    assert act.main(["--root", str(repo), "list"]) == 0
    out = capsys.readouterr().out
    owed_part = out.split("owed --", 1)[1] if "owed --" in out else ""
    assert "rq-901" in out and "rq-900" not in owed_part, "a re-queued amend is no longer owed"


def test_show_prints_a_file_items_text_and_every_options_consequence(repo, capsys):
    """2026-10-17: a bar/oracle/hook IS its text, so `show` prints the file it binds to; and an adjudication's
    options show their consequence whichever key holds it (`consequence` in WS-3, `consequenceForTheSpike` in the
    slice) -- rq-038 was decided while the page showed none."""
    import hashlib
    f = repo / "spike" / "x.test.mjs"
    f.write_text("import test from 'node:test';\ntest('a seeded bar', () => {});\n", encoding="utf-8")
    _add_item(repo, id="rq-910", batch="BX", queuedAt="2026-10-17T00:00:00-04:00", kind="bar", artifact="spike/x.test.mjs",
              artifactFileDigest="sha256:" + hashlib.sha256(f.read_bytes()).hexdigest())
    assert act.main(["--root", str(repo), "show", "rq-910"]) == 0
    assert "| test('a seeded bar', () => {});" in capsys.readouterr().out
    art = repo / "spike" / "adj.jsonld"
    adj = {"@id": "adj:x", "@type": "Adjudication", "conflict": "diag:x",
           "options": [{"id": "A", "label": "one", "consequence": "the WS-3 key"},
                       {"id": "B", "label": "two", "consequenceForTheSpike": "the slice key"}]}
    art.write_text(json.dumps({"adjudications": [adj]}), encoding="utf-8")
    _add_item(repo, id="rq-911", batch="BX", queuedAt="2026-10-17T00:00:00-04:00", kind="Adjudication", record="adj:x",
              artifact="spike/adj.jsonld", recordDigest=act.digest(adj), options=["A: one", "B: two"])
    assert act.main(["--root", str(repo), "show", "rq-911"]) == 0
    out = capsys.readouterr().out
    assert "the WS-3 key" in out and "the slice key" in out


def test_show_prints_every_field_of_an_adjudication_not_a_whitelist(repo, capsys):
    """2026-10-17: `show` printed an adjudication's fields from a whitelist (conflict, theSourceSays, thePlanSays), so
    rq-035 was decided with theFactorySays -- one side of its own conflict -- never printed. Every field is shown
    unless it is one of the named structural keys; a field nobody has thought of yet is shown by default."""
    art = repo / "spike" / "adj2.jsonld"
    adj = {"@id": "adj:y", "@type": "Adjudication", "notACandidate": True, "conflict": "diag:y",
           "theFactorySays": {"value": "FACTORY-SIDE-ZQ"}, "precedents": ["PRECEDENT-ZQ"],
           "aFieldNobodyNamedYet": "UNNAMED-ZQ", "decision": None,
           "options": [{"id": "A", "label": "one", "consequence": "c", "files": {"m": "OPTION-FILE-ZQ.ts"}}]}
    art.write_text(json.dumps({"adjudications": [adj]}), encoding="utf-8")
    _add_item(repo, id="rq-912", batch="BX", queuedAt="2026-10-17T00:00:00-04:00", kind="Adjudication", record="adj:y",
              artifact="spike/adj2.jsonld", recordDigest=act.digest(adj), options=["A: one"])
    assert act.main(["--root", str(repo), "show", "rq-912"]) == 0
    out = capsys.readouterr().out
    for shown in ("theFactorySays:", "FACTORY-SIDE-ZQ", "precedents:", "PRECEDENT-ZQ", "aFieldNobodyNamedYet:", "UNNAMED-ZQ",
                  "files:", "OPTION-FILE-ZQ.ts"):     # an option's own extra keys too (the files a decision fixes)
        assert shown in out, shown
    for hidden in ("notACandidate:", "@type:", "decision:"):
        assert hidden not in out, hidden


# Acted before act.py recorded `actDigest` (2026-09-11, the operator's own hand): the row's artifactFileDigest is the
# only binding, and it is still checked against the file's current bytes above. Any OTHER acted row lacking it is red.
ACTED_BEFORE_ACT_DIGEST = {"rq-001"}


def test_every_live_file_item_is_bound_to_its_files_current_bytes():
    """The digest-agreement pin covers record-addressed rows; this one covers file-addressed rows (bars, oracles,
    hooks, rules). Counted, never vacuous -- and INDEPENDENT of whether a row is acted (IA Ops finding 2026-10-17, "the
    file-binding gate counts unacted rows and goes red when WS3-5 is ratified"): it used to examine unacted rows only,
    so ratifying WS3-5 would have emptied its subject. An ACTED row is the more important case: the file must still be
    the bytes the act bound, or the ratification no longer describes what is in the tree."""
    q = act.Queue(ROOT)
    dead = q.superseded()
    live = [r for _, r in q.rows if r.get("artifactFileDigest") and r["id"] not in dead]
    for r in live:
        assert q.current_digest(r)[1] == r["artifactFileDigest"], r["id"]
        if r.get("actedAt") and r["id"] not in ACTED_BEFORE_ACT_DIGEST:
            assert r.get("actDigest") == r["artifactFileDigest"], "%s: the act bound other bytes" % r["id"]
    assert len(live) >= 8, "examined %d live file rows (rq-001, rq-013 and WS3-5's six), acted or not" % len(live)


def test_the_file_binding_gate_survives_a_drained_queue(repo):
    """Ops' acceptance bullet 2, seeded: with every pending file row marked acted, the same rule still examines them
    all and still catches a file edited after its act."""
    import hashlib
    f = repo / "spike" / "bar.test.mjs"
    f.write_text("export const bar = 1;\n", encoding="utf-8")
    d = "sha256:" + hashlib.sha256(f.read_bytes()).hexdigest()
    _add_item(repo, id="rq-920", batch="BX", queuedAt="2026-10-17T00:00:00-04:00", kind="bar", artifact="spike/bar.test.mjs",
              artifactFileDigest=d, actedAt="2026-10-17T01:00:00-04:00", act="ratified", actor="Seeded", actDigest=d)
    q = act.Queue(repo)
    rows = [r for _, r in q.rows if r.get("artifactFileDigest") and r["id"] not in q.superseded()]
    assert [r["id"] for r in rows if r.get("actedAt")] and all(q.current_digest(r)[1] == r["artifactFileDigest"] for r in rows)
    f.write_text("export const bar = 2;   // edited after the act\n", encoding="utf-8")
    assert q.current_digest(next(r for r in rows if r["id"] == "rq-920"))[1] != d


def test_show_puts_each_statement_above_the_passages_it_cites(repo, capsys):
    """Found by the operator's dry run (2026-09-29): `show` printed the cited passages but not the statements
    being accepted, while the item's own instruction is 'review every cited span beside its assertion'."""
    assert act.main(["--root", str(repo), "show", "rq-004"]) == 0
    out = capsys.readouterr().out
    first, second = "Finding is an event record and is append-only.", "A Finding record carries the fields id"
    assert first in out and second in " ".join(out.split())
    assert out.index("Finding is an event record") < out.index("[line 85, primary]") < out.index("A Finding record")
    assert out.count("[line 85, primary]") == 1, "a wrapped passage names its source once"


def test_show_lays_out_an_adjudication_s_options_and_consequences(repo, capsys):
    assert act.main(["--root", str(repo), "show", "rq-011"]) == 0
    out = capsys.readouterr().out
    for opt in ("A  Honor the source", "B  Source-amendment request", "C  Relocating closure"):
        assert opt in out
    assert "consequence:" in out and "theSourceSays" in out


def test_show_marks_design_rationale_as_not_grounding(repo, capsys):
    assert act.main(["--root", str(repo), "show", "rq-008"]) == 0
    assert "rationale (not grounding):" in capsys.readouterr().out


def test_show_json_keeps_the_raw_row(repo, capsys):
    assert act.main(["--root", str(repo), "--json", "show", "rq-004"]) == 0
    assert json.loads(capsys.readouterr().out)["item"]["record"] == "sr:L2:Finding"
