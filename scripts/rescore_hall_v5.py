# -*- coding: utf-8 -*-
"""Secondary analysis (re-scoring only): hallucination definition v5 = v4 minus labels grounded in
the manual sections of the scenario's workflow. Definition fixed in data/eval/study2/hall_v5_definition.md
BEFORE this script is run. The production scorer is untouched; result files are not modified.

Usage: CHROMADB_PATH=./data/chromadb_v4 .venv/Scripts/python.exe scripts/rescore_hall_v5.py
Writes data/eval/results/hall_v5_rescore.md
"""
from __future__ import annotations
import glob, json, os, re, statistics, sys
from collections import defaultdict, Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
os.environ.setdefault("CHROMADB_PATH", "./data/chromadb_v4"); os.environ["GEOLENS_SCORER"] = "v4"
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from api.services import evaluation as ev  # noqa: E402
from stats_stratified import perm_p  # noqa: E402
import chromadb  # noqa: E402

MODELS = ["gemini", "claude", "gpt"]
SETS = [("study2", "Study 2 test set", "data/eval/scenarios/.study2_test"),
        ("v3_qgis", "v3 QGIS test set", "data/eval/scenarios"),
        ("v3", "v3 OpendTect dev set", "data/eval/scenarios")]
WF_OF = {"opendtect__survey_setup__01": "survey_setup", "opendtect__3d_visualization__01": "d3_visualization",
         "opendtect__attribute_computation__01": "seismic_attribute", "opendtect__fault_sticks__01": "fault_sticks_143b",
         "opendtect__horizon_autotrack__01": "horizon_autotrack_142a", "qgis__vector_buffer__01": "qgis_vector_buffer"}
canon = lambda s: re.sub(r"[^a-z0-9]+", "", (s or "").lower())
tokens = lambda s: set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def workflow_sections(wf_id):
    for f in glob.glob("data/workflows/*.json") + glob.glob("data/workflows/excluded_study2/*.json"):
        wf = json.load(open(f, encoding="utf-8"))
        if wf.get("workflow_id") == wf_id:
            return sorted({s for n in wf["nodes"] for s in (n.get("manual_sections") or [])})
    return []


_client = chromadb.PersistentClient(path=os.environ["CHROMADB_PATH"])
_manual_cache = {}


def section_text(manual_id, sections):
    key = (manual_id, tuple(sections))
    if key in _manual_cache:
        return _manual_cache[key]
    col = _client.get_collection("manual_" + manual_id)
    got = col.get(include=["documents", "metadatas"])
    parts = []
    for d, m in zip(got["documents"], got["metadatas"]):
        sec = str(m.get("section", ""))
        if any(sec.startswith(s) for s in sections):
            parts.append(re.sub(r"^\[Section:.*?\]\n", "", d, flags=re.S))
    txt = " ".join(parts)
    _manual_cache[key] = (canon(txt), tokens(txt), len(parts))
    return _manual_cache[key]


def grounded(label, ctext, ctok):
    for part in re.split(r"[/+,]", label):
        c = canon(part)
        if not c:
            continue
        if len(c) >= 3:
            if c not in ctext:
                return False
        elif c not in ctok:
            return False
    return True


def main():
    L = ["# 환각 정의 v5 재채점 (2차 분석; 정의 = data/eval/study2/hall_v5_definition.md; 재실행 없음, 원본 불변)", ""]
    excluded = Counter(); remaining = Counter()
    summary = {}
    for tag, label, sdir in SETS:
        scen = {}
        for f in glob.glob(os.path.join(sdir, "*.json")):
            d = json.load(open(f, encoding="utf-8"))
            if d.get("scenario_id") in WF_OF:
                scen[d["scenario_id"]] = d
        per = defaultdict(lambda: defaultdict(list))  # (model, backend) -> {"v4": [rep rates], "v5": [...]}
        for f in sorted(glob.glob(f"data/eval/results/run_*_{tag}_r*_*.json")):
            m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
            if not m or m.group(1) not in MODELS:
                continue
            model = m.group(1); run = json.load(open(f, encoding="utf-8"))
            for sc in run["scenarios"]:
                sid = sc["scenario_id"]; st = scen[sid]
                secs = workflow_sections(WF_OF[sid]); ctext, ctok, nchunks = section_text(st["manual_id"], secs)
                for b, bd in sc["backends"].items():
                    h4 = h5 = 0; n = len(bd["per_step"])
                    for ps in bd["per_step"]:
                        gt = st["steps"][ps["step_index"]]
                        labs = ev.hallucinated_elements(ps["response"], gt["visual_state_gt"]["visible_elements"], step_gt=gt, goal=st["goal"])
                        h4 += bool(labs)
                        keep = [l for l in labs if not grounded(l, ctext, ctok)]
                        for l in labs:
                            (remaining if l in keep else excluded)[(tag, l)] += 1
                        h5 += bool(keep)
                    per[(model, b)]["v4"].append(h4 / n); per[(model, b)]["v5"].append(h5 / n)
        L += [f"## {label} (tag {tag})", "", "| model | backend | hall v4 | hall v5 | Δ |", "|---|---|---|---|---|"]
        for model in MODELS:
            for b in ("no_rag", "vanilla_budget", "vanilla_vector", "full_system", "graph_only", "vision_only", "state_path"):
                if (model, b) in per:
                    a4, a5 = statistics.mean(per[(model, b)]["v4"]), statistics.mean(per[(model, b)]["v5"])
                    L.append(f"| {model} | {b} | {a4:.3f} | {a5:.3f} | {a5 - a4:+.3f} |")
        summary[tag] = per
        L.append("")
    # study 2 secondary grades
    per = summary["study2"]
    L += ["## Study 2 — hall 조건을 v5로 재평가한 2차 분석 등급 (step accuracy 조건은 서명된 판정 그대로: 비교 1 성립, 비교 2 불성립)", ""]
    for comp, step_ok, signed in (("vanilla_budget", True, "A′"), ("vanilla_vector", False, "B")):
        rows = []
        for model in MODELS:
            a, c = statistics.mean(per[(model, "full_system")]["v5"]), statistics.mean(per[(model, comp)]["v5"])
            _, p = perm_p(per[(model, "full_system")]["v5"], per[(model, comp)]["v5"])
            rows.append((model, a, c, a <= c, p))
        ok = sum(1 for r in rows if r[3]); hall_ok = ok >= 2
        grade = ("A" if hall_ok else "A′") if step_ok else "B"
        L.append(f"- full_system vs {comp}: " + "; ".join(f"{r[0]} {r[1]:.3f} vs {r[2]:.3f} ({'✓' if r[3] else '✗'}, p {r[4]:.3f})" for r in rows) + f" → hall 조건 {ok}/3 {'성립' if hall_ok else '불성립'} → **2차 분석 등급 {grade}** (서명된 등급 {signed})")
    L += ["", "## v5에서 제외된 라벨(매뉴얼 절에 있음) 상위", ""]
    for (tag, l), v in excluded.most_common(25):
        L.append(f"- {tag}: {l!r} × {v}")
    L += ["", "## v5에서 남은 라벨(화면에도 매뉴얼 절에도 없음) 상위", ""]
    for (tag, l), v in remaining.most_common(25):
        L.append(f"- {tag}: {l!r} × {v}")
    md = "\n".join(L) + "\n"
    Path("data/eval/results/hall_v5_rescore.md").write_text(md, encoding="utf-8"); print(md)


if __name__ == "__main__":
    main()
