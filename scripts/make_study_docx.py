# -*- coding: utf-8 -*-
"""Build a Word (.docx) record of a study: the GeoLens implementation (mechanism) and the test results, from the
verdict markdown, the result JSONs and the pre-registration. No paper framing - facts and tables.
Usage: .venv/Scripts/python.exe scripts/make_study_docx.py --study 4 --out "C:/Users/user/Downloads/STUDY-대체.docx"
       .venv/Scripts/python.exe scripts/make_study_docx.py --study 5 --out "C:/Users/user/Downloads/STUDY-신규세트.docx"
"""
from __future__ import annotations
import argparse, glob, json, os, re, statistics, sys
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

MODELS = ["gemini", "claude", "gpt"]; BACKENDS = ["no_rag", "vanilla_budget", "vanilla_vector", "full_system"]
BACKEND_KO = {"no_rag": "no_rag (RAG 없음)", "vanilla_budget": "vanilla_budget (고정 예산 벡터 RAG)", "vanilla_vector": "vanilla_vector (무절단 벡터 RAG)", "full_system": "full_system (GeoLens)"}
CFG = {
    4: dict(tags=["study4_opendtect", "study4_qgis"], verdict="data/eval/results/verdict_study4.md", prereg="data/eval/study4/study4_pre_registration_DRAFT.md",
            scen_dirs=["data/eval/scenarios/.study4_test_opendtect", "data/eval/scenarios/.study4_test_qgis"],
            title="GeoLens 평가 — Study 4 (최종 메커니즘의 개발 세트 재평가, 5 시나리오 × 10회)",
            nature="이 실행의 판정 세트는 이전 연구(study 2·3)에서 결과를 본 시나리오이며, 최종 메커니즘은 그 실패를 진단해 설계·검증했다. 따라서 이 결과는 '최종 메커니즘이 이 5개 과제에서 내는 성능'이고 새 과제로의 일반화 근거가 아니다(사전등록 4 §7)."),
    5: dict(tags=["study5_opendtect", "study5_qgis"], verdict="data/eval/results/verdict_study5.md", prereg="data/eval/study4/study5_pre_registration_DRAFT.md",
            scen_dirs=["data/eval/scenarios/.study5_test_opendtect", "data/eval/scenarios/.study5_test_qgis"],
            title="GeoLens 평가 — Study 5 (새 캡처 세트 E/F/G 확인 연구, 3 시나리오 × 10회)",
            nature="이 실행의 판정 세트는 최종 메커니즘 확정 뒤 매뉴얼만 보고 저작·캡처한 새 세트이며, 생성기는 선정 실행(no_rag) 외에 서명 전까지 한 번도 실행되지 않았다(사전등록 5)."),
}


def load_runs(tags):
    d = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list))))   # model -> rep -> backend -> metric -> [per-scenario]
    per_sc = defaultdict(lambda: defaultdict(list))   # (model, backend, sid) -> [acc per rep]
    steps = defaultdict(lambda: defaultdict(list))    # (model, sid, step) -> [(matched, hall)] for full_system
    cost = defaultdict(float); n_files = 0; commits = set(); errs = 0
    for tag in tags:
        for f in sorted(glob.glob(str(ROOT / "data/eval/results" / f"run_*_{tag}_r*_*.json"))):
            m = re.match(rf"run_([a-z]+)_{tag}_r(\d+)_", os.path.basename(f))
            if not m or m.group(1) not in MODELS:
                continue
            run = json.load(open(f, encoding="utf-8")); n_files += 1; commits.add(run["code_version"]["commit"][:7])
            model, rep = m.group(1), int(m.group(2))
            for sc in run["scenarios"]:
                for b, bd in sc["backends"].items():
                    for k in ("step_accuracy", "hallucination_rate", "goal_completion_rate", "mean_cost_total_usd", "mean_latency_sec"):
                        if bd.get(k) is not None:
                            d[model][rep][b][k].append(bd[k])
                    per_sc[(model, b, sc["scenario_id"])][rep].append(bd["step_accuracy"])
                    for s in bd.get("per_step") or []:
                        errs += 1 if s.get("error") else 0
                        cost[model] += float(s.get("cost_total_usd") or 0)
                        if b == "full_system":
                            steps[(model, sc["scenario_id"])][s["step_index"]].append((bool(s.get("matched")), bool(s.get("hallucinated"))))
    return d, per_sc, steps, cost, n_files, commits, errs


