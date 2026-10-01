"""WS-3 (Plan v1.1 s5): the capability-grain L2 graph for the A9 target is reproducible, fully grounded, inside the
named region, and queued for 100% span review without disturbing the ratified slice."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS3 = ROOT / "spike" / "graph" / "ws3"
GRAPH = ROOT / "spike" / "graph" / "l2" / "srs-ws3.graph.jsonld"
QUEUE = ROOT / "spike" / "measurements" / "ratification-queue.jsonl"
DIGEST = "sha256:2428b115bafe685044b88f97ac11f6ba28e1179c45989ee1b596b72ae3c89450"


def _run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True)


def _graph():
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def _fragments():
    return json.loads((WS3 / "fragments.json").read_text(encoding="utf-8"))["fragments"]


def test_the_graph_on_disk_is_exactly_what_the_builder_produces():
    r = _run("spike/graph/ws3/build_l2.py", "--check")
    assert r.returncode == 0, r.stderr


def test_every_citation_resolves_to_a_fragment_minted_from_the_registered_digest():
    frags = {f["fragmentId"]: f for f in _fragments()}
    assert all(f["source"]["digest"] == DIGEST for f in frags.values())
    g = _graph()
    cited = [c["fragment"] for r in g["records"] for a in r["assertions"] for c in a["groundedBy"]]
    cited += [e for d in g["diagnostics"] for e in d["evidence"]]
    assert cited and all(c in frags for c in cited)


def test_every_assertion_is_grounded_by_a_primary_span():
    for r in _graph()["records"]:
        for a in r["assertions"]:
            assert any(c["role"] == "primary" for c in a["groundedBy"]), a["@id"]


def test_the_capabilities_are_exactly_the_A9_target():
    g = _graph()
    caps = sorted(a["target"]["name"] for r in g["records"] for a in r["assertions"]
                  if a.get("target", {}).get("kind") == "capability")
    assert caps == ["C-S2", "C-S3", "C-S7"] == g["ws3"]["target"]["capabilities"]
    assert g["ws3"]["demonstrationControlCandidate"]["capability"] == "C-S2"


def test_every_capability_primary_span_lies_inside_the_named_region():
    region = set(range(43, 54)) | set(range(73, 77))   # A9: lines 43-53 and 73-75; 76 is C-S7's own determinism note
    by_id = {f["fragmentId"]: f for f in _fragments()}
    for r in _graph()["records"]:
        if r["@id"] in ("sr:L2:C-S2", "sr:L2:C-S3", "sr:L2:C-S7"):
            for a in r["assertions"]:
                for c in a["groundedBy"]:
                    if c["role"] == "primary":
                        assert int(by_id[c["fragment"]]["display"]["lines"]) in region, (a["@id"], c["label"])


def test_every_WS3_record_is_queued_once_and_bound_to_its_current_bytes():
    rows = [json.loads(l) for l in QUEUE.read_text(encoding="utf-8").splitlines() if l.strip()]
    ws3 = [r for r in rows if r.get("artifact") == "spike/graph/l2/srs-ws3.graph.jsonld"]
    recs = [r["@id"] for r in _graph()["records"]]
    assert sorted(r["record"] for r in ws3) == sorted(recs)
    for row in ws3:
        assert _run("tools/act.py", "show", row["id"]).returncode == 0, row["id"]


def test_the_ratified_slice_projection_is_untouched():
    r = _run("spike/projections/project.py", "--check")
    assert r.returncode == 0 and "byte-identical" in r.stdout, r.stdout + r.stderr
