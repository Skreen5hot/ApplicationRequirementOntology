"""The sitting page is the act tool with buttons: every act goes through act.act(), so its rules hold unchanged.
Driven over real HTTP against a COPY of the spike tree -- the live queue is never touched."""
import json
import shutil
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from conftest import load_tool

ROOT = Path(__file__).resolve().parents[1]
ui = load_tool("aro_act_ui", "tools/act_ui.py")


@pytest.fixture()
def site(tmp_path):
    shutil.copytree(ROOT / "spike", tmp_path / "spike", ignore=shutil.ignore_patterns("__pycache__", "out"))
    ui.STATE.update(root=str(tmp_path), actor="Aaron", sitting="2026-10-17T19:00:00-04:00", flash="")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), ui.Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield "http://127.0.0.1:%d" % srv.server_address[1], tmp_path
    srv.shutdown()


def _get(url):
    with urllib.request.urlopen(url) as r:
        return r.read().decode("utf-8")


def _post(url, **fields):
    data = urllib.parse.urlencode(fields).encode("utf-8")
    with urllib.request.urlopen(urllib.request.Request(url, data=data)) as r:   # follows the 303
        return r.read().decode("utf-8")


def _row(root, item_id):
    for line in (root / "spike" / "measurements" / "ratification-queue.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip() and json.loads(line)["id"] == item_id:
            return json.loads(line)


def _first_pending(root, adjudication):
    q = ui.A.Queue(root)
    return next(r["id"] for r in q.pending() if bool(r.get("options")) == adjudication)


def test_the_list_and_an_item_render_what_act_show_prints(site):
    base, root = site
    assert "Pending" in _get(base + "/")
    item = _first_pending(root, adjudication=False)
    page = _get(base + "/item/" + item)
    shown = ui.A.render_show(ui.A.Queue(root), _row(root, item))
    first_statement = shown.splitlines()[0]
    assert ui.html.escape(first_statement) in page
    assert "Ratify" in page and "Amend" in page


def test_a_ratify_through_the_page_is_recorded_by_act_exactly_as_the_cli_would(site):
    base, root = site
    item = _first_pending(root, adjudication=False)
    before = _row(root, item)
    _post(base + "/act/" + item, verb="ratify", note="")
    after = _row(root, item)
    assert after["act"] == "ratified" and after["actor"] == "Aaron"
    assert after["actDigest"] == before["recordDigest"] and after["sittingStart"] == "2026-10-17T19:00:00-04:00"


def test_an_amend_without_a_note_records_nothing(site):
    base, root = site
    item = _first_pending(root, adjudication=False)
    page = _post(base + "/act/" + item, verb="amend", note="")
    assert "needs a note" in page and not _row(root, item).get("actedAt")


def test_a_decide_records_the_letter_and_an_agent_actor_is_refused(site):
    base, root = site
    q = root / "spike" / "measurements" / "ratification-queue.jsonl"
    src = _row(root, "rq-038")      # a real adjudication, re-queued unacted in the COPY so a decide can be exercised
    fresh = {k: v for k, v in src.items() if k not in ("actedAt", "act", "actor", "actDigest", "decision", "actNote", "sittingStart")}
    fresh.update(id="rq-990", queuedAt="2026-10-17T00:00:00-04:00")
    q.write_text(q.read_text(encoding="utf-8") + json.dumps(fresh, ensure_ascii=False) + chr(10), encoding="utf-8")
    item = "rq-990"
    ui.STATE["actor"] = "claude"
    page = _post(base + "/act/" + item, decision="C", note="")
    assert "REFUSED" in page and not _row(root, item).get("actedAt")
    ui.STATE["actor"] = "Aaron"
    _post(base + "/act/" + item, decision="C", note="narrow reading")
    row = _row(root, item)
    assert row["act"] == "decided" and row["decision"] == "C" and row["actNote"] == "narrow reading"


def test_the_page_never_writes_the_queue_itself():
    """The one door: the only write path is act.act()."""
    src = (ROOT / "tools" / "act_ui.py").read_text(encoding="utf-8")
    assert "A.act(" in src and "write_row" not in src and "ratification-queue" not in src
