# QGIS Pilot 사전등록 문서 (P-4 벤치 실행 전)

**작성 시점**: 2026-08-13, P-3 캡처 완료 + validate 통과 직후, P-4 벤치
실행 **전**. 어떤 pilot 벤치 숫자도 보기 전.

**Pilot 태그**: `qgis_pilot` (unified4 매트릭스 동결 완전 분리, 별도 산출물)

**작성 목적**: unified4 사전등록 (`v2_pre_registration.md`) 과 동일 원칙 —
결과 관측 전 성공 기준 / 예측 / 정지 규칙을 못 박아 "숫자에 맞춰 해석이
휘는" 확증편향 차단.

---

## 1. Pilot 의 목적 (재확인)

**이식의 존재 증명 (existence proof)** — "4 개 touch-point 수정 + 정규
업로드 기능만으로 파이프라인이 새 소프트웨어에서 end-to-end 작동하고
벤치 지표가 산출된다."

**성능 우위 입증이 아님.** OpendTect 벤치의 hybrid 우위를 QGIS 에서도
확인하는 것은 pilot 스코프 밖. Pilot 이 답하는 질문은 오직: **"바뀐 SW 에서
전체 파이프라인이 돌아가고 숫자가 나오는가?"**

## 2. 성공 기준 (사전 고정)

### 2.1 Primary 성공 기준 (existence proof)

- ✅ **End-to-end 완주**: Gemini × {no_rag, vanilla_vector, full_system} × 5
  replicates × 1 시나리오 = **120 스텝 전량 empty=0 상태로 완료**
- ✅ **지표 산출**: step_accuracy · hallucination_rate · goal_completion_rate ·
  mean_latency_sec · mean_cost_usd 5 개 지표가 모든 (backend, replicate) 셀에
  실측값 반환
- ✅ **fallback 로그 무결**: fallback_activated 필드가 per_step 에 정상 기록
  (True/False 값), 값 자체는 관찰 대상 (다음 절 참조)

**Pass 조건**: 세 항목 모두 충족 → **pilot 성공 (이식성 증명)**.

**Fail 조건**: 
- Empty>0 발생 → 원인 진단 후 discard-and-rerun (unified2/3/4 선례)
- 지표 계산 불가 (예: latency/cost 필드 누락) → 채점 파이프라인 결함,
  audit 후 대응
- 파이프라인 크래시 → 즉시 정지, 원인 보고, 정지 규칙 적용 여부 판단

### 2.2 Secondary 관찰 (성공 기준 아님, 예측 항목)

성능 수치 자체는 pass/fail 판정 아님. 그러나 아래 예측을 결과 관측 전
명문화 (사후 재해석 방지):

#### 예측 A: 파라메트릭 마스킹 발현
> "vanilla_vector 는 QGIS 매뉴얼 §6.2.6 절차 청크를 확보 여부와 무관하게
> step_accuracy 40-70% 를 유지할 것. Gemini 2.5 Pro 의 사전학습에 QGIS
> Vector Analysis 튜토리얼이 이미 포함되어 있어 검색 실패 → 파라메트릭
> 지식 우회 경로가 활성화."

**확증 지표**:
- vanilla_vector step_accuracy ≥ 40% (파라메트릭 마스킹 하한 존재)
- vanilla_vector 의 retrieval 이 §6.2.6 절차 페이지 (pp212-218) 를 못 잡아도
  step_accuracy 는 유의미하게 하락하지 않음

**반증 지표**:
- vanilla_vector step_accuracy < 30% (파라메트릭 지식 부재)
- 그 경우 QGIS 는 파라메트릭 마스킹 조건에서 벗어난 지형 → OpendTect 대비
  hybrid 우위 측정이 오히려 유리할 것 (별건 후속 관찰)

#### 예측 B: Fallback 발동률 (라우팅 가드 갭 재현)
> "full_system 스텝의 fallback 발동률이 **30-50%** 사이에서 관측될 것.
> unified4 attribute 시나리오 40.6% 와 유사 패턴 — QGIS 시나리오는 신규
> workflow (hand-authored, 미성숙) 이라 vision-extracted state 와 signature
> 사이 quoted-phrase mismatch 예상."

**확증 지표**:
- full_system fallback rate 30-50% 범위
- 발동 스텝 분포가 특정 노드 (예: `_03_configure_buffer`) 에 편중되지 않고
  전 워크플로우에 분산

**반증 지표**:
- Fallback rate < 10% → signature 가 unified4 대비 훨씬 정밀 (관찰 가치)
- Fallback rate > 70% → signature 심각 부적합, 관문 (dry-run 8/8) 이
  bench-time 을 대변 못한 증거

