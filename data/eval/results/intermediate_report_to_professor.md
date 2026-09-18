# 중간 진행 상황 보고 (2026-08-07)

**전제**: 교수님의 두 요구 — (1) 복잡한 워크플로우 시나리오 추가,
(2) 다른 소프트웨어 이식 가능성 — 에 대한 답변은 실행 완료. 그러나
결과 확인 과정에서 흥미로운 시스템 결함이 드러났고, 이를 수리해서
최종 결과를 낼지 여부에 대한 중간 판단 요청.

## 1. 완료된 것

### 1.1 복잡한 시나리오 추가 (요구 1)

- `opendtect__attribute_computation__01` 신규 시나리오 (8 스텝, 매뉴얼
  §1.5.1a Bright Spot/Energy 속성, on-the-fly inline 표시 경로) 저작 완료
- 사전등록 예측 등록 완료 (결과 보기 전): "vanilla 는 이론 페이지 쏠림,
  full 은 workflow 라우팅으로 극복, 격차 확대 예상"
- **unified3 벤치 실행 완료**: 4 모델 × 6 백엔드 × 5 replicates × 3
  시나리오 = 1,920 스텝 + Gemini long_context 240 스텝. Empty-response
  카운트 0/2160 달성 (수 차례 discard-and-rerun 사이클 거쳐 검증)

### 1.2 이식 가능성 확인 (요구 2)

- **QGIS portability 조사 완료** (`qgis_portability_report.md`): 코드
  결합 6 파일 (~4 실질 touch-point), 시나리오·워크플로우 JSON 스키마
  변경 불필요. 예상 이식 노력 7-10 인일. 이번 논문은 조사 결과만
  Discussion 에 포함, 실제 이식은 후속 트랙 권장.

## 2. 흥미로운 발견 (결함 및 관측)

### 2.1 사전등록 예측의 2-층 판정

예측의 **메커니즘 부분** 은 확증:
- Vanilla 는 attribute 시나리오에서 목표 절차 페이지 §1.5.1a 를 **0/15
  hit** (완전 미스, §2.3.1g fault filter 나 §1.5.2a spectral 같은 다른
  attribute 계열로 검색 편향)
- Full_system 은 `seismic_attribute` workflow 로 47.5% 라우팅 (부분 확증)

그러나 예측의 **결과 부분** 은 반증:
- 격차 확대 예측이었으나 실제로는 **격차 축소** (Δ full − vanilla:
  기존 시나리오 평균 +11.9pp → attribute 시나리오 −1.3pp)
- 4 모델 중 Gemini/Claude 는 확증, GPT/Qwen 은 강한 반증

### 2.2 파라메트릭 마스킹 (parametric masking) 발견

축소의 원인을 규명한 결과:
- Vanilla 가 검색을 완전히 실패했음에도 성능이 유지된 것은 **모델의
  사전학습 파라메트릭 지식** 이 OpendTect 를 이미 알고 있어 잘못된
  검색을 우회하기 때문
- 시험 상황 비유: 오픈북(RAG) vs 클로즈드북(vanilla) 인데, 상대가
  **시험 문제집을 통암기하고 온** 상황. 오픈북 이점이 압축됨
- Full_system 의 오라우팅 스텝도 55/80/95% 통과 — 잘못된 문맥에서도
  모델이 채워 넣음

**논문 함의**: 공개 소프트웨어 매뉴얼 기반 RAG 벤치는 구조적으로 hybrid
우위를 낮게 측정한다는 일반적 방법론 이슈. 실제 사용 환경 (사내 문서,
신기능) 에서는 격차가 더 벌어질 것으로 예상. 이 관측은 `discussion_
draft_parametric_masking.md` 로 초안 완성 — unified4 결과와 무관하게
논문에 남길 finding.

### 2.3 Signature 과잉 흡수 결함

라우팅 실패 스텝 진단 (`routing_score_concentration_unified3.md`) 에서
**성공 라우팅이 오히려 더 못한** 역설 발견:
- `seismic_attribute` 로 "정답" 라우팅된 스텝: **48.7%** 통과
- 다른 workflow 로 오라우팅된 스텝: **73.1%** 통과 (성공보다 더 잘함)