def add_table(doc, header, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Light Grid Accent 1"
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]; c.text = str(h)
        for p in c.paragraphs:
            for r in p.runs: r.font.bold = True; r.font.size = Pt(9)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v)
            for p in cells[i].paragraphs:
                for r in p.runs: r.font.size = Pt(9)
    doc.add_paragraph()
    return t


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--study", type=int, required=True); ap.add_argument("--out", required=True)
    args = ap.parse_args(); cfg = CFG[args.study]
    d, per_sc, steps, cost, n_files, commits, errs = load_runs(cfg["tags"])
    verdict = open(ROOT / cfg["verdict"], encoding="utf-8").read() if (ROOT / cfg["verdict"]).exists() else "(verdict file missing)"
    prereg = open(ROOT / cfg["prereg"], encoding="utf-8").read() if (ROOT / cfg["prereg"]).exists() else ""
    scen = {}
    for sd in cfg["scen_dirs"]:
        for f in glob.glob(str(ROOT / sd / "*.json")):
            sc = json.load(open(f, encoding="utf-8")); scen[sc["scenario_id"]] = sc

    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Malgun Gothic"; st.font.size = Pt(10)
    st.element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", "Malgun Gothic")
    doc.add_heading(cfg["title"], level=0)
    doc.add_paragraph("작성: 메인 세션(Claude), 사용자 위임. 문서 성격: 구현 방식과 테스트 결과의 사실 기록(논문 서술 없음). 근거 파일: " + ", ".join([cfg["verdict"], cfg["prereg"], "data/eval/results/methodology_audit_trail.md"]))
    doc.add_paragraph(cfg["nature"])

    doc.add_heading("1. GeoLens 구현 방식 (평가 시점의 최종 메커니즘)", level=1)
    impl = [
        ("입력", "사용자 목표 문장 + 현재 화면 스크린샷(JPEG). 매뉴얼 PDF는 800토큰 청크(100 겹침)로 분할해 bge-m3 임베딩으로 ChromaDB(v4 KB)에 저장. 매뉴얼의 각 절차는 워크플로우 그래프(노드 = 도달한 화면 상태, 엣지 = 다음 상태로 가는 동작 지시)로 저작되고 노드마다 매뉴얼 청크가 연결된다(linked_chunks, 절 출처 제한)."),
        ("1) 비전", "gemini-2.5-flash가 스크린샷의 창 제목·메뉴·버튼·필드 라벨과 값·트리/목록 항목을 원문 그대로 JSON으로 추출(프롬프트 v3, temperature 0)."),
        ("2) 후보 풀", "비전 JSON과 노드 signature의 임베딩 유사도 top-5 ∪ CLIP 이미지 유사도 top-3 ∪ 그래프 prior(직전 확정 노드의 1~2-hop 후속, ROUTER_PRIOR_HOPS=2)."),
        ("3) rerank", "gemini-2.5-flash가 후보 중 현재 화면 상태에 맞는 노드를 고른다(프롬프트 v4: 상태 일치 규칙, 같은 대화상자 후보의 필드 상태 대조, 세션에서 이미 준 지시 목록)."),
        ("4) 라우팅 규칙", "R1 세션 고정(같은 대화상자 제목의 다른 워크플로우 노드로 튀는 것을 세션 워크플로우로 되돌림). R2‴ 이력 전진(직전 지시가 직전 노드의 나가는 엣지를 0.6 이상 덮으면 후속으로 전진; 목표 대화상자가 아직 안 열렸거나 직전 대화상자가 아직 열려 있으면 전진하지 않음). R3 화면 증거 전진(직전 노드의 후속 사슬(≤3)에서 화면에 새로 나타난 고유 키워드·대화상자 출현/소멸 증거가 있는 가장 먼 노드로 전진; 결정적)."),
        ("5) 맥락 조립 v8", "라우팅된 노드의 도달 상태 + 들어온 엣지 1개(0번) + 나가는 후속 사슬 3개 엣지를 '동작 → 만들어지는 화면 상태' 순서로 제시하고, 화면과 대조해 0번부터 결과가 보이지 않는 첫 동작만 지시(직전 지시 결과가 화면에 없으면 반복, 묶음 지시는 첫 미완료 부분만, 정확히 한 동작, 종단이면 완료 센티널). 노드 연결 청크(3 × 800자) + 목표 질의 벡터 검색(1,500자). 라우팅 실패 시 벡터 검색만(3,900자 = vanilla_budget과 동일)."),
        ("6) 생성기", "gemini-2.5-pro / claude-sonnet-4-6 / gpt-4o가 같은 프롬프트(v3: 화면·맥락에 없는 단축키·수정자 키·메뉴 경로 금지)로 한 동작을 한국어로 출력. temperature 0.2, 1,024토큰."),
        ("비교군", "no_rag(맥락 없음), vanilla_budget(목표 질의 벡터 검색 3,900자), vanilla_vector(무절단 벡터 검색). 생성기·프롬프트·채점기는 전 백엔드 동일."),
        ("채점", "step accuracy = 응답이 스텝의 정답 패턴/키워드/허용 대안에 부합(완료 센티널은 목표 도달 화면에서만). hallucination(v6) = 응답의 UI 참조 중 화면(GT visible_elements)과 매뉴얼 절 본문 어디에도 없는 라벨(토크나이저 v6). consensus judge(Claude Haiku + Gemini Flash)는 기술 지표."),
        ("판정 규칙", "replicate(= 시나리오 등가중 평균) 단위, 모델 층화 순열검정 10,000회(seed 42). 비교 1 = full vs vanilla_budget, 비교 2 = full vs vanilla_vector. step 조건 = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음; hall 조건 = full ≤ 비교군 2/3 이상. 등급 A(둘 다) / A′(step만) / B(방향만) / C."),
    ]
    add_table(doc, ["항목", "내용"], impl)

    doc.add_heading("2. 실행 기록", level=1)
    doc.add_paragraph(f"결과 파일 {n_files}개(태그 {', '.join(cfg['tags'])}), 코드 커밋 스탬프 {sorted(commits)}, 스텝 오류 {errs}. 실행 중 api/·풀·GT 불변(감사 기록).")
    doc.add_paragraph("비용(결과 JSON 합산, 생성기 + 보조 호출): " + ", ".join(f"{m} ${cost[m]:.2f}" for m in MODELS))
    doc.add_paragraph("판정 세트: " + "; ".join(f"{sid} ({len(sc['steps'])}스텝, {sc.get('manual_reference','')[:60]})" for sid, sc in sorted(scen.items())))

    doc.add_heading("3. 결과 요약 (replicate 평균, n = 10)", level=1)
    rows = []
    for m in MODELS:
        for b in BACKENDS:
            accs = [statistics.mean(d[m][r][b]["step_accuracy"]) for r in sorted(d[m]) if d[m][r][b]["step_accuracy"]]
            halls = [statistics.mean(d[m][r][b]["hallucination_rate"]) for r in sorted(d[m]) if d[m][r][b]["hallucination_rate"]]
            goals = [statistics.mean(d[m][r][b]["goal_completion_rate"]) for r in sorted(d[m]) if d[m][r][b]["goal_completion_rate"]]
            if accs:
                rows.append([m, BACKEND_KO[b], len(accs), f"{statistics.mean(accs):.3f} ± {statistics.pstdev(accs):.3f}", f"{statistics.mean(halls):.3f}", f"{statistics.mean(goals):.3f}" if goals else "-"])
    add_table(doc, ["모델", "백엔드", "n", "step accuracy (평균 ± sd)", "hall v6", "goal completion"], rows)

    doc.add_heading("4. 시나리오별 step accuracy (10회 평균)", level=1)
    sids = sorted(scen)
    rows = []
    for m in MODELS:
        for b in BACKENDS:
            row = [m, BACKEND_KO[b]]
            for sid in sids:
                v = [statistics.mean(x) for x in per_sc[(m, b, sid)].values()]
                row.append(f"{statistics.mean(v):.3f}" if v else "-")
            rows.append(row)
    add_table(doc, ["모델", "백엔드"] + [s.replace("opendtect__", "").replace("qgis__", "q:") for s in sids], rows)

    doc.add_heading("5. full_system 스텝별 정답률·환각 (10회 중 정답 횟수 / 환각 횟수)", level=1)
    for sid in sids:
        doc.add_paragraph(sid, style="Heading 3")
        n_steps = len(scen[sid]["steps"]); rows = []
        for i in range(n_steps):
            row = [f"s{i}", (scen[sid]["steps"][i].get("expected_action_keywords") or [""])[0][:30]]
            for m in MODELS:
                v = steps[(m, sid)].get(i) or []
                row.append(f"{sum(1 for ok, _ in v if ok)}/{len(v)}  hall {sum(1 for _, h in v if h)}" if v else "-")
            rows.append(row)
        add_table(doc, ["스텝", "정답 키워드", "gemini", "claude", "gpt"], rows)

    doc.add_heading("6. 판정 (verdict 스크립트 출력 원문)", level=1)
    for line in verdict.splitlines():
        if line.startswith("#"):
            doc.add_paragraph(line.lstrip("# ").strip(), style="Heading 3")
        elif line.strip():
            p = doc.add_paragraph(line); p.paragraph_format.space_after = Pt(0)
            for r in p.runs: r.font.size = Pt(9)

    doc.add_heading("7. 사전등록 원문", level=1)
    for line in prereg.splitlines():
        if line.startswith("#"):
            doc.add_paragraph(line.lstrip("# ").strip(), style="Heading 3")
        elif line.strip():
            p = doc.add_paragraph(line); p.paragraph_format.space_after = Pt(0)
            for r in p.runs: r.font.size = Pt(8)
    doc.save(args.out); print("saved", args.out)


if __name__ == "__main__":
    main()
