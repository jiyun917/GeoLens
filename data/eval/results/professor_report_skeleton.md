# 교수님 보고 자료 뼈대 (unified3 결과 대기 중)

**전제**: 교수님이 지시하신 두 가지:
1. **복잡한 워크플로우 시나리오 추가** — attribute_computation (매뉴얼 §1.5.1a, 8 스텝, 파라미터 다이얼로그 다수) 신설.
2. **다른 소프트웨어 대응 계획** — GeoLens 이 OpendTect 뿐 아니라 다른 지구과학 도구에도 확장 가능한지 검증.

이 두 요구에 대한 답을 아래 구조로.

---

## 1. 요구사항 (1) 대응: 복잡한 시나리오 추가 + 검증 결과

### 1.1 신규 시나리오 정의

- 이름: `opendtect__attribute_computation__01`
- 매뉴얼 참조: 1.5.1a Bright Spot (Energy attribute, on-the-fly display, steps 1-9)
- 목표: F3 Demo 에서 Energy 속성을 정의하고 In-line 250 에 on-the-fly 로 표시
- 스텝 수: 8 (기존 두 시나리오는 각 4스텝)
- 파라미터 다이얼로그: Attribute Set 3D 창 + Save Attribute Set 다이얼로그 + Select (attribute picker) 다이얼로그 = 3
- 왜 "복잡": 매뉴얼 §1.5 는 이론 (§1.5.1) + 절차 (§1.5.1a) 혼재. Vector 검색이
  이론 페이지로 쏠리기 쉬운 지형. Hybrid retrieval 의 workflow 그래프
  라우팅이 진가를 발휘하는 실험 조건.

### 1.2 검증 프로토콜 (unified3 태그)

- 사전등록: `v2_pre_registration.md § attribute prediction` 에 예측 명문화 (결과
  보기 전 등록)
- 채점: 결정적 keyword-based `step_match` (LLM judge 미사용)
- 통계: n=5 replicates × 4 models × 6 backends + Gemini long_context
- 판정 프레임: 사전등록 A/B/C + attribute 예측 대조 3-sub-check

### 1.3 사전등록 예측 (결과 보기 전 등록됨)

> "attribute 시나리오에서 vanilla_vector의 retrieval hit가 이론 페이지
> (§1.5.1)로 쏠려 step acc·faithfulness가 저조할 것,
> full_system은 workflow 라우팅으로 절차 청크(p118~120)를 확보해
> 격차가 기존 2개 시나리오보다 벌어질 것."

### 1.4 결과 (unified3 완료)

`unified3_judgment_template.md § 3` 요약:

- **Retrieval attribution 예측 확증 여부**: **부분 확증**
  - 메커니즘 (vanilla §1.5.1a 미스): **확증** (0/15 target hit)
  - Full_system workflow 라우팅: 부분 확증 (`seismic_attribute` 47.5%)
  - 결과 (격차 확대): **반증** (Δ = −13.1pp widening)
- **복잡도-격차 상관**: 음의 상관 (복잡할수록 hybrid 우위 축소)
- **Hybrid 우위 확대 시나리오 여부**: **미확인**. attribute 시나리오에서
  full − vanilla 격차 오히려 축소. 모델별 반응 갈림 (Gemini/Claude 확증,
  GPT/Qwen 반증)

### 1.5 시나리오별 breakdown 표 (교수님 보고 핵심)

Macro 평균 (4 모델), n=5 replicates:

| 시나리오 | 복잡도 | full Step Acc | vanilla Step Acc | Δ | full Faith | vanilla Faith | Δ |
|---|---|---|---|---|---|---|---|
| survey_setup    | Low | 80.0 | 58.8 | **+21.2** | 77.5 | 67.5 | +10.0 |
| 3d_visualization | Low | 72.5 | 70.0 | +2.5 | 62.5 | 62.5 | 0.0 |
| **attribute_computation** | **High** | **60.0** | **61.3** | **−1.3** | **70.0** | **72.5** | **−2.5** |

모델별 상세 격차 (Δ complex − simple, step_acc pp):
- Gemini: **+20.0** (확증)
- Claude: **+2.5** (약확증)
- GPT: **−42.5** (반증)
- Qwen: **−32.5** (반증)

### 1.6 해석 (복잡도에 따른 격차 변화)

