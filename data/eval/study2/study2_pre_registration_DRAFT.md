# Study 2 사전등록 (초안 v1 — 서명 전)

**작성 시점**: 2026-09-21, v3 확인적 실행(비교 1 = B, 비교 2 = C; `verdict_v3.md`, V3-26) 이후. v3 결과는 그대로 보고하며 이 문서는 별도의 확인 연구다. 이 세트에서 어떤 시스템 백엔드도 아직 실행하지 않았다.
**원칙**: v3 사전등록과 같다 — 모든 수정은 실행 전에 확정, 전 백엔드 동일 적용, 판정 기준 선고정, 양방향 예측, 불리한 결과 그대로 보고, 결과를 본 뒤 GT·채점기·메커니즘·signature를 고치지 않음, study 3 없음.

## 0. 왜 새 세트인가 (v3의 교훈, V3-27)
- v3 테스트 세트(QGIS Buffer)는 no_rag가 100%(Gemini·Claude)·98.8%(GPT)로 천장에 붙어 검색·라우팅이 이길 자리가 없었다. 판정 B/C의 첫째 원인.
- 둘째 원인은 조립 v4의 다단계 노드 결함(GPT s3 10/10)과 채점 표기 두 건(말줄임표, 따옴표 목표 값). 셋 다 §2에서 실행 전에 고친다.
- 개발 세트(매뉴얼이 필요한 과제)에서는 full_system이 두 vanilla를 3/3 모델에서 앞섰다(+8.6~9.9pp, p = 0.0001; 판정에는 쓰지 않음).

## 1. 세트
| 세트 | 시나리오 | 상태 |
|---|---|---|
| 테스트 세트 후보 | `opendtect__horizon_autotrack__01` (매뉴얼 §1.4.2a, 7스텝), `opendtect__fault_sticks__01` (§1.4.3b, 9스텝) | 워크플로우·시나리오 골격·패턴은 **스크린샷 전에 매뉴얼만 보고 저작**(커밋 bdf8039). 스크린샷 16장(커밋 e1a745b). GT visible_elements는 vision 열거 + 외부 검토(진행 중) |
| 개발 세트 | v3와 같은 OpendTect 3 시나리오(16스텝) | §2 수정의 검증에만 사용 |

### 1.1 테스트 세트 선정 규칙 (시스템 실행 전, 이 규칙을 커밋한 뒤 실행)
- 각 후보 시나리오에 대해 **no_rag만** 3모델 × 1회 실행(채점기 v4, 최종 GT 초안의 패턴; visible_elements는 step accuracy에 영향 없음). 3모델 평균 step accuracy **< 0.85**이면 채택, 아니면 제외(고치지 않음). 두 후보 모두 제외되면 study 2는 여기서 멈추고 보고한다.
- 선정 실행의 응답은 선정에만 쓰고, 시스템·조립·signature·GT 수정에 참고하지 않는다.
- 결과(2026-09-21 04:15–04:20 UTC, 커밋 f18298b, 채점기 v4, judge 없음; 파일 `run_<model>_study2sel_r1_*.json`): `opendtect__fault_sticks__01` no_rag step accuracy Gemini 0.333 / Claude 0.444 / GPT 0.222, 평균 **0.333** → 채택; `opendtect__horizon_autotrack__01` Gemini 0.286 / Claude 0.286 / GPT 0.143, 평균 **0.238** → 채택. 두 시나리오 모두 채택(테스트 세트 = 2시나리오 16스텝). 실패 유형(기록만): 메뉴 경로(FaultStickSet > New, Save as, Display > Only at Sections, 3D Horizon > New > Auto and Manual Tracking), 탭·아이콘(Correlation 탭, Auto-Track 아이콘), Z-slice/Similarity 절차를 매뉴얼 없이 못 찾음. 이 응답은 시스템 수정에 참고하지 않는다.

## 2. 실행 전에 확정된 수정 (전 백엔드 동일; V3-28)
| # | 수정 | 근거 |
|---|---|---|
| F1 | 채점기 v4: 말줄임표 `…`→`...` 정규화; 목표 문장의 독립 숫자는 길이와 무관하게 환각 제외 | v3 QGIS s5 손실(Claude 29/30 등), Claude 환각 35%의 '50' |
| F2 | 컨텍스트 조립 v6: [Next Action] 아래 "순서대로, 화면에 결과가 없는 첫 동작만; 전부 끝났으면 완료" 규칙 한 줄 | GPT QGIS s3 10/10(복합 지시문의 마지막 절만 답함) |
| F3 | `RERANK_SESSION_BLOCK` = `[개발 세트 검증 후 결정: 0 또는 1]` | 생성기→라우팅 결합(V3-22) |
| F4 | 워크플로우 풀 = 9개(v3의 7개 + study 2의 2개). 방해 워크플로우 `horizon_tracking.json`·`fault_interpretation.json`(같은 주제의 generic 그래프)을 그대로 둠 | 라우팅 난이도 유지 |
- 그 외 v3 동결 구성(c01fdda)의 모든 knob·프롬프트·KB v4·GT 절차는 그대로.

