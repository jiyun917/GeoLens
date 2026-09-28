# Study 4 사전등록 (초안 v2 — 서명 전) — 최종 메커니즘의 개발 세트 재평가

**작성 시점**: 2026-09-28, study 3 판정(비교 1 A′, 비교 2 B; V3-42)·사후 진단(V3-43)·study 4 개발 검증(V3-44·45) 이후. 결정은 사용자가 위임했다("진짜 이번 테스트를 마지막으로 해서 모든 부분에서 조금이라도 geolens가 우위에 있을 수 있도록", "새로운 캡처 없이 현재 캡처 시나리오로 TEST 진행", "signature 결함 부분의 시나리오만 다른 걸로 변경").
**성격**: 이 연구의 판정 세트는 **이미 결과를 본 시나리오**(study 2 세트 2 + study 3 세트 3)이다. 이번 메커니즘 수정(R3·C8·G3·S6·R2‴)은 이 세트의 실패를 진단해 설계했고, 개발 검증도 이 세트에서 했다. 따라서 이 연구는 확인 연구가 아니라 **최종 메커니즘의 개발 세트(in-sample) 재평가**이며, study 3의 서명된 판정(A′/B)은 그대로 보고한다. 새 캡처에 의한 확인 실행은 별도로 열 수 있다(§7).
**원칙**: 실행 전 확정, 전 백엔드 동일 적용(생성기 프롬프트·채점기), 판정 기준 선고정(study 2·3 §5 그대로), 양방향 예측, 불리한 결과 그대로, 결과를 본 뒤 GT·채점기·메커니즘·signature 불변. 이 세트에서 결과를 본 뒤 다시 고쳐 재실행하지 않는다.

## 0. 왜 이 설계인가
- study 3 사후 진단: full_system 손실의 주원인은 라우터 지연(정답률 50~57%, 틀린 선택의 70~75%가 뒤처짐; 라우팅이 맞은 스텝의 정확도 0.92~0.94), 환각 플래그는 전부 키보드 키·창 컨트롤 어휘와 토크나이저 버그.
- 개발 검증(V3-45, 1회 실행, 6 시나리오): OpendTect 9칸 full_system 전부 1.000·환각 0; QGIS는 study 3에서 졌던 두 시나리오가 세 모델 모두 1.000. v3 천장 시나리오 vector_buffer만 v3식 signature 결함(설정 전 값 '50'이 도달 상태로 기재)으로 Gemini·GPT가 1스텝 열세 → 사용자 결정으로 판정 세트에서 제외.
- 새 캡처 세트(E/F/G, 캡처 지시서·초안 저작 완료)는 시간 제약으로 이번에 쓰지 않는다.

## 1. 세트
| 세트 | 시나리오 | 상태 |
|---|---|---|
| **판정 세트** (5, 44스텝) | `opendtect__fault_sticks__01` (§1.4.3b, 9), `opendtect__horizon_autotrack__01` (§1.4.2a, 7), `opendtect__horizon_2dviewer__01` (§1.4.2b, 9), `qgis__rule_classification__01` (§3.3.5, 10), `qgis__reclassify_raster__01` (§7.3.10, 9) | GT는 각 연구에서 서명 전 확정된 그대로(`data/eval/scenarios/.study4_test_opendtect`, `.study4_test_qgis` = study 2·3 확정본 복사, 바이트 동일). 워크플로우·signature도 study 3 실행 시 그대로 |
| 제외 | `qgis__vector_buffer__01` (v3 천장 세트) | signature 결함(§0); 게이트 참고용으로만 기록 |
| 미사용 | E/F/G 새 시나리오 초안 | 별도 확인 실행용 |

### 1.1 선정 규칙
- 각 연구의 선정 실행(no_rag ×1 ×3모델) 값을 그대로 쓴다(재실행 없음): fault_sticks 0.333, horizon_autotrack 0.238, horizon_2dviewer 0.778, rule_classification 0.600, reclassify_raster 0.704 — 모두 < 0.85 → 채택.