원인: `_04_configure` 노드가 confidence 0.91 로 스텝 0-3 을 모두 흡수
하나, 스텝 1 (Attribute Set 3D 창 오픈) 은 자기 담당이 아닌데도 잡아채
5% 통과. "confidence 가 높은 것이 오히려 함정" 이라는 관찰.

## 3. 다음 스텝 (승인 요청)

두 갈래로 진행:

### 3.1 (독립) 파라메트릭 마스킹 관측은 지금 확정 기록

- audit trail 관측 #1 로 기록 완료
- Discussion 초안 문장 후보 완성
- 이건 unified4 결과와 무관하게 논문에 남음

### 3.2 Signature 수리 + unified4 재실행 (2-3 일 소요)

**사전등록**: unified4 예측을 결과 보기 전 등록 완료:
- 방향 예측: "attribute 시나리오 full − vanilla 격차 양전환"
- 크기는 열어둠 (회복 상한 +10.7pp 는 목표 아님, 참고값)
- **정지 규칙**: unified4 는 이 논문의 마지막 이터레이션. 결과가 어떻든
  unified5 는 없음. 성공 시 A 급 스토리, 실패 시 B 판정 + 마스킹 발견
  으로 마감

**작업 순서**:
1. `seismic_attribute` workflow signature 재작성 (오늘)
2. Routing dry-run 게이트 통과 확인: 기존 16/16 유지 + 신규 attribute
   8/8 통과. 두 조건 모두 만족해야 unified4 킥오프
3. 전 매트릭스 재실행 (unified4): 시그니처 변경은 지식 베이스 변경 =
   시스템 버전 변경. 4 모델 × 6 백엔드 × 5 rep × 3 시나리오 재실행
4. Phase B-5 집계 재실행
5. 기존 시나리오 비열화 확인 (unified3 대비 −5pp 이내)

**동결 원칙 재확인**: 채점기, 시나리오 JSON, 사전등록 예측 문구, 완료
스크린샷 — 전량 그대로. workflow signature 만 수정.

## 4. 판정 결과 (unified3 현재)

Pre-registered A/B/C 프레임 기준:
- **B (조건부 우위)**
  - ✓ step_acc full vs vanilla direction consistency 4/4
  - ✓ Qwen step_acc pairwise p = 0.025
  - ✓ Cost 역설 유지 (Gemini full $2.21m/step vs vanilla $9.27m/step)
  - ✗ Attribute 시나리오에서 격차 반전 (universal advantage 미달)

## 5. 교수님께 여쭙는 것

**Q1**: signature 수리 + unified4 재실행 계획 진행해도 되겠습니까?
(정지 규칙 사전등록 + 채점기 동결 + 사전 dry-run 게이트 조건부)

**Q2**: 파라메트릭 마스킹 발견을 Discussion 새 챕터로 부각시켜도
되겠습니까? 이 관측은 이 논문의 부산물이지만 RAG 벤치 방법론 자체에
대한 기여로 승격 가능.

**Q3**: 만약 unified4 도 격차 반전에 실패하면 B 판정 + 마스킹 발견
으로 이번 논문을 마감하고, QGIS 이식과 private-knowledge 벤치를 후속
트랙으로 잡는 방향에 동의하시는지?

---

**참조 산출물** (모두 `data/eval/results/` 아래):
- `unified3_judgment_template.md` — 판정 보고서 (숫자 채움 완료)
- `retrieval_attribution_unified3.md` — vanilla 0/15 hit 원자료
- `routing_score_concentration_unified3.md` — 과잉 흡수 진단
- `per_scenario_unified3.md`, `complexity_gap_unified3.md` — 시나리오별
  breakdown
- `discussion_draft_parametric_masking.md` — Discussion 초안
- `v2_pre_registration.md § unified4` — unified4 사전등록
- `methodology_audit_trail.md § 관측 #1, § 결함 #10` — 감사 기록
- `qgis_portability_report.md` — 이식 조사
