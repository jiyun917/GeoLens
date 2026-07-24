"""Confidence distribution reporter for the paper appendix.

The user's judgment call was explicit: if fallback activation rate stays at
0% across all 4 models, we do NOT lower the threshold to force firings.
Instead we document the confidence distribution — min, max, quartiles —
to show that P1 had no *room* to activate on this dataset, i.e., that its
threshold (0.7) was above the observed maximum confidence-below-70 range
never actually happened.

This exists so the paper appendix can show 'confidence distribution across
all routed steps' and the reader can verify that the fallback threshold
0.7 was above the observed minimum by a real margin.

Usage:
    .venv/Scripts/python.exe scripts/confidence_distribution.py --tag unified2
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def load_confidences(tag: str) -> dict:
    """(model, backend) -> [confidence_value_per_routed_step, ...]"""
    out: dict = defaultdict(list)
    for f in sorted(glob.glob(str(ROOT / f"data/eval/results/run_*_{tag}_r*_*.json"))):
        m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", Path(f).name)
        if not m:
            continue
        model = m.group(1)
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        for scen in d.get("scenarios", []) or []:
            for bname, b in (scen.get("backends") or {}).items():
                if not b or "error" in b:
                    continue
                for ps in b.get("per_step") or []:
                    if not ps.get("route_method"):
                        continue
                    conf = ps.get("route_confidence")
                    if conf is not None:
                        out[(model, bname)].append(float(conf))
    return out


def summarize(vals: list) -> dict:
    if not vals:
        return {"n": 0}
    s = sorted(vals)
    n = len(s)
    def _q(p):
        return s[max(0, min(n - 1, int(p * n)))]
    return {
        "n":    n,
        "min":  min(s),
        "q25":  _q(0.25),
        "median": _q(0.5),
        "q75":  _q(0.75),
        "max":  max(s),
        "mean": statistics.fmean(s),
        "below_0.7": sum(1 for x in s if x < 0.7),
    }


def report(data: dict) -> str:
    THRESHOLD = 0.7
    lines = []
    lines.append("# Route-confidence distribution — v2 unified matrix\n")
    lines.append(f"Fallback threshold = **{THRESHOLD}**. Any routed step with "
                 f"confidence < {THRESHOLD} triggers vector-only fallback.\n")
    lines.append("| model | backend | n | min | Q25 | median | Q75 | max | mean | n below 0.7 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    total_all = 0
    total_below = 0
    for (mdl, bkn), vals in sorted(data.items()):
        s = summarize(vals)
        total_all += s["n"]
        total_below += s.get("below_0.7", 0)
        if s["n"] == 0:
            continue
        lines.append(
            f"| {mdl} | {bkn} | {s['n']} | "
            f"{s['min']:.2f} | {s['q25']:.2f} | {s['median']:.2f} | "
            f"{s['q75']:.2f} | {s['max']:.2f} | {s['mean']:.2f} | "
            f"{s['below_0.7']} |"
        )

    lines.append(f"\n**Total routed steps**: {total_all}")
    lines.append(f"**Steps below threshold 0.7**: {total_below} "
                 f"({100*total_below/max(total_all,1):.1f}%)")

    if total_below == 0:
        lines.append("\n## Interpretation for the paper\n")
        lines.append(f"The confidence gate at threshold {THRESHOLD} did not "
                     f"activate on any of the {total_all} routed steps across "
                     "the entire v2 matrix. The observed minimum confidence "
                     f"across all (model, backend) cells was above {THRESHOLD}, "
                     "so the fallback branch of the pipeline was dead code on "
                     "this dataset. This does not mean the branch is "
                     "gratuitous — the ground-truth dry-run (with hand-authored "
                     "visual_state) produced confidences as low as 0.60, so "
                     "the safety net exists for cases where Gemini's real-time "
                     "vision extraction is less certain than the authored "
                     "ground truth. On the two scenarios in this benchmark, "
                     "no such uncertainty occurred.")

    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="unified2")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    data = load_confidences(args.tag)
    if not data:
        print(f"no confidence data for tag={args.tag}")
        return
    md = report(data)
    print(md)
    out = ROOT / "data" / "eval" / "results" / (args.out or f"confidence_dist_{args.tag}.md")
    out.write_text(md, encoding="utf-8")
    print(f"\nsaved: {out}")


if __name__ == "__main__":
    main()