#### 예측 C: "NONE" bucket (guard hole) 재현
> "attribute 시나리오에서 40% 였던 'NONE' bucket (LLM rerank 후보 거절,
> fallback 미발동, 실질 vector-only 지만 라벨링 slip through) 이 QGIS 에서도
> 관측될 것. unified4 관측 #2 의 vision-extracted state mismatch 가 신규
> workflow signature 에서 동일 재현 예상."

**확증 지표**: picked_workflow_id=None 이고 fallback_activated=False 인 스텝
비율 ≥ 20%

**반증 지표**: NONE bucket < 5% → 신규 workflow signature 가 unified4 대비
훨씬 정합 (예상 밖, 감사 기록 관찰).

## 3. 벤치 실행 스코프 (사전 고정)

### 3.1 매트릭스

- **Model**: Gemini 2.5 Pro (단독 — pilot 은 이식성 증명 목적, 4-model
  매트릭스는 스코프 밖)
- **Backends**: `no_rag`, `vanilla_vector`, `full_system` (3 개 — 파라메트릭
  마스킹 + hybrid 대비 관찰의 최소 세트)
- **Replicates**: 5 (unified4 와 동일)
- **Scenario**: `qgis__vector_buffer__01` (1 개, 8 steps)
- **총 스텝**: 3 backends × 5 rep × 8 steps = **120 스텝**

### 3.2 백엔드 격리 원칙 (Q2 옵션 A)

- **full_system, graph_only, state_path** (workflow-using) 은 `hint_workflow_id`
  prefix 로 QGIS workflows 만 검색 대상 (`qgis_vector_buffer` +
  `auto_bf2804feea57..._*`). OpendTect workflows (`survey_setup`, `d3_visualization`,
  `seismic_attribute`, `fault_interpretation`, `horizon_tracking`) 은 검색 대상
  에서 배제.
- **vanilla_vector, no_rag** 는 workflow 미사용 → 격리 불요.
- **manual_ids**: `[bf2804feea57434bb79b749134ed1df0]` (QGIS Training Manual
  단독) 만 벤치에 전달. OpendTect manual (`645b7cdf...`) 은 미포함.

### 3.3 채점기 · 시나리오 · workflow 동결

- 채점기 (`step_match`, `_get_completion_claim_patterns` QGIS 프로파일,
  hallucination scorer): 그대로
- 시나리오 JSON, workflow JSON, hand-authored signature: 그대로 (P-2 정제 #2
  이후 finalized)
- 사전등록 문구 (이 문서): 결과 관측 후 사후 변경 금지

## 4. 정지 규칙 (Stop Rule)

**이 pilot 에서 qgis_pilot2 는 없다.** Pilot 벤치가 어떤 결과든:
- Primary 성공 기준 (§2.1) 충족 → **pilot 성공, 논문 Discussion 에 이식성
  증명 사례로 기록**
- 성공 기준 미달 (empty>0, 지표 계산 불가, 크래시) → 원인 진단 후 **1회
  discard-and-rerun 만 허용**. 그 이후에도 미달 시 **pilot 실패 기록**, 논문
  Discussion 에 "이식 가능성 조건부 확인 + 미해결 실패 모드" 로 정직 서술

**정지 규칙 명문화 이유**:
1. Pilot 이 "이길 때까지 반복" 프레임 진입 방지
2. Unified4 stop rule 과 동일 규율 (미리 선언된 정지 규칙 = 방법론적 방어)
3. 이식성 증명의 신뢰도는 "얼마나 매끄럽게 됐는가" 가 아니라 "성공/실패
   판정 프레임이 미리 정의됐는가" 에 있음

## 5. Wrapper 및 안전장치 (재사용)

- **Wrapper**: `scripts/run_unified3_recovery.sh` 를 pilot 태그로 변경 (또는
  경량 신규 wrapper 작성)
- **안전장치**: credit-depletion aware probe (rc=4 즉시 abort), 60s 인터-
  replicate sleep, tail-100 depletion 사후 검사 → unified4 검증 로직 그대로
  재사용
- **Empty 감사**: `scripts/_check_empty.py` pilot 태그 지원 확인 후 실행

## 6. 감사 산출물 예정

- `data/eval/results/run_gemini_qgis_pilot_r{1..5}_*.json` — 벤치 raw
- `data/eval/results/qgis_pilot_bench.log` — wrapper log
- `data/eval/results/qgis_pilot_result_report.md` — 사후 판정 보고 (이 사전
  등록 대조 + Primary/Secondary 판정)
- `data/eval/results/methodology_audit_trail.md` § QGIS Pilot 감사 기록 (추가
  섹션)

## 7. 서명

이 문서는 P-4 pilot 벤치 실행 **전** 작성됨. 이후 결과가 어떻게 나오든 이
문서의 성공 기준 · 예측 · 정지 규칙을 그대로 적용해 판정. 판정 결과가 어느
쪽에 해당하는지는 벤치 산출물 (지표 + fallback 분포 + NONE bucket 분포) 을
이 문서 기준에 대조해 결정.