## 2. 실행 전에 확정된 메커니즘 (전 백엔드 동일 또는 full_system; V3-43~45; 커밋 e330836)
| # | 수정 | 근거 |
|---|---|---|
| R3 | **화면 증거 전진**(`ROUTER_SCREEN_ADVANCE=1`, hops 3): rerank(+R1·R2″)가 직전 확정 노드(또는 이전 노드·none)를 골랐을 때 단일 후속 사슬(≤ 3)을 현재 비전 출력과 대조 — (a) 후속 노드의 고유 `screenshot_keywords`가 지금 화면에 있고 직전 화면에는 없었으면(단일 토큰은 10자 이상 또는 숫자 포함일 때만; 말줄임된 화면 라벨은 접두사로 인정; 크롬·일반 어휘 제외) (b) 후속 노드의 expected dialog가 창 제목에 새로 나타났으면(가장 이른 노드에만 인정, 같은 대화상자의 뒤 노드는 그 턴에 토큰 증거 불인정) (c) 다른 증거가 없고 직전 노드의 대화상자가 제목에서 사라졌으며 다음 엣지가 그 대화상자를 벗어나면 한 칸 — 증거가 있는 가장 먼 후속 노드로 전진. 결정적, 노드 id 없음. 기록된 라우팅 결정 1,578건 재생: 지연 139건 교정·잘못된 이동 0. 텔레메트리 `route_screen_advance` | V3-43 (i) |
| P2 | 후보 풀에 직전 확정 노드의 2-hop 후속 포함(`ROUTER_PRIOR_HOPS=2`) | 정답 노드 풀 누락 |
| R2‴ | R2″ 덮음 기준 0.6 + **화면 가드**: 목표 노드의 특정 대화상자가 아직 제목에 없거나(G1), 직전 노드의 특정 대화상자가 아직 제목에 있고 목표 노드가 그 대화상자를 유지하지 않으면(G2) 전진하지 않음(메인 창 서술형 제목은 비특정으로 제외). 개발 검증 1차에서 GPT reclassify의 잘못된 전진 3건이 근거 | V3-45 |
| C8 | **조립 v8**(`CONTEXT_ASSEMBLY=v8`): 들어온 엣지 1개(0번) + 나가는 단일 후속 사슬 3개 엣지를 "동작 → 만들어지는 화면 상태"로 제시; 규칙 — 화면과 대조해 0번부터 결과가 안 보이는 첫 동작만 지시, 직전 지시의 결과가 화면에 없으면(화면이 그대로면) 그 지시를 반복, 묶음 지시는 첫 미완료 부분만, 정확히 한 동작; 종단이면 완료 센티널. v7 이력 규칙은 결과가 화면에 나타나지 않는 엣지에만 유지 | 라우팅 ±1~3 오차 흡수; 동일 화면 오전진 제거 |
| G3 | **생성기 프롬프트 v3**(`GEN_PROMPT_VERSION=v3`, 전 백엔드 동일): 화면·Reference Manual Context에 없는 단축키·수정자 키·메뉴 경로를 덧붙이지 않음 | V3-43 (ii) |
| S6 | **채점기 v6**(`GEOLENS_SCORER=v6`) = v5 + 토크나이저 수정(라틴 런에 붙은 여는 괄호 제거). 환각 정의는 v5 그대로 | V3-43 (ii) 버그 |
| — | 그 외 study 3 구성 그대로: R1, 세션 블록 1, step_match v4 규칙, KB v4, 풀 10(study 3과 동일), knob 스탬프에 R2″·R3 핀 추가 | |

### 2.1 검증 게이트 (실행 전; 개발 세트 6 시나리오 × 4 백엔드 × 3 모델 × 1회, `study4_verify_gate.py`)
- (a) step: full_system ≥ vanilla_vector 모델별(전체) 및 시나리오 ≥ 5/6; (b) hall(v6): full ≤ vanilla_vector·vanilla_budget 모델별; (c) 라우팅 정답률 ≥ 0.85, 잘못된 R3 전진 0; (d) vector_buffer full ≥ 0.95(참고).
- 결과(2026-09-28, 커밋 e330836, 파일 `run_<model>_study4ver_{opendtect,qgis}_r1_*.json`; Gemini·GPT QGIS 패스는 R2‴·v8 문장 수정 뒤 재실행분, 이전 분은 `study4ver_superseded/`): 전체 step_acc full/vv/vb — gemini 0.981/0.731/0.731, claude 1.000/0.846/0.769, gpt 0.981/0.808/0.731; hall v6 full/vv/vb — gemini 0.019/0.019/0.019, claude 0.019/0.038/0.019, gpt 0.019/0.019/0.019. 시나리오 18칸: full ≥ vv 17칸(동률 3칸: gemini 2dviewer 1.00/1.00, gemini·claude vector_buffer 1.00/1.00), 열세 1칸(gpt vector_buffer 0.88/1.00 — 제외 시나리오). 라우팅 136/156 = 0.872(fault_sticks 1.00, 2dviewer 0.81, autotrack 0.86, reclassify 0.93, rule 0.67, buffer 1.00); R3 발동 8, 교정 8, 잘못된 전진 0. **(a) PASS, (b) PASS, (c) PASS, (d) FAIL**(제외 시나리오; 판정 세트 5개에서는 15칸 모두 full ≥ vv, 동률 1칸). 게이트 통과로 구성 채택.

