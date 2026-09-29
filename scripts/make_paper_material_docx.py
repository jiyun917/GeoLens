# -*- coding: utf-8 -*-
"""Word record organised as development set / test set (no development narrative): the GeoLens implementation, the
two scenario sets, the evaluation design, the main result on the held-out test set (study 5), the in-sample
development-set result (study 4) as reference, run record, and the signed test-set pre-registration as appendix.
Usage: .venv/Scripts/python.exe scripts/make_paper_material_docx.py --out "C:/Users/user/Downloads/STUDY-신규세트.docx"
"""
from __future__ import annotations
import argparse, glob, json, statistics, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from make_study_docx import load_runs, add_table, MODELS, BACKENDS, BACKEND_KO, ROOT  # noqa: E402
from docx import Document
from docx.shared import Pt

TEST_TAGS = ["study5_opendtect", "study5_qgis"]
DEV_TAGS = ["study4_opendtect", "study4_qgis"]
TEST_DIRS = ["data/eval/scenarios/.study5_test_opendtect", "data/eval/scenarios/.study5_test_qgis"]
DEV_DIRS = ["data/eval/scenarios/.study4_test_opendtect", "data/eval/scenarios/.study4_test_qgis"]
SOFT = {"opendtect": "OpendTect 7.0.9 / F3 Demo 2023", "qgis": "QGIS 3.44 / Training Data"}
MANUAL = {"opendtect": "Introduction to OpendTect & OpendTect Pro Training Manual 7.0 (486 청크)", "qgis": "QGIS 3.44 Training Manual (733 청크)"}
CAT_KO = {"fault_interpretation": "단층 해석", "horizon_tracking": "호라이즌 추적", "raster_analysis": "래스터 분석", "symbology": "심볼로지", "attribute_analysis": "속성 분석", "projections": "투영", "vector_analysis": "벡터 분석"}
# manual section labels used in the pre-registrations
SECTION = {"opendtect__fault_sticks__01": "§1.4.3b FaultStickSet", "opendtect__horizon_autotrack__01": "§1.4.2a 3D auto-track", "opendtect__horizon_2dviewer__01": "§1.4.2b 2D viewer horizon",
           "qgis__rule_classification__01": "§3.3.5 Rule-based Classification", "qgis__reclassify_raster__01": "§7.3.10 Reclassifying the Raster", "qgis__vector_buffer__01": "§6.2.6 Buffer (Distances From Schools and Roads)",
           "opendtect__spectral_decomp__01": "§1.5.2a Spectral Decomposition", "qgis__custom_projection__01": "§6.1.4 Creating Your Own Projection", "qgis__aspect_north__01": "§7.3.6 Finding the north-facing aspect"}
DEV_SELECT = {"opendtect__fault_sticks__01": 0.333, "opendtect__horizon_autotrack__01": 0.238, "opendtect__horizon_2dviewer__01": 0.778, "qgis__rule_classification__01": 0.600, "qgis__reclassify_raster__01": 0.704}
TEST_SELECT = {"opendtect__spectral_decomp__01": 0.667, "qgis__aspect_north__01": 0.833, "qgis__custom_projection__01": 0.815}


def load_scen(dirs):
    out = {}
    for sd in dirs:
        for f in glob.glob(str(ROOT / sd / "*.json")):
            sc = json.load(open(f, encoding="utf-8")); out[sc["scenario_id"]] = sc
    return out


def rep_means(d, m, b, k):
    return [statistics.mean(d[m][r][b][k]) for r in sorted(d[m]) if d[m][r][b][k]]


def summary_rows(d):
    rows = []
    for m in MODELS:
        for b in BACKENDS:
            accs, halls, goals = rep_means(d, m, b, "step_accuracy"), rep_means(d, m, b, "hallucination_rate"), rep_means(d, m, b, "goal_completion_rate")
            cost, lat = rep_means(d, m, b, "mean_cost_total_usd"), rep_means(d, m, b, "mean_latency_sec")
            if accs:
                rows.append([m, BACKEND_KO[b], len(accs), f"{statistics.mean(accs):.3f} ± {statistics.pstdev(accs):.3f}", f"{statistics.mean(halls):.3f}",
                             f"{statistics.mean(goals):.3f}" if goals else "-", f"{statistics.mean(cost):.4f}" if cost else "-", f"{statistics.mean(lat):.1f}" if lat else "-"])
    return rows


