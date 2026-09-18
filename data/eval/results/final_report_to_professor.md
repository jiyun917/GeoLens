# 최종 실험 결과 보고 (unified4)

**작성 시점**: 2026-08-10, unified4 벤치 + Phase B-5 집계 + 판정 완료 직후.
**전제 정지 규칙**: 이 논문에서 unified5 는 없다. 이 표가 논문 실험 매트릭스 최종.

## 헤드라인

교수님이 요구하신 **복잡 워크플로우 (8스텝 attribute)** 를 추가하여
**4모델 × 6백엔드 × 5replicates × 3시나리오 = 1,920 스텝** 전체 재평가한
결과, 제안 시스템이 사전등록 기준의 **시스템 우위 판정 (A)** 을
충족했습니다. 복잡 시나리오에서 흥미로운 실패 모드 두 가지 (**파라메트릭
마스킹**, **라우팅 가드 갭**) 를 발견하여 논문의 Discussion 3 챕터로
정리 중이며, 두 번째 요구 (타 소프트웨어) 는 **QGIS 1시나리오 이식성
검증** 으로 제안 드립니다 (조사 결과 4개 touch-point, 약 1인일).

## 1. 판정 결과 — A (시스템 우위)

**사전등록 A 조건 4개 모두 충족** (`v2_pre_registration.md § 스토리 A`):

| 조건 | 결과 |
|---|---|
| ① 3+/4 모델 방향 일관성 (step_accuracy full > vanilla) | ✓ 3/4 (Claude, GPT, Qwen) |
| ② 최소 1 모델 permutation p < 0.10 | ✓ GPT × 2 (p=0.032, 0.034) |
| ③ 3+/4 모델 방향 일관성 (faithfulness) | ✓ 3/4 (Claude, GPT, Qwen) |
| ④ Cost 역설 유지 (API 유료 3 모델) | ✓ 3/3 (Gemini 4.4×, Claude 2.6×, GPT 2.9× 저렴) |

**핵심 수치 (macro mean ± sample SD, n=5)**:

| Model | Backend | Step Acc (%) | Faith (%) | Cost/step |
|---|---|---|---|---|
| Gemini | full_system | 72.5 | 92.5 | **$2.13m (4.4× 저렴)** |
| Gemini | vanilla_vector | 75.0 | 92.5 | $9.27m |
| Claude | full_system | **85.0** | 77.5 | $10.60m |
| Claude | vanilla_vector | 84.2 | 75.8 | $27.10m |
| GPT | full_system | **69.2** | 69.2 | $6.08m |
| GPT | vanilla_vector | 60.0 | 63.3 | $17.93m |
| Qwen | full_system | 56.7 | 50.0 | $30.9m |
| Qwen | vanilla_vector | 55.0 | 38.3 | $9.00m |

## 2. 복잡 시나리오 (attribute) 결과

**사전등록 예측 vs 실제** (`v2_pre_registration.md § attribute prediction`):

| 예측 요소 | 결과 | 판정 |
|---|---|---|
| Vanilla 는 §1.5.1a 절차 페이지를 못 찾는다 | **0/15 hit** | 확증 |
| Full_system 은 workflow 라우팅으로 절차 청크 확보 | 47.5% (unified3), **0%** (unified4) | 반증 (unified4) |
| 격차가 기존 시나리오 대비 확대 | Δ = **-1.3pp (u3) → +3.1pp (u4)** | **양전환** |

**격차 양전환의 실제 메커니즘** (예측과 다름):
- Signature 재작성이 dry-run 8/8 통과했으나 vision-extracted state 노이즈로
  실제 벤치에서 `seismic_attribute` workflow 라우팅률 0%
- 그럼에도 격차 양전환 원인 = **잘못된 라우팅 회피 → fallback (vector-only)
  로 방어**
- 즉 unified3 의 `_04_configure` 과잉 흡수 (confidence 0.91 로 잘못된
  문맥을 자신 있게 주입) 가 downstream 성능을 저하시키던 것을 unified4
  에서 회피

이 관측을 **"When in doubt, don't route" 원칙** 으로 논문 Discussion 승격.

