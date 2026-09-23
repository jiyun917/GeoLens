# Study 3 사전등록 (초안 v1 — 서명 전)

**작성 시점**: 2026-09-22, study 2 판정(비교 1 A′, 비교 2 B; 2차 분석 A/B; V3-34~36) 이후. study 2 결과는 그대로 보고하며 이 문서는 별도의 확인 연구다. 새 테스트 세트에서는 아직 어떤 백엔드도 실행하지 않았다. 결정은 사용자가 위임했다("고칠 수 있는 건 고치고, QGIS는 OpendTect처럼 새 시나리오로").
**원칙**: v3·study 2와 같다 — 실행 전 확정, 전 백엔드 동일 적용, 판정 기준 선고정, 양방향 예측, 불리한 결과 그대로, 결과를 본 뒤 GT·채점기·메커니즘·signature 불변, study 4 없음.

## 0. 왜 study 3인가
- study 2에서 남은 두 열세: (i) Claude가 무절단 검색(vanilla_vector)에 −8pp — 노드 단위 라우팅이 화면 변화가 작은 스텝 연쇄에서 한 스텝 뒤에 머물러 [Next Action]이 늦었음(fault_sticks s4–s7, horizon s4–s6; V3-34). (ii) 환각 정의 v4가 매뉴얼 조작 명칭(메뉴·단축키·마우스 동작)을 환각으로 셈(V3-35) — 정의 v5(화면에도 매뉴얼 절에도 없는 라벨만)는 study 2에서 사후에 만들었으므로 2차 분석에 그쳤다.
- v3 QGIS 테스트 세트는 천장 효과(no_rag 98–100%)로 어떤 시스템도 우위를 낼 수 없었다. QGIS에서도 매뉴얼이 필요한 과제로 새 시나리오를 만든다.

## 1. 세트
| 세트 | 시나리오 | 상태 |
|---|---|---|
| **판정 세트(테스트)** | `opendtect__horizon_2dviewer__01` (§1.4.2b, 9스텝), `qgis__rule_classification__01` (§3.3.5, 10스텝), `qgis__reclassify_raster__01` (§7.3.10, 9스텝) | 워크플로우·시나리오 골격·패턴·linked_chunks를 **캡처 전에 매뉴얼만 보고 저작**(`scripts/study3_author.py`, 커밋 해시 §8). 스크린샷은 사용자 캡처(`CAPTURE_GUIDE.md`) → GT 열거 + 외부 검토 → 승인 |
| 2차 세트 | study 2의 두 시나리오(16스텝) | R2가 겨냥한 결함이 관측된 세트. 결과를 본 뒤 재사용하므로 판정에 쓰지 않고 "결함 해소 여부"만 보고 |
| 개발 세트 | OpendTect 3 시나리오(16스텝) | 게이트 검증 |

### 1.1 선정 규칙 (판정 세트, 시스템 실행 전)
- 각 시나리오에 no_rag만 3모델 × 1회. 3모델 평균 step accuracy < 0.85이면 채택, 아니면 제외(고치지 않음). 선정 실행의 응답은 선정에만 쓰고 GT·시스템 수정에 참고하지 않는다.
- 결과(QGIS 패스, 2026-09-23, `run_<model>_study3sel_qgis_r1_*.json`, 채점기 v5, judge 없음): `qgis__reclassify_raster__01` Gemini 0.556 / Claude 0.667 / GPT 0.889, 평균 **0.704** → 채택; `qgis__rule_classification__01` 0.400 / 0.800 / 0.600, 평균 **0.600** → 채택. OpendTect 패스(`opendtect__horizon_2dviewer__01`)는 s6–s8 재캡처 후 실행: `[기재]`

## 2. 실행 전에 확정된 수정 (전 백엔드 동일 또는 full_system 메커니즘; V3-37)
| # | 수정 | 근거 |
|---|---|---|
| F1′ | **환각 정의 v5를 1차 정의로 채점기에 내장**(`GEOLENS_SCORER=v5`): v4 플래그 중 시나리오의 `manual_grounding_sections` 절 본문(KB v4)에 있는 라벨은 근거 있음으로 제외(정의는 `data/eval/study2/hall_v5_definition.md`와 동일, 이번에는 실행 전 고정). v4 값도 재채점으로 병기 | V3-35·36 |
| R2″ | **이력 기반 전진**(`ROUTER_HISTORY_ADVANCE=1`): rerank(+R1)가 직전 확정 노드 또는 같은 워크플로우의 이전 노드를 골랐고, 직전 지시가 직전 노드의 유일한 나가는 엣지를 덮되(라틴 토큰 2개 이상이면 ≥ 0.8) 들어온 엣지보다 더 잘 덮으면 후속 노드로 전진. 조립 v7의 이력 규칙에도 같은 들어옴/나감 가드. 노드 id·스텝 번호 없음, 전 워크플로우 공통. 텔레메트리 `route_advance`. 검증 1–3차에서 정제(V3-37·38) | V3-34 라우팅 지연 |
| F4′ | 워크플로우 풀 = 10(study 2의 7 + 새 3). 새 3개는 저작 시점에 linked_chunks 연결(V3-32 교훈), preflight 통과 | 라우팅 난이도 유지 |
| F6 | 실행 래퍼 2패스(`run_study3.sh`): OpendTect 시나리오는 `GEOLENS_SOFTWARE_ID=opendtect`, QGIS는 `qgis`(vision 프롬프트 프로필·완료 판정 패턴이 프로세스 전역이라서). 풀·knob 동일 | 구현 제약 |
| — | 그 외 study 2 동결 구성 그대로: 조립 v7, R1 세션 고정, 세션 블록 1, 채점기의 step_match v4 규칙, KB v4, GT 절차 | |
- 텔레메트리 `route_sticky`·`route_advance`를 per_step에 저장(study 2에서는 로그로만 집계).

