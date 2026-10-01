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
    for _, row in q.rows:
        if row.get("recordDigest"):
            rec = act._find(json.loads((ROOT / row["artifact"]).read_text(encoding="utf-8")), row["record"])
            assert act.digest(rec) == layout_rule.digest(rec) == row["recordDigest"], row["id"]
            checked += 1
    assert checked >= 9


def test_list_is_read_only_and_excludes_acted_and_superseded(repo):
    before = (repo / act.QUEUE_REL).read_bytes()
    ids = [r["id"] for r in act.Queue(repo).pending()]
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
    assert "consequence:" in out and "theSourceSays:" in out


def test_show_marks_design_rationale_as_not_grounding(repo, capsys):
    assert act.main(["--root", str(repo), "show", "rq-008"]) == 0
    assert "rationale (not grounding):" in capsys.readouterr().out


def test_show_json_keeps_the_raw_row(repo, capsys):
    assert act.main(["--root", str(repo), "--json", "show", "rq-004"]) == 0
    assert json.loads(capsys.readouterr().out)["item"]["record"] == "sr:L2:Finding"