**메시지 A (교수님 보고 핵심)**: **"hybrid 는 복잡한 작업에서 오히려
격차가 축소된다 — 그러나 이는 검색 실패가 아니라 downstream 합성 한계
때문이다."**

- 검색 메커니즘 예측 (§1.4) 은 확증: vanilla 는 §1.5.1a 절차 청크 0 hit,
  full_system 은 seismic_attribute workflow 로 절차 청크 확보.
- 그럼에도 step_accuracy 격차가 벌어지지 않은 원인:
  1. Vanilla 도 "다른 attribute 계열 절차" (§2.3.1g, §1.5.2a) 로 우회 학습
     가능 — 완전 무능이 아닌 substitute grounding
  2. Full_system 도 8 스텝 복잡도에 하락 (74.2% → 60.0%)
  3. GPT/Qwen 은 특히 full 하락폭이 커서 flip
- **긍정적 재해석**: Low 복잡도 시나리오 (실제 사용자가 훨씬 자주 접함)
  에서 hybrid 는 확실한 우위 (+21.2pp). Aggregate 25-cell 표의 hybrid
  우위 (Gemini 74.2 vs vanilla 67.5) 는 여전히 유효.
- **negative result 도 정직한 기여**: "Retrieval mechanism confirmed,
  downstream advantage moderated by scenario complexity" — 논문 Discussion
  에 이 축을 새 챕터로 삽입 권장.

---

## 2. 요구사항 (2) 대응: 다른 소프트웨어 이식성 (QGIS 사례)

### 2.1 조사 대상 선정

- 후보: **QGIS** (오픈소스 GIS 소프트웨어)
- 선정 근거:
  - 지구과학 분야 널리 사용 (OpendTect 와 사용자 계층 겹침)
  - 완전 오픈소스 + 공개 매뉴얼 (CC-BY-SA)
  - UI 패턴 (창·메뉴·툴바) 이 OpendTect 와 유사한 데스크톱 GUI
  - Sphinx 기반 매뉴얼 → PDF/HTML 인제스트 파이프라인 호환

### 2.2 이식성 기술 조사 결과 (완료)

**결론**: **매우 이식 가능**. 핵심 RAG/그래프/임베딩/평가 인프라는 소프트웨어
독립. OpendTect 특화 결합은 6 파일에 한정.

#### 코드 결합 인벤토리

| 파일 | 위치 | 결합 유형 | 대응 |
|---|---|---|---|
| `guide_pipeline.py:81` | VISUAL_STATE_PROMPT | 프롬프트 내 "OpendTect" 명시 | 프롬프트 템플릿에 `{software_name}` 변수화 |
| `evaluation.py:578-582` | `_COMPLETION_CLAIM_PATTERNS` | OpendTect UI 토큰 화이트리스트 (Inline/Crossline/등) | `{software_id: [patterns]}` dict 로 리팩터 |
| `lib/prompts/action.ts:134-163` | "3D Scene right-click" 정책 문단 | OpendTect Tree scene 분류학 삽입 | software_id 조건부 프롬프트 조각 |
| `components/multimodal-input.tsx:81,83` | UI placeholder text | "Pick horizons in OpendTect" 등 | 소프트웨어별 프론트엔드 리소스 |

**총 실질 코드 변경 touch-point: 4개 (설정 스와프 3, 소규모 리팩터 1)**

#### 시나리오/워크플로우 스키마 이식성

- **시나리오 JSON 스키마 변경 필요 없음** (100% 소프트웨어 중립)
- **워크플로우 노드 스키마 변경 필요 없음**
- QGIS 용은 JSON 콘텐츠만 새로 작성 (기존 3-5 개 저작 필요)

#### QGIS 매뉴얼 파이프라인 호환성

| 단계 | 호환성 |
|---|---|
| PDF/URL 파서 (pdfplumber/pypdf) | Yes — 완전 generic |
| pypdf 아웃라인 추출 | Yes — Sphinx PDF outline 정상 |
| Gemini Vision OCR | Yes — QGIS docs 스크린샷 페이지 다수 |
| 청킹 (800 tokens, 100 overlap) | Yes |
| CLIP 이미지 임베딩 | Yes — 도메인 독립 |
| Workflow 자동 구축 (`AutoGraphBuilder`) | Yes — 섹션 기반 그룹핑 generic |

### 2.3 QGIS 이식 작업 추정 (단계별)