## 3. 발견한 실패 모드 두 가지 (논문 Discussion 축)

### 3.1 파라메트릭 마스킹 (parametric masking)

Vanilla 가 매뉴얼 §1.5.1a 를 0/15 hit 했음에도 attribute 시나리오 step_acc
가 60% 수준 유지. 원인: **4 모델의 사전학습 corpus 가 OpendTect 문서를
이미 포함**. 검색 실패해도 파라메트릭 지식으로 우회. 결과: hybrid 우위가
공개 매뉴얼 벤치에서 **구조적으로 낮게 측정** 됨.

**논문 함의**: unified4 결과는 lower bound. 진짜 hybrid 우위 측정에는
private-knowledge 조건 (사내 문서, 신기능, 저자원 언어 매뉴얼) 이 필요.

### 3.2 라우팅 가드 갭 (guarded hybrid 의 미해결 실패 모드)

Attribute full_system 160 스텝의 3-layer 분포:
- FALLBACK (vector-only, 명시적 안전판): 65 (40.6%) — **72.3% 통과**, 환각 30.8%
- **NONE (LLM rerank 가 후보 거절, 안전판 미발동)**: 64 (40.0%) — **39.1% 통과**, 환각 21.9%
- d3_visualization 자신 있는 오라우팅 (conf≥0.7): 31 (19.4%) — **71.0% 통과**, 환각 3.2% (최저)

**진단**: 코드 (`guide_pipeline.py:519-528`) 에서 fallback 은 `current_node_id
and confidence < CONFIDENCE_THRESHOLD` 조건. LLM 이 "후보 다 거절" 하면
`current_node_id=None` 이라 fallback 절 미진입 → 갭 발생. 실질적으로는
vector-only 를 받지만 안전판으로 라벨링 안 됨.

**검증가능 예측 (future work)**: NONE 64 스텝을 명시적 fallback 로 처리
하면 통과율이 72% 를 향해 이동. Macro 격차 최대 +1.1pp 추가 개선 여지.
**정지 규칙에 따라 수리 안 함, 예측으로 남김.**

**부수 발견**: d3_visualization 오라우팅의 환각률 3.2% (최저) 는 우연이
아님. Attribute 스텝 5-7 (Tree 우클릭, 레이어 추가, 3D scene 표시) 이
d3_visualization workflow 의 절차 공간과 **실제로 겹침**. "라우터가 틀렸
는데 운 좋음" 이 아니라 "**라우터가 의미적으로 유효한 이웃 워크플로우를
찾음**". 워크플로우 경계는 사람이 그은 구획일 뿐, 절차 공간에서는 연속체.

### 3.3 Dry-run vs vision-extracted state 괴리

Signature 재작성이 hand-authored `visual_state_gt` 기반 dry-run 은 8/8
통과 (kickoff 게이트), 벤치 실제 (vision-extracted state) 에서는 quoted
phrase 못 맞춰 0/160. **Dry-run 게이트는 필요조건이지만 충분조건이 아님**.
Future work: vision-noise 시뮬레이션 기반 signature 검증 파이프라인.

## 4. QGIS 이식성 (요구 2 답)

**결론**: **매우 이식 가능**. 상세는 `qgis_portability_report.md`.

### 4.1 코드 결합 조사 결과

| 유형 | 파일 수 | 대응 |
|---|---|---|
| 프롬프트 내 "OpendTect" 하드코드 | 1 | `{software_name}` 변수화 |
| UI 토큰 화이트리스트 (Inline/Crossline 등) | 1 | `{software_id: [patterns]}` dict 리팩터 |
| 소프트웨어별 프론트엔드 리소스 (placeholder) | 2 | software_id 조건부 |
| **총 실질 touch-point** | **4** | 설정 스와프 3 + 소규모 리팩터 1 |

### 4.2 스키마 이식성

- 시나리오 JSON 스키마 변경 필요 없음 (100% 소프트웨어 중립)
- 워크플로우 노드 스키마 변경 필요 없음
- QGIS 용은 JSON 콘텐츠만 새로 작성 (3-5 개 저작 필요)

### 4.3 이식 노력 추정