def per_scenario_rows(per_sc, sids):
    rows = []
    for m in MODELS:
        for b in BACKENDS:
            row = [m, BACKEND_KO[b]]
            for sid in sids:
                v = [statistics.mean(x) for x in per_sc[(m, b, sid)].values()]
                row.append(f"{statistics.mean(v):.3f}" if v else "-")
            rows.append(row)
    return rows


def short(sid):
    return sid.replace("opendtect__", "").replace("qgis__", "q:").replace("__01", "")


def verdict_tables(md_text):
    """Return [(title, header, rows, bullet lines)] for the two comparisons and the Holm line from a verdict markdown."""
    out, cur, header, rows, bullets, holm = [], None, None, [], [], ""
    for line in md_text.splitlines():
        if line.startswith("### 비교"):
            if cur: out.append((cur, header, rows, bullets))
            cur, header, rows, bullets = line.lstrip("# ").strip(), None, [], []
        elif cur and line.startswith("|") and not line.startswith("|---"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if header is None: header = cells
            else: rows.append(cells)
        elif cur and line.startswith("- "):
            bullets.append(line[2:].replace("**", ""))
        elif line.startswith("Holm"):
            holm = line.replace("**", "")
            if cur: out.append((cur, header, rows, bullets)); cur = None
        elif line.startswith("## ") and cur:
            out.append((cur, header, rows, bullets)); cur = None
    return out, holm


def add_md_lines(doc, text, size=8, skip_heading_prefix=None):
    for line in text.splitlines():
        if line.startswith("#"):
            doc.add_paragraph(line.lstrip("# ").strip(), style="Heading 3")
        elif line.strip():
            p = doc.add_paragraph(line); p.paragraph_format.space_after = Pt(0)
            for r in p.runs: r.font.size = Pt(size)


def para(doc, text, size=None, bold=False):
    p = doc.add_paragraph(); r = p.add_run(text); r.font.bold = bold
    if size: r.font.size = Pt(size)
    return p


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); args = ap.parse_args()
    dT, per_scT, stepsT, costT, n_filesT, commitsT, errsT = load_runs(TEST_TAGS)
    dD, per_scD, stepsD, costD, n_filesD, commitsD, errsD = load_runs(DEV_TAGS)
    scenT, scenD = load_scen(TEST_DIRS), load_scen(DEV_DIRS)
    vb = json.load(open(ROOT / "data/eval/scenarios/qgis__vector_buffer__01.json", encoding="utf-8"))
    verdictT = open(ROOT / "data/eval/results/verdict_study5.md", encoding="utf-8").read()
    verdictD = open(ROOT / "data/eval/results/verdict_study4.md", encoding="utf-8").read()
    prereg = open(ROOT / "data/eval/study4/study5_pre_registration_DRAFT.md", encoding="utf-8").read()

    doc = Document()
    st = doc.styles["Normal"]; st.font.name = "Malgun Gothic"; st.font.size = Pt(10)
    st.element.rPr.rFonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}eastAsia", "Malgun Gothic")
    doc.add_heading("GeoLens 평가 자료 — 개발 세트 / 테스트 세트", level=0)
    para(doc, "작성: 메인 세션(Claude), 사용자 위임. 문서 성격: 구현 방식·시나리오 세트·평가 설계·결과의 사실 기록. 주 결과는 테스트 세트(메커니즘 확정 뒤 처음 보는 3 시나리오, 사전등록·서명 후 실행)이며, 개발 세트 결과는 in-sample 참고값이다.", size=9)

    # ---------------------------------------------------------------- 0. 개요
    doc.add_heading("0. 개요", level=1)
    para(doc, "GeoLens는 소프트웨어 매뉴얼을 워크플로우 그래프와 벡터 KB로 저장하고, 사용자의 현재 화면(스크린샷)과 목표 문장을 받아 다음 한 동작을 한국어로 지시하는 화면 인식 RAG 안내 시스템이다. 평가는 두 세트로 나눈다.")
    add_table(doc, ["세트", "구성", "용도", "결과의 성격"], [
        ["개발 세트", "OpendTect 3 + QGIS 3 시나리오 (성능 측정은 5 시나리오 44스텝)", "메커니즘(라우팅 규칙·맥락 조립·프롬프트·채점기) 설계와 조정", "in-sample. 최종 메커니즘의 개발 세트 성능(§5), 일반화 근거로 쓰지 않음"],
        ["테스트 세트", "OpendTect 1 + QGIS 2 시나리오 (24스텝), 메커니즘 확정 뒤 매뉴얼만 보고 저작·캡처", "최종 메커니즘의 확인 평가(사전등록 서명 후 실행)", "held-out. 주 결과(§4)"],
    ])
    para(doc, "두 세트 모두 3 생성기 모델 × 4 백엔드(no_rag, vanilla_budget, vanilla_vector, GeoLens) × 10회 반복으로 같은 채점기·같은 판정 규칙을 적용했다. 테스트 세트 결과: 비교 1(GeoLens vs 고정 예산 벡터 RAG) A, 비교 2(GeoLens vs 무절단 벡터 RAG) A. 개발 세트 결과: A′ / A.")

    # ---------------------------------------------------------------- 1. 구현
    doc.add_heading("1. GeoLens 구현 방식", level=1)
    impl = [
        ("입력", "사용자 목표 문장 + 현재 화면 스크린샷(JPEG). 매뉴얼 PDF는 800토큰 청크(100 겹침)로 분할해 bge-m3 임베딩으로 ChromaDB(v4 KB)에 저장. 매뉴얼의 각 절차는 워크플로우 그래프(노드 = 도달한 화면 상태, 엣지 = 다음 상태로 가는 동작 지시)로 저작되고 노드마다 매뉴얼 청크가 연결된다(linked_chunks, 절 출처 제한). 워크플로우 풀 13개(개발·테스트 세트 절차 + 같은 매뉴얼의 다른 절차; 라우팅은 이 풀 전체에서 고른다)."),
        ("1) 비전", "gemini-2.5-flash가 스크린샷의 창 제목·메뉴·버튼·필드 라벨과 값·트리/목록 항목을 원문 그대로 JSON으로 추출(프롬프트 v3, temperature 0)."),
        ("2) 후보 풀", "비전 JSON과 노드 signature의 임베딩 유사도 top-5 ∪ CLIP 이미지 유사도 top-3 ∪ 그래프 prior(직전 확정 노드의 1~2-hop 후속)."),
        ("3) rerank", "gemini-2.5-flash가 후보 중 현재 화면 상태에 맞는 노드를 고른다(프롬프트 v4: 상태 일치 규칙, 같은 대화상자 후보의 필드 상태 대조, 세션에서 이미 준 지시 목록)."),
        ("4) 라우팅 규칙", "R1 세션 고정(같은 대화상자 제목의 다른 워크플로우 노드로 튀는 것을 세션 워크플로우로 되돌림). R2 이력 전진(직전 지시가 직전 노드의 나가는 엣지를 0.6 이상 덮으면 후속으로 전진; 목표 대화상자가 아직 안 열렸거나 직전 대화상자가 아직 열려 있으면 전진하지 않음). R3 화면 증거 전진(직전 노드의 후속 사슬(≤3)에서 화면에 새로 나타난 고유 키워드·대화상자 출현/소멸 증거가 있는 가장 먼 노드로 전진; 결정적)."),
        ("5) 맥락 조립 v8", "라우팅된 노드의 도달 상태 + 들어온 엣지 1개(0번) + 나가는 후속 사슬 3개 엣지를 '동작 → 만들어지는 화면 상태' 순서로 제시하고, 화면과 대조해 0번부터 결과가 보이지 않는 첫 동작만 지시(직전 지시 결과가 화면에 없으면 반복, 묶음 지시는 첫 미완료 부분만, 정확히 한 동작, 종단이면 완료 센티널). 노드 연결 청크(3 × 800자) + 목표 질의 벡터 검색(1,500자). 라우팅 실패 시 벡터 검색만(3,900자 = vanilla_budget과 동일)."),
        ("6) 생성기", "gemini-2.5-pro / claude-sonnet-4-6 / gpt-4o가 같은 프롬프트(v3: 화면·맥락에 없는 단축키·수정자 키·메뉴 경로 금지)로 한 동작을 한국어로 출력. temperature 0.2, 1,024토큰."),
        ("세션", "각 시나리오는 스텝 순서대로 한 세션으로 실행된다. 직전 지시와 직전 화면 상태를 다음 스텝의 라우팅 입력으로 넘긴다(R1·R2·R3의 입력)."),
    ]
    add_table(doc, ["항목", "내용"], impl)

    # ---------------------------------------------------------------- 2. 시나리오 세트
    doc.add_heading("2. 시나리오 세트", level=1)
    para(doc, "시나리오 = 매뉴얼의 한 절차를 목표 문장·초기 상태·스텝(각 스텝 = 스크린샷 + 화면 GT + 정답 패턴/키워드/허용 대안)으로 옮긴 것. 스크린샷은 실제 소프트웨어에서 절차를 수행하며 캡처했고, 화면 GT(visible_elements: 창 제목·메뉴·버튼·필드·값)는 gemini-2.5-pro 열거 + 스크린샷만 보는 검토자의 대조로 확정했다.")
    doc.add_heading("2.1 개발 세트", level=2)
    rows = []
    for sid in ["opendtect__fault_sticks__01", "opendtect__horizon_autotrack__01", "opendtect__horizon_2dviewer__01", "qgis__rule_classification__01", "qgis__reclassify_raster__01"]:
        sc = scenD[sid]; sw = sid.split("__")[0]
        rows.append([sid, SOFT[sw], SECTION[sid], CAT_KO.get(sc.get("category"), sc.get("category")), len(sc["steps"]), f"{DEV_SELECT[sid]:.3f}", "성능 측정(§5)"])
    rows.append(["qgis__vector_buffer__01", SOFT["qgis"], SECTION["qgis__vector_buffer__01"], CAT_KO["vector_analysis"], len(vb["steps"]), "-", "설계에만 사용(노드 signature 결함으로 성능 측정 제외)"])
    add_table(doc, ["시나리오", "소프트웨어 / 데이터", "매뉴얼 절", "과제 유형", "스텝", "no_rag 선정값*", "용도"], rows)
    para(doc, "* 선정값 = 시스템 실행 전 no_rag만 3모델 × 1회 돌린 평균 step accuracy. 0.85 미만인 시나리오만 판정 세트로 채택하는 규칙(매뉴얼 없이도 풀리는 과제 배제).", size=8)

    doc.add_heading("2.2 테스트 세트", level=2)
    rows = []
    for sid in ["opendtect__spectral_decomp__01", "qgis__custom_projection__01", "qgis__aspect_north__01"]:
        sc = scenT[sid]; sw = sid.split("__")[0]
        rows.append([sid, SOFT[sw], SECTION[sid], CAT_KO.get(sc.get("category"), sc.get("category")), len(sc["steps"]), f"{TEST_SELECT[sid]:.3f}", "주 결과(§4)"])
    add_table(doc, ["시나리오", "소프트웨어 / 데이터", "매뉴얼 절", "과제 유형", "스텝", "no_rag 선정값*", "용도"], rows)
    para(doc, "테스트 세트 작성 절차(모두 모델 실행 전, 사전등록 §3에 기록):")
    for t in [
        "1) 메커니즘 확정 뒤 매뉴얼만 보고 워크플로우·시나리오 골격·정답 패턴을 저작(커밋 9ba5b23). 그 뒤 사용자가 실제 소프트웨어에서 24장을 캡처(재캡처 없음). 버전 차이(OpendTect 7.0.9의 'Select Horizons', QGIS 3.44의 'Input layers' 등)는 캡처 노트에 기록.",
        "2) 벤치용 JPEG는 quality 85로 통일(원본 PNG 불변).",
        "3) KB signature 문자열 검증(K1): 워크플로우 노드의 대화상자 제목·키워드 문자열을 비전 모델이 읽은 화면 문자열과 대조해 문자열만 정정(대화상자 24/24 일치, 키워드 122/129 화면 존재; 나머지 7개는 매뉴얼 별칭으로 유지). 라우팅 dry-run(생성기 없음) 23/24 = 0.958.",
        "4) 화면 GT: gemini-2.5-pro 열거 → 초안 → 스크린샷만 보는 외부 검토(1,498항목, 표본 오독률 1.34%; 삭제 1·정정 32·추가 36) → 확정. 정답 패턴·키워드는 저작본 유지(별칭 1건 추가: 'Input layers').",
        "5) 선정 실행(no_rag ×1 ×3모델): E 0.667, G 0.833, F 0.815 → 셋 다 채택. 선정 응답은 GT·시스템 수정에 쓰지 않음.",
        "6) 사전등록 서명(2026-09-28T19:14:20Z, 커밋 5be5a78, 태그 study5-prereg-signed) → 본 실행. 결과를 본 뒤 GT·채점기·메커니즘·signature 불변.",
    ]:
        para(doc, t, size=9)
    para(doc, "개발 세트의 GT는 각 시나리오가 처음 쓰인 시점에 같은 방식(열거 → 검토 → 확정)으로 확정되어 그대로 사용했다(§5 실행에서 바이트 동일).", size=9)

    # ---------------------------------------------------------------- 3. 평가 설계
    doc.add_heading("3. 평가 설계", level=1)
    add_table(doc, ["항목", "내용"], [
        ("백엔드(4)", "no_rag: 맥락 없음(목표 + 화면만). vanilla_budget: 목표 질의 벡터 검색 3,900자(GeoLens의 맥락 예산과 동일). vanilla_vector: 무절단 벡터 검색(top-k 전부). full_system(GeoLens): §1. 생성기·프롬프트·temperature·채점기는 전 백엔드 동일."),
        ("생성기 모델(3)", "gemini-2.5-pro, claude-sonnet-4-6, gpt-4o."),
        ("매트릭스", "모델 3 × 백엔드 4 × 시나리오(개발 5 / 테스트 3) × 10회 반복. 각 반복은 시나리오를 스텝 순서대로 한 세션으로 실행."),
        ("step accuracy", "응답이 해당 스텝의 정답 패턴(정규식)·키워드·허용 대안에 부합하면 1. 완료 센티널은 목표 도달 화면에서만 정답."),
        ("hallucination rate (v6)", "응답이 언급한 UI 라벨 중 화면 GT(visible_elements)와 매뉴얼 해당 절 본문 어디에도 없는 것의 비율(라틴 라벨 토크나이저 v6)."),
        ("기술 지표", "goal completion(세션 종료 시 완료 선언이 목표 도달 화면에서 나왔는가), 스텝당 비용(생성기 + 비전·rerank·judge 보조 호출), 스텝당 지연, consensus judge(Claude Haiku + Gemini Flash)가 매긴 step 정답률(패턴 채점과 별개의 기술 지표)."),
        ("판정 규칙", "집계 단위 replicate(= 시나리오 등가중 평균), n = 10. 비교 1 = GeoLens vs vanilla_budget, 비교 2 = GeoLens vs vanilla_vector. 모델을 층으로 한 층화 순열검정 10,000회(seed 42). step 조건 = 3모델 중 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음. hall 조건 = GeoLens 환각 ≤ 비교군인 모델 ≥ 2/3. 등급 A(둘 다 성립) / A′(step만) / B(방향만) / C. Holm(패밀리 2) 병기."),
        ("실행 조건", "서명 커밋에서 실행(결과 파일마다 커밋·dirty 여부 스탬프), 실행 전 preflight(환경 핀·KB·워크플로우 풀·GT 무결성), 실행 중 코드·GT·워크플로우 불변, 장애 시 진행 중 반복 폐기 후 재개. 판정은 스크립트가 기계적으로 산출."),
    ])

    # ---------------------------------------------------------------- 4. 주 결과: 테스트 세트
    doc.add_heading("4. 주 결과 — 테스트 세트 (held-out, 3 시나리오 × 10회)", level=1)
    doc.add_heading("4.1 요약 (replicate 평균, n = 10)", level=2)
    add_table(doc, ["모델", "백엔드", "n", "step accuracy (평균 ± sd)", "hall v6", "goal completion", "비용 $/스텝", "지연 s/스텝"], summary_rows(dT))
    doc.add_heading("4.2 시나리오별 step accuracy (10회 평균)", level=2)
    sidsT = ["opendtect__spectral_decomp__01", "qgis__custom_projection__01", "qgis__aspect_north__01"]
    add_table(doc, ["모델", "백엔드"] + [short(s) for s in sidsT], per_scenario_rows(per_scT, sidsT))
    doc.add_heading("4.3 GeoLens 스텝별 정답 횟수 / 환각 플래그 횟수 (10회 중)", level=2)
    for sid in sidsT:
        doc.add_paragraph(sid, style="Heading 3")
        rows = []
        for i in range(len(scenT[sid]["steps"])):
            row = [f"s{i}", (scenT[sid]["steps"][i].get("expected_action_keywords") or [""])[0][:30]]
            for m in MODELS:
                v = stepsT[(m, sid)].get(i) or []
                row.append(f"{sum(1 for ok, _ in v if ok)}/{len(v)}  hall {sum(1 for _, h in v if h)}" if v else "-")
            rows.append(row)
        add_table(doc, ["스텝", "정답 키워드", "gemini", "claude", "gpt"], rows)
    doc.add_heading("4.4 판정 (사전등록 §5, 스크립트 산출)", level=2)
    tabs, holm = verdict_tables(verdictT)
    for title, header, rows, bullets in tabs:
        doc.add_paragraph(title, style="Heading 3"); add_table(doc, header, rows)
        for b in bullets: para(doc, "• " + b, size=9)
    para(doc, holm, size=9, bold=True)
    doc.add_heading("4.5 사전 예측 대비 결과", level=2)
    add_table(doc, ["#", "예측(실행 전)", "결과", "판정"], [
        ["Q1", "테스트 세트 no_rag 평균 step accuracy < 0.85", "gemini 0.835, claude 0.848, gpt 0.752", "적중(세트 유지)"],
        ["Q2", "vanilla_budget > no_rag (+3pp, 2/3 이상)", "gemini −0.056, claude +0.074, gpt +0.137", "적중(2/3)"],
        ["Q3", "비교 1 방향 3/3, p < 0.05", "3/3, p 0.0001, Δ +0.111", "적중"],
        ["Q4", "비교 2 방향 3/3, p < 0.05", "3/3, p 0.0001, Δ +0.077", "적중"],
        ["Q5", "환각(v6) GeoLens ≤ 비교군, 각 3/3", "2/3, 2/3 (GPT GeoLens 0.137 > 0.000)", "반증(등급 조건은 2/3이라 A 유지)"],
        ["Q6", "라우팅 노드 정답률 ≥ 0.85, R3 오전진 ≤ 2%", "0.888 / 0.954 / 0.954; R3 오전진 5/720 = 0.69%", "적중"],
        ["Q7", "F s4(WKT)에서 no_rag는 PROJCRS 문자열을 못 내고 RAG 백엔드는 낸다", "어느 백엔드도 PROJCRS 문자열을 내지 않음(다른 패턴 대안으로 정답). GPT no_rag 3/10 vs RAG 7–10/10", "반증(기록)"],
    ])
    doc.add_heading("4.6 사후 기술 (결과 관측 후, 수정 없음)", level=2)
    for t in [
        "GPT GeoLens 환각 0.137(37/240 플래그)의 출처: spectral_decomp s0 'Attribute 3D' 10/10(화면 라벨은 'Attribute Set 3D'), aspect_north s2 'OK' 10/10(Raster Calculator 대화상자의 버튼은 Run/Close; 스텝 자체는 Input layers 동작으로 정답), custom_projection s6 'User Defined Coordinate Systems' 10/10(매뉴얼 표기; 화면은 'User-defined'), spectral_decomp s4 'Output frequency 24 Hz' 2/10. Gemini·Claude의 GeoLens 환각은 0.000.",
        "Gemini GeoLens가 spectral_decomp s4(속성 종류 Spectral Decomposition 선택)에서 0/10: 라우팅은 10/10 정답 노드였으나 생성기가 'Similarity 드롭다운 메뉴를 클릭하세요'(드롭다운을 여는 앞 동작만)를 지시해 패턴 미충족. GPT가 spectral_decomp s0(Add Color Blended)에서 0/10: 세션 이력이 없는 빈 scene 화면에서 rerank가 세 모델 모두 10/10 다른 워크플로우(seismic_attribute)의 시작 노드를 골랐고(사전등록 dry-run에서 예고된 동점 화면), Gemini·Claude는 목표·벡터 맥락으로 정답 동작을 냈지만 GPT는 그 워크플로우의 첫 동작('Attribute 3D 아이콘 클릭')을 지시.",
        "라우팅(GeoLens, 모델당 240스텝): 노드 정답 gemini 213, claude 229, gpt 229. R3 화면 전진 57회 중 GT 밖 노드 5회(모두 Gemini), R2 이력 전진 27회 모두 GT 노드. Gemini의 rerank 호출 실패 3스텝(custom_projection s0)은 워크플로우 맥락 없이 벡터 검색만으로 생성.",
        "불리한 수치: GeoLens 스텝당 지연 17–28초(비교군 2–11초; 비전 + rerank + 생성), 스텝당 비용은 vanilla_budget보다 높고(전 모델) Gemini는 vanilla_vector보다도 높음. Gemini vanilla_budget < no_rag. F(custom_projection)는 no_rag도 0.933–0.989로 천장에 가까워 변별력이 낮음(사전등록 §7).",
        "judge 누락 1스텝(Gemini opendtect r1 vanilla_budget 8/9; 기술 지표만 영향). 스텝 오류 0/2,880.",
    ]:
        para(doc, "• " + t, size=9)

    # ---------------------------------------------------------------- 5. 참고: 개발 세트
    doc.add_heading("5. 참고 결과 — 개발 세트 (in-sample, 5 시나리오 × 10회)", level=1)
    para(doc, "최종 메커니즘을 개발 세트 5 시나리오(44스텝)에서 같은 설계로 10회 실행한 결과. 이 시나리오들은 메커니즘 설계·조정에 쓰였으므로 값은 낙관적일 수 있으며 일반화 근거로 쓰지 않는다. 실행·판정 절차는 §3과 동일(사전등록 4, 커밋 834d58b, 태그 study4-prereg-signed).", size=9)
    doc.add_heading("5.1 요약 (replicate 평균, n = 10)", level=2)
    add_table(doc, ["모델", "백엔드", "n", "step accuracy (평균 ± sd)", "hall v6", "goal completion", "비용 $/스텝", "지연 s/스텝"], summary_rows(dD))
    doc.add_heading("5.2 시나리오별 step accuracy (10회 평균)", level=2)
    sidsD = ["opendtect__fault_sticks__01", "opendtect__horizon_autotrack__01", "opendtect__horizon_2dviewer__01", "qgis__rule_classification__01", "qgis__reclassify_raster__01"]
    add_table(doc, ["모델", "백엔드"] + [short(s) for s in sidsD], per_scenario_rows(per_scD, sidsD))
    doc.add_heading("5.3 판정", level=2)
    tabs, holm = verdict_tables(verdictD)
    for title, header, rows, bullets in tabs:
        doc.add_paragraph(title, style="Heading 3"); add_table(doc, header, rows)
        for b in bullets: para(doc, "• " + b, size=9)
    para(doc, holm, size=9, bold=True)
    para(doc, "비교 1의 환각 조건 불성립(1/3)은 Claude 0.006·GPT 0.009(각각 rule_classification s2 'Shift' 3/10, horizon_2dviewer s0 'Add Data' 4/10의 라벨 불일치)가 비교군 0.000보다 큰 데서 온다.", size=9)

    # ---------------------------------------------------------------- 6. 실행 기록
    doc.add_heading("6. 실행 기록·재현 정보", level=1)
    add_table(doc, ["항목", "테스트 세트(§4)", "개발 세트(§5)"], [
        ["실행 시각(UTC)", "2026-09-28 19:14 → 2026-09-29 02:49", "2026-09-28 07:19 → 19:12"],
        ["서명 커밋 / 태그", "5be5a78 / study5-prereg-signed → study5-complete", "834d58b / study4-prereg-signed → study4-complete"],
        ["결과 파일", f"{n_filesT}개 (run_<model>_study5_<pass>_r<k>_*.json), 커밋 스탬프 {sorted(commitsT)}", f"{n_filesD}개 (run_<model>_study4_<pass>_r<k>_*.json), 커밋 스탬프 {sorted(commitsD)}"],
        ["스텝 수 / 오류", f"2,880 / {errsT}", f"5,280 / {errsD}"],
        ["기록 비용(생성기 + 보조 호출)", ", ".join(f"{m} ${costT[m]:.2f}" for m in MODELS), ", ".join(f"{m} ${costD[m]:.2f}" for m in MODELS)],
        ["중단·재개", "Gemini 선불 크레딧 소진(402)으로 QGIS 4회차 중단, 진행 중 반복 폐기, 충전 후 4회차부터 재개(코드·데이터 불변)", "Anthropic 크레딧 소진으로 1회 중단, 진행 중 반복 폐기 후 재개(코드·데이터 불변)"],
        ["판정 스크립트 / 출력", "scripts/verdict_study5.py → data/eval/results/verdict_study5.md", "scripts/verdict_study4.py → data/eval/results/verdict_study4.md"],
        ["사전등록", "data/eval/study4/study5_pre_registration_DRAFT.md (부록 A)", "data/eval/study4/study4_pre_registration_DRAFT.md"],
        ["감사 기록", "data/eval/results/methodology_audit_trail.md (V3-46~48)", "같은 파일 (V3-44~45, 47)"],
    ])
    para(doc, "환경 핀(양 세트 동일): GEOLENS_SCORER=v6, CONTEXT_ASSEMBLY=v8, ROUTER_SESSION_STICKY=1, ROUTER_HISTORY_ADVANCE=1, ROUTER_ADVANCE_MIN_COVERAGE=0.6, ROUTER_SCREEN_ADVANCE=1(hops 3, min tokens 1), ROUTER_PRIOR_HOPS=2, RERANK_SESSION_BLOCK=1, GEN_PROMPT_VERSION=v3, KB data/chromadb_v4, EMBED bge-m3, GEN_TEMPERATURE 0.2, GEN_MAX_TOKENS 1024, VANILLA_BUDGET_CHARS 3900.", size=8)

    # ---------------------------------------------------------------- 부록
    doc.add_heading("부록 A. 테스트 세트 사전등록 원문 (서명본, 수정 없음)", level=1)
    add_md_lines(doc, prereg, size=8)
    doc.save(args.out); print("saved", args.out)


if __name__ == "__main__":
    main()