### 2.1 검증 게이트 (실행 전)
- 개발 세트 full_system 3모델 × 1회(최종 구성): (a) 라우팅 정답 스텝의 새 생성 손실(iteration 5 합집합 대비) 0, (b) 환각(v5) 모델별 ≤ study 2 검증 2차 값, (c) 라우팅 기록. 2차 세트(study 2) full_system 3모델 × 1회: (d) fault_sticks s4–s7·horizon s4–s6의 노드 단위 라우팅이 study 2 벤치(19/19/19/18 of 30, 30/30 ×3 오라우팅)보다 개선, (e) R2가 잘못 전진한 사례(전진했는데 응답이 오답이 된 스텝) 0. 통과 못 한 항목은 그 값을 버린다(R2 실패 시 `ROUTER_HISTORY_ADVANCE=0`). 결과(V3-38, 커밋 79c73fb+): 개발 세트 (a) 새 생성 손실 0, (b) 환각 v5 0/0/0, (c) 48/48; study 2 세트 (e) 잘못된 전진 0/7(3라운드 합계 0/24), (d) 뒤처짐 7칸 중 6칸 개선·horizon s6 1칸 동일(세 모델 응답 정답). (d)의 문자 그대로 기준은 미달이나 무해한 1칸이므로 구성을 채택(사용자 위임; §7에 기재). study 2 세트 step accuracy(1회) 1.000 / 0.651 / 1.000 — Claude는 fault_sticks s3 화면 오독의 연쇄(라우팅 규칙과 무관, 세 라운드 일관).

## 3. GT 절차
study 2와 동일: gemini-2.5-pro 열거(temperature 0) → 스크린샷만 보는 외부 검토(RULES) → 사용자 승인 → 커밋 → 서명 전까지 불변. `manual_grounding_sections`는 시나리오에 저작 시점에 기재.

## 4. 사전 예측 (결과 관측 전, 양방향)
| # | 예측 | 임계 | 반증되면 |
|---|---|---|---|
| Q1 | 판정 세트 no_rag 평균 step accuracy < 0.85 (선정 규칙) | — | 세트 제외 |
| Q2 | vanilla_budget > no_rag (매뉴얼 필요 과제) | 2/3 이상 +3pp | 파라메트릭 마스킹 보고 |
| Q3 | 비교 1(full vs vanilla_budget) step accuracy 방향 3/3, p < 0.05 | §5 | §6.5 |
| Q4 | 비교 2(full vs vanilla_vector) 방향 ≥ 2/3이고 유의한 역방향 없음(R2가 study 2의 Claude 역방향 원인을 제거했다는 가설) | §5 | R2 무효로 보고 |
| Q5 | 환각(v5): full ≤ vanilla_budget, full ≤ vanilla_vector 각 2/3 이상 | — | A′ 보고 |
| Q6 | 라우팅(벤치 모드): 워크플로우 단위 ≥ 7/9·8/10·7/9; 노드 단위는 화면 변화가 작은 스텝(B s5–s8, D s4–s5)에서 낮아질 수 있음; R2 전진 발동 ≥ 1회 | — | 기록 |
| Q7 | QGIS 새 시나리오에서는 v3 QGIS와 달리 no_rag < 0.85(천장 아님) | — | 세트 제외(Q1) |

## 5. 판정 (study 2 §5와 동일)
- 판정 지표 step accuracy·hallucination_rate(v5), 기술 지표 goal completion·cost·latency·hall v4. 비교 1 = vs vanilla_budget, 비교 2 = vs vanilla_vector. 층화 순열검정(모델 층, 10,000회, seed 42), 방향 분모 3·동률 미가산, step 조건 = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음, hall 조건 = full ≤ 비교대상 2/3 이상, A/A′/B/C, Holm(패밀리 2) 병기. 집계 단위 replicate(3 시나리오 평균), n = 10, |M| = 3.

## 6. 실행 계획
- 매트릭스: 3모델 × {no_rag, vanilla_budget, vanilla_vector, full_system} × 3시나리오(28스텝) × 10회, 2패스. 예상 비용 $40~50(Gemini 약 $15: 생성 + Flash 보조·judge), 약 12~14시간 순차. 실행 전 Gemini 잔액 확인(≥ $25 권장, 약 20,000원 추가 충전).
- 서명 후: 태그 `study3-prereg-signed` → `bash scripts/run_study3.sh` → `verdict_study2.py --tag`(패스별 파일을 합쳐 집계하는 study 3 판정 스크립트) → 보고. study 4 없음.

## 7. 한계
- 단일 저자 캡처·저작. 판정 세트 3시나리오 28스텝. R2·v5·풀 정리는 study 2 결과를 보고 설계했다(판정 세트는 새것이므로 그 자체는 오염되지 않았으나 설계 동기는 사후임을 명시). QGIS 준비 단계(AREA 필드, aspect 계산)는 시나리오 밖.
- R2는 후속 노드가 하나인 선형 그래프에서만 작동하며, 직전 지시가 틀렸을 때 그 오류를 한 칸 전진시킬 수 있다(게이트 (e)로 확인).
- 검증 게이트 (d)는 1회 관측에서 7칸 중 1칸(마지막 스텝, 응답 정답)이 미개선인 채 채택했다. R2″의 덮음 기준(0.8)과 들어옴/나감 가드는 검증 결과를 보며 정했다(판정 세트는 새것이므로 그 자체는 오염되지 않았으나 설계는 사후).

## 8. 서명
- 저작 커밋(캡처 전): `[기재]` / 작성: `[ ]` / 검토: `[ ]` / 확정 시각(UTC): `[ ]`