### 2.1 개발 세트 검증 (실행 전 게이트)
- dry-run ×5(9개 풀): 라우팅 16/16 × 5. full_system 벤치 3모델 × 1회(v6, 채점기 v4, F3의 두 값 각각): 벤치 라우팅 64/64, iteration 5 대비 새 손실 0, 환각 증가 0. 통과하지 못한 항목은 그 값을 버리고 v3 동결 값으로 둔다(F2가 실패하면 v4 유지, F3가 실패하면 1 유지). 결과: `[검증 후 기재]`

## 3. GT 절차
- visible_elements: gemini-2.5-pro 열거(temperature 0, 고정 프롬프트, v3와 동일) → 스크린샷만 보는 외부 검토 세션(RULES.md: 오독 삭제·원문 정정, 표본 오독률 < 5%, 패턴·키워드는 손대지 않고 보류 목록) → 사용자 승인 → 커밋. 이후 서명 전까지 GT 불변.
- 화면이 같은 스텝 쌍(A s5/s6 Lock, B s3/s4 Only at Sections)은 세션 이력으로만 구별된다(`CAPTURE_NOTES.md`). loop_rate 집계에 잡힐 수 있으며 loop는 판정 지표가 아니다.

## 4. 사전 예측 (결과 관측 전, 양방향)
| # | 예측 | 임계 | 반증되면 |
|---|---|---|---|
| Q1 | 선정된 세트에서 no_rag 평균 step accuracy < 0.85 (선정 규칙과 동일) | — | 세트 제외 |
| Q2 | vanilla_budget > no_rag step accuracy (매뉴얼이 필요한 과제) | 3모델 중 2 이상 +3pp | 파라메트릭 마스킹 보고 |
| Q3 | 비교 1(full vs vanilla_budget) step accuracy 방향 ≥ 2/3 | §6.3 | §6.5 |
| Q4 | 비교 2(full vs vanilla_vector) 방향은 예측하지 않음(개발 세트 iteration 5에서 모델별로 달랐음) | — | 관측대로 보고 |
| Q5 | 환각률: full ≤ vanilla_budget 2/3 이상(채점기 v4) | — | A′ 보고 |
| Q6 | 라우팅(full_system, 벤치 모드): 워크플로우 단위 정답 ≥ 5/7·7/9, 노드 단위는 화면 동일 스텝(A s5/s6, B s3/s4)에서 낮아질 수 있음 | — | 기록 |
| Q7 | 위험: 다단계 노드(B 노드 03·07·08 없음 — study 2 워크플로우는 노드당 1스텝이 원칙이나 A s5/s6·B s3/s4는 같은 화면) | — | 기록 |

## 5. 판정 (v3 §6.3과 동일)
- 판정 지표 step accuracy·hallucination_rate(채점기 v4, 확정 GT), 기술 지표 goal completion·cost·latency.
- 비교 1 = full_system vs vanilla_budget, 비교 2 = full_system vs vanilla_vector. 층화 순열검정(모델 층, 10,000회, seed 42), 방향 분모 3·동률 미가산, step 조건 = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음, hall 조건 = full ≤ 비교대상 2/3 이상, A/A′/B/C, Holm(패밀리 2) 병기.
- 집계 단위 replicate(시나리오 평균), n = 10, |M| = 3, Qwen 제외.

## 6. 실행 계획
- 매트릭스: 3모델 × {no_rag, vanilla_budget, vanilla_vector, full_system} × 채택 시나리오 × 10회. long_context 없음. 예상 비용 $25~40, 약 3~4시간(순차).
- 래퍼 `scripts/run_study2.sh` `[작성 예정]`: v3 knob + `GEOLENS_SCORER=v4`, `CONTEXT_ASSEMBLY=v6`, `RERANK_SESSION_BLOCK=<F3>`, 시나리오 디렉터리 = 채택 시나리오만. 결과 JSON에 커밋 해시·knob 스냅샷.
- 서명 후: 태그 `study2-prereg-signed` → 실행 → 집계(verdict 스크립트 재사용) → 기계적 판정 → 보고. study 3 없음.

## 7. 한계 (명시)
- 단일 저자 캡처·저작(워크플로우·패턴은 매뉴얼에서, 스크린샷 전에). 테스트 세트 2시나리오 16스텝.
- 채점 패턴은 캡처 전 저작이라 화면과 어긋나는 스텝이 있을 수 있다(외부 검토의 보류 목록 참조; 결과를 본 뒤 고치지 않음).
- OpendTect 환경: dip-steering 라이선스 없음(DipSteer 탭 없음).

## 8. 서명
- 작성: `[ ]` / 검토: `[ ]` / 확정 시각(UTC): `[ ]`
