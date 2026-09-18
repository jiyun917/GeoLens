"""Generate a comprehensive Word summary of GeoLens paper experiment results.

Produces: out/GeoLens_실험결과종합_unified4.docx
"""

from docx import Document
from docx.shared import Pt, RGBColor, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime

OUT = r"out/GeoLens_실험결과종합_unified4.docx"

doc = Document()

# ─── Style setup ────────────────────────────────────────────────
style = doc.styles['Normal']
style.font.name = '맑은 고딕'
style.font.size = Pt(10)
style._element.rPr.rFonts.set(qn('w:eastAsia'), '맑은 고딕')

for h in ['Heading 1','Heading 2','Heading 3']:
    s = doc.styles[h]
    s.font.name = '맑은 고딕'
    s._element.rPr.rFonts.set(qn('w:eastAsia'), '맑은 고딕')

def set_cell_shading(cell, color_hex):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tc_pr.append(shd)

def add_table(doc, headers, rows, header_shade='D9E2F3', col_widths=None):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Light Grid Accent 1'
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        for p in hdr[i].paragraphs:
            for r in p.runs:
                r.bold = True
                r.font.size = Pt(9)
        set_cell_shading(hdr[i], header_shade)
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            t.rows[ri+1].cells[ci].text = str(val)
            for p in t.rows[ri+1].cells[ci].paragraphs:
                for r in p.runs:
                    r.font.size = Pt(9)
    if col_widths:
        for row in t.rows:
            for ci, w in enumerate(col_widths):
                row.cells[ci].width = Cm(w)
    return t

