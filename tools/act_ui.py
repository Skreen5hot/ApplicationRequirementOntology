# SPDX-License-Identifier: Apache-2.0
"""A local page for ratification sittings -- the act tool with buttons.

    python tools/act_ui.py              # then open http://127.0.0.1:8766
    python tools/act_ui.py --port 9000

The same pattern as IntegratedAgent's tools/chat_ui.py (stdlib http.server, 127.0.0.1 only), but it drives the
RATIFICATION QUEUE, not a build. Every button calls `tools/act.py`'s own `act()` -- the one door -- so the content
address binding, the named-human rule, the superseded/already-acted/changed-since-queued refusals and the
decide-needs-an-option rule are enforced exactly as on the command line. This page adds no rule and skips none.

Each item is shown with act.py's own `render_show` text (statements with their source passages beneath them), so
what you read here is what `act.py show` prints. The sitting start is stamped when the page starts and is editable.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
import act as A  # noqa: E402  -- the one door

STATE = {"root": A.ROOT_DEFAULT, "actor": "Aaron",
         "sitting": dt.datetime.now().astimezone().replace(microsecond=0).isoformat(), "flash": ""}

CSS = """
:root{--bg:#fafaf9;--fg:#1c1917;--mut:#57534e;--line:#e7e5e4;--card:#fff;--acc:#1d4ed8;--ok:#15803d;--bad:#b91c1c}
@media (prefers-color-scheme: dark){:root{--bg:#1c1917;--fg:#f5f5f4;--mut:#a8a29e;--line:#44403c;--card:#292524;--acc:#93c5fd;--ok:#86efac;--bad:#fca5a5}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:16px}
a{color:var(--acc)} h1{font-size:20px;margin:8px 0 4px} h2{font-size:16px;margin:20px 0 8px}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px;margin:10px 0}
.row{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.id{font-family:ui-monospace,monospace;font-weight:600} .mut{color:var(--mut);font-size:13px}
pre{white-space:pre-wrap;word-wrap:break-word;font:13px/1.45 ui-monospace,Consolas,monospace;margin:0}
textarea{width:100%;min-height:70px;font:14px system-ui;box-sizing:border-box}
input[type=text]{font:14px system-ui;padding:3px 6px}
button{font:14px system-ui;padding:6px 14px;margin:4px 6px 4px 0;border-radius:6px;border:1px solid var(--line);
  background:var(--card);color:var(--fg);cursor:pointer} button.go{border-color:var(--ok);color:var(--ok)}
button.am{border-color:var(--bad);color:var(--bad)}
.flash{padding:8px 12px;border-radius:6px;border:1px solid var(--line)} .flash.ok{border-color:var(--ok)}
.flash.bad{border-color:var(--bad)}
"""


def _page(title, body):
    return ("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,"
            "initial-scale=1'><title>%s</title><style>%s</style></head><body><main>%s</main></body></html>"
            % (html.escape(title), CSS, body)).encode("utf-8")


def _flash():
    f, STATE["flash"] = STATE["flash"], ""
    if not f:
        return ""
    kind, text = f
    return "<p class='flash %s'>%s</p>" % (kind, html.escape(text))


def _header():
    return ("<h1>Ratification sitting</h1><form method='post' action='/settings' class='row mut'>"
            "Actor <input type='text' name='actor' value='%s' size='10'> Sitting start "
            "<input type='text' name='sitting' value='%s' size='26'> <button>Save</button>"
            "<a href='/'>all items</a></form>" % (html.escape(STATE["actor"]), html.escape(STATE["sitting"])))


def list_page():
    q = A.Queue(Path(STATE["root"]))
    pend = q.pending()
    cards = "".join(
        "<div class='card row'><a class='id' href='/item/%s'>%s</a><span class='mut'>%s</span><span>%s</span></div>"
        % (html.escape(r["id"]), html.escape(r["id"]), html.escape(r.get("batch") or ""),
           html.escape(r.get("title") or r.get("kind") or "")) for r in pend) or "<p>No pending items.</p>"
    owed = q.owed()
    owed_html = ("<h2>Owed -- acted, but the act left work to do</h2>" + "".join(
        "<div class='card row'><span class='id'>%s</span><span class='mut'>%s</span><span>%s</span></div>"
        % (html.escape(r["id"]), html.escape(r.get("act") or ""), html.escape(r.get("title") or ""))
        for r in owed)) if owed else ""
    return _page("Ratification sitting", _header() + _flash() + "<h2>Pending (%d), in order</h2>" % len(pend)
                 + cards + owed_html)


def item_page(item_id):
    q = A.Queue(Path(STATE["root"]))
    _, row = q.get(item_id)
    shown = A.render_show(q, row)
    opts = [str(o) for o in row.get("options") or []]
    acted = bool(row.get("actedAt")) or item_id in q.superseded()
    if acted:
        form = "<p class='mut'>This item cannot be acted on (see the end of the text above).</p>"
    elif opts:
        form = ("<form method='post' action='/act/%s'><p>Decide -- one of:</p>%s"
                "<p class='mut'>Note (optional, recorded verbatim):</p><textarea name='note'></textarea></form>"
                % (html.escape(item_id), "".join(
                    "<button class='go' name='decision' value='%s'>%s</button><br>"
                    % (html.escape(o.split(":", 1)[0].strip()), html.escape(o)) for o in opts)))
    else:
        form = ("<form method='post' action='/act/%s'><p class='mut'>Note (optional for ratify / accept; REQUIRED "
                "for amend and diagnostic -- say what to change or what to look into; recorded verbatim):</p>"
                "<textarea name='note'></textarea><br>"
                "<button class='go' name='verb' value='ratify'>Ratify</button>"
                "<button class='go' name='verb' value='accept'>Accept</button>"
                "<button class='am' name='verb' value='amend'>Amend</button>"
                "<button class='am' name='verb' value='diagnostic'>Open diagnostic</button></form>"
                % html.escape(item_id))
    pend = [r["id"] for r in q.pending()]
    nxt = pend[(pend.index(item_id) + 1)] if item_id in pend and pend.index(item_id) + 1 < len(pend) else None
    nav = "<p class='mut'><a href='/'>all items</a>%s</p>" % (
        " · <a href='/item/%s'>next: %s</a>" % (html.escape(nxt), html.escape(nxt)) if nxt else "")
    return _page(item_id, _header() + _flash() + nav + "<div class='card'><pre>%s</pre></div>" % html.escape(shown)
                 + "<div class='card'>%s</div>" % form)


def do_act(item_id, fields):
    """One act through act.act(); returns (ok, message). The page never writes the queue itself."""
    note = (fields.get("note") or [""])[0].strip() or None
    decision = (fields.get("decision") or [None])[0]
    verb = "decide" if decision else (fields.get("verb") or [""])[0]
    if verb in ("amend", "diagnostic") and not note:
        return False, "%s needs a note saying what to change or look into -- nothing was recorded" % verb
    try:
        q = A.Queue(Path(STATE["root"]))
        out = A.act(q, item_id, verb, STATE["actor"], decision, STATE["sitting"] or None, note)
    except (A.Refused, A.Usage) as e:
        return False, "REFUSED: %s" % e
    return True, "%s %s by %s at %s%s" % (out["id"], out["act"], out["actor"], out["actedAt"],
                                          (" -- decision %s" % out["decision"]) if out.get("decision") else "")


class Handler(BaseHTTPRequestHandler):
    def _send(self, body, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, to):
        self.send_response(303)
        self.send_header("Location", to)
        self.end_headers()

    def log_message(self, *args):
        pass

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/":
                return self._send(list_page())
            if path.startswith("/item/"):
                return self._send(item_page(path[len("/item/"):]))
        except (A.Refused, A.Usage) as e:
            return self._send(_page("error", "<p>%s</p><a href='/'>back</a>" % html.escape(str(e))), 404)
        self._send(_page("not found", "<a href='/'>back</a>"), 404)

    def do_POST(self):
        path = urlparse(self.path).path
        n = int(self.headers.get("Content-Length") or 0)
        fields = parse_qs(self.rfile.read(n).decode("utf-8"), keep_blank_values=True)
        if path == "/settings":
            STATE["actor"] = (fields.get("actor") or [""])[0].strip()
            STATE["sitting"] = (fields.get("sitting") or [""])[0].strip()
            STATE["flash"] = ("ok", "saved")
            return self._redirect("/")
        if path.startswith("/act/"):
            item_id = path[len("/act/"):]
            ok, msg = do_act(item_id, fields)
            STATE["flash"] = ("ok" if ok else "bad", msg)
            if ok:
                pend = [r["id"] for r in A.Queue(Path(STATE["root"])).pending()]
                return self._redirect("/item/%s" % pend[0] if pend else "/")
            return self._redirect("/item/%s" % item_id)
        self._send(_page("not found", "<a href='/'>back</a>"), 404)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8766)
    ap.add_argument("--root", default=str(A.ROOT_DEFAULT))
    ap.add_argument("--actor", default="Aaron")
    args = ap.parse_args(argv)
    STATE.update(root=args.root, actor=args.actor)
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("ratification sitting at http://127.0.0.1:%d  (sitting start %s; Ctrl+C to stop)" % (args.port, STATE["sitting"]))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