## 3. GT·KB 절차
- 캡처·GT·signature 모두 각 연구의 확정본 그대로. K1(캡처 후 signature 검증)은 새 캡처가 없으므로 이번에는 적용하지 않는다(새 세트 확인 실행 시 적용). 개발 워크플로우의 signature도 고치지 않는다(vector_buffer 제외로 갈음).

## 4. 사전 예측 (결과 관측 전, 양방향)
| # | 예측 | 임계 | 반증되면 |
|---|---|---|---|
| Q1 | vanilla_budget > no_rag (매뉴얼 필요 과제) | 2/3 이상 +3pp | 파라메트릭 마스킹 보고 |
| Q2 | 비교 1(full vs vanilla_budget) step accuracy 방향 3/3, p < 0.05 | §5 | 보고 |
| Q3 | 비교 2(full vs vanilla_vector) 방향 3/3, p < 0.05 | §5 | 지연 제거 실패로 보고 |
| Q4 | 환각(v6): full ≤ vanilla_budget, full ≤ vanilla_vector 각 3/3 | — | A′ 보고 |
| Q5 | 라우팅(벤치 모드) 노드 단위 정답률 ≥ 0.85; R3 잘못된 전진 ≤ 2% | — | 기록 |
| Q6 | 개발 검증(1회)의 만점 칸은 10회 평균에서도 ≥ 0.95 | — | 분산 보고 |

## 5. 판정 (study 2·3 §5와 동일)
- 판정 지표 step accuracy·hallucination_rate(v6), 기술 지표 goal completion·cost·latency·hall v5. 비교 1 = vs vanilla_budget, 비교 2 = vs vanilla_vector. 층화 순열검정(모델 층, 10,000회, seed 42), 방향 분모 3·동률 미가산, step 조건 = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음, hall 조건 = full ≤ 비교대상 2/3 이상, A/A′/B/C, Holm(패밀리 2) 병기. 집계 단위 replicate(5 시나리오 등가중 평균), n = 10, |M| = 3.

## 6. 실행 계획
- 매트릭스: 3모델 × {no_rag, vanilla_budget, vanilla_vector, full_system} × 5시나리오(44스텝) × 10회, 2패스(`run_study4.sh`: OpendTect 패스 태그 `study4_opendtect`, QGIS 패스 `study4_qgis`; 리터럴 핀·리터럴 preflight; 서명 태그 `study4-prereg-signed` 없으면 거부). **모델별 병렬 3프로세스**(v3 때 검토한 방식; 파일·로그 모델별 분리). 예상 비용 $50~55(Gemini ≈ $21), 약 13시간.
- 서명 후: 태그 → 3개 래퍼 병렬 → `scripts/verdict_study4.py` → 보고. 실행 중 코드·GT·워크플로우·사전등록 본문 불변; 장애 시 중단 replicate 폐기·재개(`START_REP`).

## 7. 한계
- **In-sample**: 판정 세트는 메커니즘 설계·검증에 쓰인 세트다. 결과는 "최종 메커니즘이 이 5개 과제에서 내는 성능"이지 새 과제로의 일반화 증거가 아니다. v3 → 2 → 3 → 4의 연속 시도이며, 사전등록 3의 "study 4 없음"은 사용자 지시로 번복(V3-43).
- 개발 검증은 1회 관측; 이번 실행은 그 구성을 10회 반복한다.
- 개발 검증 중 이탈: 크레딧 소진 2회(Gemini, Anthropic)로 중단·재개; 1차 규칙의 vector_buffer 오전진(60건, 오프라인 재생)으로 검증 1차 중단·재설계; GPT QGIS 실패로 R2‴ 가드·v8 규칙 문장 추가 후 QGIS 패스만 재실행(V3-45). 모두 판정 세트의 응답을 보고 고친 것임을 명시.
- 단일 저자 캡처. 그래픽 전이(seed 픽·추적)는 R3가 교정하지 못하고 R2‴·C8에 의존.

## 8. 서명
- 메커니즘 커밋: e330836 / GT: study 2 확정(커밋 §study2 prereg) · study 3 확정 c61a4ef 그대로 / 작성: `[ ]` / 검토: `[ ]` / 확정 시각(UTC): `[ ]`