| 단계 | 소요 |
|---|---|
| A. 코드 리팩터 + software_id 도입 | 1.0 인일 |
| B. QGIS 매뉴얼 인제스트 & QA | 0.5 인일 |
| C. QGIS 워크플로우 JSON (3-5개) | 1.5 인일 |
| D. QGIS 시나리오 JSON (3-5개) | 1.5 인일 |
| E. 스크린샷 캡처 및 검증 | 1.5 인일 |
| F. 벤치 실행 & 표 재생성 | 1.0 인일 |
| G. 여유 | 1.0 인일 |
| **총** | **~8 인일 (약 2주)** |

**단축 옵션 — QGIS 1 시나리오 pilot**:
- 대표 1 시나리오만 저작 + 실행 (~1 인일 코어 + ~1 일 저작)
- 이식성의 존재 증명 목적. 결과는 Discussion 부록에 "portability pilot" 로.
- 이번 논문 스코프에 포함 가능 여부 논의 요청.

## 5. 결함 · 관측 · 정지 규칙

**신규 결함** (unified4 사이클):
- **결함 #11**: `survey_setup × state_path -7.5pp` — signature 재작성이 기존
  시나리오 state_path 백엔드에 부작용. 사전등록 원칙 "억지로 되돌리지 않고
  결함 기록" 준수.

**신규 관측**:
- **관측 #1**: 파라메트릭 마스킹 (§3.1)
- **관측 #2**: dry-run vs vision-extracted 괴리 (§3.3)
- **관측 #3**: When in doubt, don't route (§3.2)

**정지 규칙**: unified4 A 판정으로 이 논문 실험 매트릭스 최종 확정.
결함·관측 3개는 정직히 기록하되 unified5 로 재실행 안 함. "발견했지만
사전등록된 정지 규칙에 따라 재실행하지 않고 예측으로 남긴다" 자체가
방법론적 규율의 증명.

## 6. 다음 스텝 (교수님 결정 요청)

**A. Discussion 챕터 초안 작성** — 3 챕터 구조 확정 및 착수:
1. A 판정 확증 (confidence-gated hybrid 재구성)
2. 파라메트릭 마스킹 (공개 SW 벤치의 하한 상승 → lower bound 서술)
3. 라우팅 가드 갭 + dry-run 괴리 (워크플로우 검증 방법론)

**B. QGIS 1시나리오 pilot 승인 여부** — 이번 논문 스코프 포함 or 후속 트랙?

**C. 문서 정리 작업 병행** — stale narrative 갱신 (`FINAL_tables_and_prose.md`,
`v2_judgment_report.md` archive 등)

---

## 부록 A: 산출물 목록 (`data/eval/results/`)

| 파일 | 용도 |
|---|---|
| `unified4_judgment_template.md` | 최종 판정 보고서 (전문) |
| `table1_full_sd_unified4.md` | 25-cell mean ± SD 표 |
| `final_unified4_table.md` | 4-model × 6-backend 표 (Goal Comp 각주 갱신) |
| `stats_audit_unified4.md`, `stats_unified4.md` | 통계 감사 (permutation p) |
| `direction_unified4.md` | 방향 일관성 표 |
| `faithfulness_supplement_unified4.md` | Faith 25-cell + direction |
| `per_scenario_unified4.md`, `complexity_gap_unified4.md` | 시나리오별 breakdown |
| `discussion_draft_parametric_masking.md` | 관측 #1 논문 초안 |
| `qgis_portability_report.md` | 이식성 상세 조사 |
| `methodology_audit_trail.md` | 결함 · 관측 감사 (관측 #2, #3, 결함 #11 신규) |

## 부록 B: 실행 요약

- Bench 실행: 2026-08-07 02:35 ~ 18:51 UTC (약 16 시간, 대기 포함)
- 안전장치 발동 없음 (credit-depletion 조우 없음)
- Empty-response 0/2160 (main 1920 + longctx 240)
- Fallback 활성화: 3d_viz 13.8%, attribute 40.6% (실전 첫 대량 발동 관측)
- Qwen 서버 사전 probe HTTP 200 UP → 4 모델 전 매트릭스 정상 실행