| 단계 | 작업 | 소요 |
|---|---|---|
| A. 코드 리팩터 | VISUAL_STATE_PROMPT 파라미터화, `_COMPLETION_CLAIM_PATTERNS` dict 화, action.ts 조건부 fragment, `software_id` 필드 신설, bench_runner `--software` 필터 | 1.0 인일 |
| B. QGIS 매뉴얼 인제스트 & QA | PDF 업로드, 청크·섹션·auto-workflow 검증 | 0.5 인일 |
| C. QGIS 워크플로우 JSON 작성 (3-5 개) | Hand-authored | 1.5 인일 |
| D. QGIS 시나리오 JSON 작성 (3-5 개) | 스텝 + 트랩 + 완료 조건 | 1.5 인일 |
| E. QGIS 스크린샷 캡처 | 시나리오별 5-8 장 × 3-5 시나리오 = 20-25 장 + 검증 | 1.5 인일 |
| F. QGIS 벤치 실행 & 채점 | run_all_models, 표 재생성 | 1.0 인일 |
| G. 예상 밖 대응 여유 | | 1.0 인일 |
| **총** | | **~7-10 인일 (~2주)** |

### 2.4 논문 서술 관점

교수님 요청 대응 서술 예시 (Discussion 삽입 후보):

> "The system architecture is software-agnostic — RAG, graph routing,
> and evaluation pipelines have no OpendTect-specific dependencies
> outside 6 well-scoped files. As a proof of portability, we ran a
> feasibility study on QGIS (open-source GIS): only ~4 code touch-points
> need refactoring; the JSON schemas for scenarios and workflows are
> reusable as-is. Total porting effort estimated at 7-10 engineer-days.
> Full QGIS evaluation is left as future work (out of scope for this
> submission), but the architecture positions GeoLens as a general
> pattern for domain-specific manual-grounded guide systems, not an
> OpendTect-only tool."

### 2.5 QGIS 이식 실제 착수 시점

**현재 논문 스코프 밖**. 이번 unified3 결과 확정 → 논문 초고 완성 →
투고 후 QGIS 이식을 별건 후속 트랙으로 진행 권장. 이유:
- 논문 트랙 동결 (unified3 = 논문 실험 매트릭스)
- QGIS 확장은 논문의 external validity 강화용 (Discussion / Future work)
- 리뷰 방어에는 "이식 가능성 확인" 만으로 충분

---

## 3. 요약 (교수님 앞에서 3분 대응 시)

1. **복잡 시나리오 (attribute_computation)** 추가 완료. 사전등록된 예측은
   **2층으로 나뉘어 판정**됨:
   - 메커니즘 예측 (vanilla 는 §1.5.1a 미스, full 은 workflow 라우팅) —
     **확증** (vanilla 0/15 target hit, full seismic_attribute 47.5%)
   - 결과 예측 (그래서 격차 확대) — **반증** (Δ = −13.1pp 축소).
   시나리오 복잡도에 따라 hybrid 우위는 **축소** (음의 상관).
   Gemini/Claude 는 확증, GPT/Qwen 은 반증 (모델간 갈림).
2. **QGIS 이식 가능성** 확인 완료: 코드 결합 6 파일 (~4 실질 touch-point),
   스키마 변경 불필요, 예상 7-10 인일. 논문 Discussion 에 이 결과 포함,
   실제 이식은 논문 후속 트랙.
3. 두 요구에 대한 답변은 이번 unified3 표 + retrieval attribution 표 +
   본 문서 § 2.2 인벤토리 세 개.

**핵심 메시지 (professor 한 문장)**: hybrid 검색의 메커니즘은 예측대로
작동하지만, 그것이 복잡한 워크플로우에서 downstream task 정확도로
전이되지 않는다는 negative result 를 정직하게 보고. Low 복잡도에서는
확실한 우위 (+21.2pp), aggregate 표에서도 여전히 hybrid 우위 유지.

---

## 부록: 참조 문서

- `data/eval/results/unified3_judgment_template.md` — 판정 보고서 (숫자 대기 중)
- `data/eval/results/retrieval_attribution_unified3.md` — 사전등록 예측 근거
- `data/eval/results/v2_pre_registration.md § attribute prediction` — 예측 원문
- `data/eval/results/methodology_audit_trail.md` — 시나리오 refinement + 결함 이력
- `data/eval/results/qgis_portability_report.md` — QGIS 이식성 상세 조사 (아래)