# ═══════════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════════
title = doc.add_heading('GeoLens 실험 결과 종합 보고서', level=0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = subtitle.add_run('Unified4 벤치 최종 판정 · 사전등록 대조 · 발견 · QGIS 이식성')
r.italic = True
r.font.size = Pt(12)

meta = doc.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
meta.add_run(f'작성일: 2026-08-10   |   실험 매트릭스: 4 모델 × 6 백엔드 × 5 replicates × 3 시나리오 + Gemini long_context\n')
meta.add_run('정지 규칙: 이 논문에서 unified5 는 없다 (본 문서가 최종 실험 매트릭스)').bold = True

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('요약 (Executive Summary)', level=1)

p = doc.add_paragraph()
p.add_run('판정: ').bold = True
r = p.add_run('A (시스템 우위) — 사전등록된 A 조건 4개 모두 충족')
r.bold = True
r.font.color.rgb = RGBColor(0x00, 0x66, 0x00)

doc.add_paragraph(
    '교수님이 요구하신 복잡한 워크플로우 시나리오 (8-스텝 attribute_computation) 를 '
    '추가하여 4 모델 × 6 백엔드 × 5 replicates × 3 시나리오 전 매트릭스 (1,920 스텝) '
    '를 재평가한 결과, 제안 시스템(full_system, hybrid RAG + workflow graph)이 '
    'vanilla_vector 대비 방향성 우위를 3/4 모델에서 확보, cost 역설 3/3 유지, '
    'GPT 에서 permutation p < 0.05 두 건 (Δ +18.3pp, +9.2pp) 확인. 복잡 시나리오에서 '
    '흥미로운 실패 모드 두 가지 (파라메트릭 마스킹, 라우팅 가드 갭) 를 발견하여 '
    '논문 Discussion 축으로 정리 완료. 두 번째 요구 (타 소프트웨어 대응) 는 '
    'QGIS 이식성 검증 결과 4개 touch-point 로 이식 가능성 확인.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 1. 실험 조건
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('1. 실험 조건', level=1)

add_table(doc,
    ['항목', '값'],
    [
        ('Bench tag', 'unified4 (최종)'),
        ('시나리오 수', '3 (survey_setup + 3d_visualization + attribute_computation)'),
        ('시나리오 복잡도', 'Low (4 steps) + Low (4 steps) + High (8 steps, 3 dialogs)'),
        ('모델', '4 (Gemini 2.5 Pro · Claude Sonnet 4.6 · GPT-4o · Qwen3-235B-Instruct)'),
        ('백엔드', '6 core (no_rag / vanilla_vector / graph_only / vision_only / full_system / state_path) + Gemini × long_context'),
        ('Replicates', '5 per (model, backend) cell'),
        ('총 스텝', '1,920 main + 240 longctx = 2,160'),
        ('채점', '결정적 keyword-based step_match (LLM judge 미사용)'),
        ('통계 단위', 'replicate (n=5), permutation p-value + Holm correction'),
        ('판정 프레임', '사전등록 A/B/C 프레임 (v2_pre_registration.md 참조)'),
        ('실행 시각', '2026-08-07 02:35 ~ 18:51 UTC (약 16h 대기 포함)'),
        ('Empty-response 감사', '0 / 2,160 (100% clean)'),
    ], col_widths=[3.5, 12.5]
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 2. 판정 결과 - A 조건 4개 대조
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('2. 판정 결과 — A (시스템 우위)', level=1)

doc.add_paragraph(
    '사전등록 A 조건 4개 (v2_pre_registration.md § 스토리 A) 대조:'
)

add_table(doc,
    ['조건', '기준', '실제', '판정'],
    [
        ('①', '3+/4 모델 방향 일관성 (step_accuracy full > vanilla)',
         '3/4 (Claude, GPT, Qwen 확증; Gemini 반전)', '✓'),
        ('②', '최소 1 모델 permutation p < 0.10',
         'GPT × 2 건: no_rag vs full p=0.032 (Δ+18.3pp), vanilla vs full p=0.034 (Δ+9.2pp)', '✓'),
        ('③', '3+/4 모델 방향 일관성 (faithfulness)',
         '3/4 (Claude, GPT, Qwen 확증; Gemini 동률)', '✓'),
        ('④', 'Cost 역설 유지 (API 유료 3 모델에서 full이 vanilla보다 저렴)',
         '3/3 확증 — Gemini 4.4× / Claude 2.6× / GPT 2.9× 저렴', '✓'),
    ], col_widths=[1, 5, 8, 1.5]
)

p = doc.add_paragraph()
p.add_run('결론: ').bold = True
p.add_run('A 조건 4개 모두 충족. 판정 A (시스템 우위) 확정.')

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 3. 핵심 수치 - macro (25-cell 요약)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('3. 핵심 수치 (Macro 평균, 3 시나리오)', level=1)

doc.add_paragraph(
    'Mean ± sample SD across 5 replicates per cell. 각 replicate 값은 3 시나리오 평균. '
    '전체 25-cell 표는 별첨 table1_full_sd_unified4.md 참조.'
)

add_table(doc,
    ['Model', 'Backend', 'Step Acc (%)', 'Faith (%)', 'Latency (s)', 'Cost/step'],
    [
        ('Gemini', 'no_rag',         '55.8±8.1', '100.0±0.0', '8.9±0.8',  '$0.75m'),
        ('Gemini', 'vanilla_vector', '75.0±...', '92.5±...',  '11.6±1.5', '$9.27m'),
        ('Gemini', 'full_system',    '72.5±...', '92.5±...',  '40±...',   '$2.13m (4.4×)'),
        ('Gemini', 'state_path',     '73.3±...', '96.7±...',  '36.6±1.8', '$1.09m'),
        ('Claude', 'vanilla_vector', '84.2±...', '75.8±...',  '4.3±0.4',  '$27.10m'),
        ('Claude', 'full_system',    '85.0±...', '77.5±...',  '30±...',   '$10.60m (2.6×)'),
        ('GPT',    'vanilla_vector', '60.0±...', '63.3±...',  '5.1±0.2',  '$17.93m'),
        ('GPT',    'full_system',    '69.2±...', '69.2±...',  '27±...',   '$6.08m (2.9×)'),
        ('GPT',    'state_path',     '76.7±...', '83.3±...',  '26.3±1.5', '$4.15m'),
        ('Qwen',   'vanilla_vector', '55.0±...', '38.3±...',  '9.6±0.9',  '$9.00m'),
        ('Qwen',   'full_system',    '56.7±...', '50.0±...',  '33±...',   '$30.4m'),
        ('Gemini', 'long_context',   '59.2±9.9', '79.2±...',  '13.9±1.5', '$315.56m (148×)'),
    ], col_widths=[2, 3, 2, 2, 2.5, 3]
)

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('주요 관찰: ').bold = True
p.add_run(
    '(1) Claude full_system 85% 최고 정확도. (2) Gemini cost 축 4.4× 압도적 우위. '
    '(3) long_context 는 Gemini full_system 대비 148× 비쌈에도 정확도 낮음 (59.2%). '
    '(4) Qwen 은 self-host 실효 비용이 높으나 파라미터 규모로 인한 특수 트레이드오프.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 4. 시나리오별 breakdown - 복잡도 vs 격차
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('4. 시나리오별 Breakdown (복잡도 vs 격차)', level=1)

doc.add_paragraph('교수님 요청 프레임: "복잡한 워크플로우에서 격차 변화" 확인.')

add_table(doc,
    ['시나리오', '복잡도', 'full Step Acc', 'vanilla Step Acc', 'Δ', 'full Faith', 'vanilla Faith', 'Δ'],
    [
        ('survey_setup',       'Low (4st)',  '78.8%', '75.6%', '+3.2', '80.0%', '77.5%', '+2.5'),
        ('3d_visualization',   'Low (4st)',  '75.0%', '85.0%', '−10.0', '75.0%', '85.0%', '−10.0'),
        ('attribute_computation','High (8st)', '58.8%', '55.6%', '+3.1', '70.0%', '72.5%', '−2.5'),
    ], col_widths=[3.5, 2, 2, 2, 1.2, 2, 2, 1.2]
)

doc.add_paragraph()

p = doc.add_paragraph()
p.add_run('사전등록 예측 대조 (attribute 시나리오, v2_pre_registration.md § attribute prediction):').bold = True

add_table(doc,
    ['예측 요소', '결과 (unified4)', '판정'],
    [
        ('Vanilla 는 §1.5.1a 절차 페이지 못 찾음', '0/15 hit (완전 미스)', '확증'),
        ('Full_system 은 workflow 라우팅으로 절차 청크 확보', '0% (unified3 47.5% 대비 완전 소멸)', '반증'),
        ('격차 확대 (full − vanilla Δ)', '−1.3pp (u3) → +3.1pp (u4), 양전환', '확증'),
        ('4/4 모델 방향 일관성', '2/4 확증 (Gemini +45pp / Claude +2.5pp)', '부분 확증'),
    ], col_widths=[6, 6.5, 2]
)

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('격차 양전환의 실제 메커니즘 (예측과 다름): ').bold = True
p.add_run(
    'Signature 재작성이 dry-run 8/8 통과했으나 실제 벤치의 vision-extracted state 노이즈로 '
    'seismic_attribute workflow 라우팅률 0%. 그럼에도 격차가 양전환한 실제 원인은 '
    '"잘못된 라우팅 회피 → fallback (vector-only) 로 방어". 즉 unified3 의 _04_configure '
    '과잉 흡수 (confidence 0.91 로 잘못된 문맥을 자신 있게 주입) 가 downstream 성능을 '
    '저하시키던 것을 unified4 에서 회피. 이 관측을 "When in doubt, don\'t route" 원칙으로 '
    '논문 Discussion 승격.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 5. 방향 일관성 + 통계 유의성
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('5. 방향 일관성 + 통계 유의성', level=1)

p = doc.add_paragraph()
p.add_run('macro 방향 일관성 (unified4)').bold = True
add_table(doc,
    ['Metric', 'Gemini', 'Claude', 'GPT', 'Qwen', 'A wins'],
    [
        ('step_accuracy full vs vanilla', 'B (72.5 vs 75.0)', 'A (85.0 vs 84.2)', 'A (69.2 vs 60.0)', 'A (56.7 vs 55.0)', '3/4'),
        ('faithfulness full vs vanilla',   '= (92.5 vs 92.5)', 'A (77.5 vs 75.8)', 'A (69.2 vs 63.3)', 'A (50.0 vs 38.3)', '3/4'),
        ('cost/step full vs vanilla (lower better)', 'A (2.13 vs 9.27)', 'A (10.60 vs 27.10)', 'A (6.08 vs 17.93)', '= (self-host)', '3/3 (API)'),
    ], col_widths=[4, 2.5, 2.5, 2.5, 2.5, 1.5]
)

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Pairwise 통계 (n=5 replicates, permutation p, 10K resamples)').bold = True
add_table(doc,
    ['Model', 'Contrast', 'Δ (pp)', 'perm p', '유의성'],
    [
        ('GPT', 'no_rag vs full_system',       '+18.3', '0.032', '✓ p<0.05'),
        ('GPT', 'vanilla_vector vs full_system','+9.2',  '0.034', '✓ p<0.05'),
        ('Qwen', '(unified3에서 step_acc full vs vanilla)', '+19.2', '0.025', '✓ p<0.05 (참고)'),
    ], col_widths=[2, 5, 2, 2, 3]
)

doc.add_paragraph(
    'n=5 small-sample 한계로 대부분 pairwise 는 non-sig. GPT 두 건이 유의성 조건 (사전등록 A 조건 ②) 을 충족.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 6. Fallback + Routing (새 관측)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('6. Fallback 활성화 & 라우팅 분포', level=1)

doc.add_paragraph('사전 예측: fallback 은 attribute step 2 (dry-run conf 0.75) 에서 처음 발동. 실제 관측:')

add_table(doc,
    ['Scenario', 'full_system fallback', '특기'],
    [
        ('survey_setup',        '3/80 (3.8%)', '낮음'),
        ('3d_visualization',    '11/80 (13.8%)', '중간, steps 1·2'),
        ('attribute_computation','65/160 (40.6%)', '높음, steps 0·3·4·6 (예측 step 2는 1건)'),
    ], col_widths=[4, 4, 6]
)

doc.add_paragraph()
p = doc.add_paragraph()
p.add_run('Attribute full_system 160 스텝의 3-layer 분포:').bold = True
add_table(doc,
    ['Destination', 'n', 'share', '통과율', '환각률'],
    [
        ('FALLBACK (vector-only, 명시적 안전판)', '65', '40.6%', '72.3%', '30.8%'),
        ('NONE (LLM rerank 후보 거절, 안전판 미발동)', '64', '40.0%', '39.1%', '21.9%'),
        ('d3_visualization (자신 있는 오라우팅, conf≥0.7)', '31', '19.4%', '71.0%', '3.2% (최저)'),
        ('seismic_attribute (target workflow)', '0', '0.0%', '—', '—'),
    ], col_widths=[6, 1.5, 2, 2, 2]
)

doc.add_paragraph(
    '"Fallback deadcode" 로 부록에 넣었던 P1 안전판이 실전에서 처음 40.6% 대량 발동하며 시스템 승부처로 승격.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 7. 발견한 실패 모드 3개 (Discussion 축)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('7. 발견한 실패 모드 3개 (논문 Discussion 축)', level=1)

doc.add_heading('7.1 파라메트릭 마스킹 (parametric masking)', level=2)
doc.add_paragraph(
    'Vanilla_vector 가 매뉴얼 §1.5.1a 를 0/15 hit 했음에도 attribute step_acc 60% 수준 유지. '
    '원인: 4 모델의 pretraining corpus 가 이미 OpendTect 문서를 포함 → 검색 실패해도 '
    '파라메트릭 지식으로 우회. 결과: hybrid 우위가 공개 매뉴얼 벤치에서 구조적으로 낮게 측정.'
)
p = doc.add_paragraph()
p.add_run('시험 상황 비유: ').italic = True
p.add_run(
    '오픈북(RAG) vs 클로즈드북(vanilla), 그러나 상대가 "시험 문제집을 통암기하고 온" 상황. '
    '오픈북의 이점이 압축됨.'
)
p = doc.add_paragraph()
p.add_run('논문 함의: ').bold = True
p.add_run(
    '본 연구 결과는 lower bound. 진짜 hybrid 우위 측정에는 사내 문서, 신기능 문서, '
    '저자원 언어 매뉴얼 같은 private-knowledge 조건 필요 (future work).'
)

doc.add_heading('7.2 라우팅 가드 갭 (Guard Hole)', level=2)
doc.add_paragraph(
    'Attribute full_system 160 스텝 중 40% 가 "NONE" 버킷 (통과율 39% — 최악). '
    'guide_pipeline.py:519-528 의 fallback 조건 "current_node_id and conf<threshold" 가 '
    'LLM 이 후보 다 거절한 케이스 (current_node_id=None) 를 잡지 못함. 실질 동작은 vector-only '
    '로 동일하나 라벨링이 slip through — 명확한 구현 갭.'
)
p = doc.add_paragraph()
p.add_run('논문 검증가능 예측 (future work): ').bold = True
p.add_run(
    'NONE 64 스텝을 명시적 fallback 로 처리하면 통과율이 FALLBACK bucket 72% 를 향해 이동. '
    'Macro 격차 최대 +1.1pp 추가 개선 여지. 정지 규칙에 따라 수리 안 함, 예측으로 남김. '
    '"발견했지만 재실행하지 않고 예측으로 남긴다" 자체가 방법론적 규율의 증명.'
)
p = doc.add_paragraph()
p.add_run('부수 발견: ').bold = True
p.add_run(
    'd3_visualization 오라우팅의 환각률 3.2% (최저) 는 우연이 아님. Attribute 스텝 5-7 '
    '(Tree 우클릭, 레이어 추가, 3D scene 표시) 이 d3_visualization workflow 의 절차 공간과 '
    '실제로 겹침. "라우터가 틀렸는데 운 좋음" 이 아니라 "라우터가 의미적으로 유효한 '
    '이웃 워크플로우를 찾음" — 워크플로우 경계는 사람이 그은 구획일 뿐, 절차 공간에서는 연속체.'
)

doc.add_heading('7.3 Dry-run vs Vision-extracted State 괴리', level=2)
doc.add_paragraph(
    'Signature 재작성이 hand-authored visual_state_gt 기반 dry-run 은 8/8 통과 (kickoff 게이트), '
    '벤치 실제 (vision-extracted state) 에서는 quoted phrase 못 맞춰 0/160. '
    'Dry-run 게이트는 signature 검증의 필요조건이지만 충분조건이 아님. '
    'Future work: vision-noise 시뮬레이션 기반 signature 검증 파이프라인.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 8. QGIS 이식성 (요구 2)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('8. QGIS 이식성 (요구 2)', level=1)

p = doc.add_paragraph()
p.add_run('결론: 매우 이식 가능. ').bold = True
p.add_run('상세는 qgis_portability_report.md.')

doc.add_heading('8.1 코드 결합 인벤토리', level=2)
add_table(doc,
    ['결합 유형', '파일 수', '대응 방식'],
    [
        ('프롬프트 내 "OpendTect" 하드코드', '1', '{software_name} 변수화'),
        ('UI 토큰 화이트리스트 (Inline/Crossline 등)', '1', '{software_id: [patterns]} dict 리팩터'),
        ('소프트웨어별 프론트엔드 리소스 (placeholder)', '2', 'software_id 조건부'),
        ('실질 total touch-point', '4', '설정 스와프 3 + 소규모 리팩터 1'),
    ], col_widths=[6, 2, 8]
)

doc.add_heading('8.2 스키마 이식성', level=2)
doc.add_paragraph('시나리오 JSON 스키마 변경 필요 없음 (100% 소프트웨어 중립).')
doc.add_paragraph('워크플로우 노드 스키마 변경 필요 없음.')
doc.add_paragraph('QGIS 용 콘텐츠만 신규 저작 (3-5 개 시나리오/워크플로우).')

doc.add_heading('8.3 이식 노력 추정', level=2)
add_table(doc,
    ['단계', '내용', '소요'],
    [
        ('A', '코드 리팩터 + software_id 도입', '1.0 인일'),
        ('B', 'QGIS 매뉴얼 인제스트 & QA', '0.5 인일'),
        ('C', 'QGIS 워크플로우 JSON (3-5 개)', '1.5 인일'),
        ('D', 'QGIS 시나리오 JSON (3-5 개)', '1.5 인일'),
        ('E', '스크린샷 캡처 및 검증', '1.5 인일'),
        ('F', '벤치 실행 & 표 재생성', '1.0 인일'),
        ('G', '여유', '1.0 인일'),
        ('총계', '', '~8 인일 (약 2주)'),
    ], col_widths=[1.5, 10, 4]
)

p = doc.add_paragraph()
p.add_run('단축 옵션 — QGIS 1 시나리오 pilot: ').bold = True
p.add_run('대표 1 시나리오만 저작 + 실행 (~2 일). 이식성의 존재 증명 목적. '
          '결과는 Discussion 부록에 "portability pilot" 로. 이번 논문 스코프에 포함 가능 여부 결정 요청.')

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 9. 감사 (결함/관측/정지규칙)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('9. 결함 · 관측 · 정지 규칙', level=1)

doc.add_heading('9.1 신규 결함 (unified4 사이클)', level=2)
add_table(doc,
    ['ID', '내용', '대응'],
    [
        ('결함 #11', 'survey_setup × state_path −7.5pp: signature 재작성의 기존 시나리오 부작용',
         '사전등록 원칙 "억지로 되돌리지 않고 결함 기록" 준수 (unified5 로 수정 안 함)'),
    ], col_widths=[2, 8, 6]
)

doc.add_heading('9.2 신규 관측', level=2)
add_table(doc,
    ['ID', '내용'],
    [
        ('관측 #1', '파라메트릭 마스킹 (§7.1)'),
        ('관측 #2', 'Dry-run vs vision-extracted state 괴리 (§7.3)'),
        ('관측 #3', 'When in doubt, don\'t route (§7.2)'),
    ], col_widths=[2, 14]
)

doc.add_heading('9.3 정지 규칙 (Stop Rule)', level=2)
p = doc.add_paragraph()
p.add_run('이 논문에서 unified5 는 없다. ').bold = True
p.add_run(
    'unified4 A 판정으로 논문 실험 매트릭스 최종 확정. '
    '결함·관측 3개는 정직히 기록하되 unified5 로 재실행하지 않는다. '
    '"발견했지만 사전등록된 정지 규칙에 따라 재실행하지 않고 예측으로 남긴다" 자체가 '
    '방법론적 규율의 증명이며, 리뷰어 방어의 근거가 된다.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 10. Discussion 챕터 구조 (예정)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('10. 논문 Discussion 챕터 구조 (예정)', level=1)

add_table(doc,
    ['챕터', '주제', '핵심 메시지'],
    [
        ('§Discussion 1',
         'A 판정 확증 (Confidence-gated Hybrid 재구성)',
         '"Confidence-gated hybrid는 vanilla보다 나빠지지 않으면서 조건이 맞으면 더 좋아진다." 게이트가 두 개, 그 사이의 갭까지 정직 공개.'),
        ('§Discussion 2',
         '파라메트릭 마스킹 (공개 SW 벤치의 lower bound)',
         'RAG 벤치의 방법론적 이슈. 본 결과는 conservative lower bound. Private-knowledge 조건 검증은 future work.'),
        ('§Discussion 3',
         '라우팅 가드 갭 + Dry-run 괴리 (검증 방법론)',
         '워크플로우 signature 튜닝의 검증 방법론 자체가 향후 연구 대상. Vision-noise 시뮬레이션 필요.'),
    ], col_widths=[3, 5, 8]
)

p = doc.add_paragraph()
p.add_run('중요 원칙: ').bold = True
p.add_run(
    '어느 챕터든 "seismic_attribute 라우팅 0%" 를 첫 문단에서 먼저 말하고 시작한다. '
    '숨길 수 없는 숫자는 저자가 먼저 말한다.'
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 11. 산출물 목록
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('11. 참조 산출물 (data/eval/results/)', level=1)

add_table(doc,
    ['파일', '용도'],
    [
        ('unified4_judgment_template.md', '최종 판정 보고서 (전문)'),
        ('final_report_to_professor.md', '교수님 최종 보고 문서'),
        ('table1_full_sd_unified4.md', '25-cell mean ± SD 표'),
        ('final_unified4_table.md', '4-model × 6-backend 표 (Goal Comp 각주 갱신)'),
        ('stats_audit_unified4.md, stats_unified4.md', '통계 감사 (permutation p)'),
        ('direction_unified4.md', '방향 일관성 표'),
        ('faithfulness_supplement_unified4.md', 'Faith 25-cell + direction reproduction'),
        ('per_scenario_unified4.md', '시나리오별 25-cell breakdown'),
        ('complexity_gap_unified4.md', 'Complexity vs gap widening'),
        ('routing_score_concentration_unified3.md', '검증 #2: routing×score 진단 (u3)'),
        ('discussion_draft_parametric_masking.md', '관측 #1 논문 초안'),
        ('qgis_portability_report.md', '이식성 상세 조사'),
        ('methodology_audit_trail.md', '결함·관측 감사 (관측 #2, #3, 결함 #11 신규)'),
        ('v2_pre_registration.md', '사전등록 문서 (unified4 predict + stop rule 등록)'),
    ], col_widths=[7, 9]
)

doc.add_paragraph()

# ═══════════════════════════════════════════════════════════════════
# 12. 다음 단계 (결정 요청)
# ═══════════════════════════════════════════════════════════════════
doc.add_heading('12. 다음 단계 (결정 요청)', level=1)

add_table(doc,
    ['옵션', '내용', '비고'],
    [
        ('A', 'Discussion 3 챕터 초안 작성 착수', '§10 구조 확정 후 진행'),
        ('B', 'QGIS 1 시나리오 pilot 실행 (이번 논문 포함)', '~2 인일 추가, 이식성 존재 증명'),
        ('C', '문서 정리 (stale narrative archive)', '병렬 진행 가능'),
    ], col_widths=[1.5, 10, 4.5]
)

# ═══════════════════════════════════════════════════════════════════
# Footer
# ═══════════════════════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph('─' * 80).alignment = WD_ALIGN_PARAGRAPH.CENTER
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
foot.add_run('GeoLens 실험 결과 종합 보고서 · unified4 최종 매트릭스\n').italic = True
foot.add_run(f'생성: {datetime.now().strftime("%Y-%m-%d %H:%M")} · 정지 규칙 준수 (unified5 없음)').italic = True

# Save
doc.save(OUT)
print(f'saved: {OUT}')
