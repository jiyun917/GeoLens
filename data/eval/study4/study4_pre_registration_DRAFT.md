# Study 4 사전등록 (초안 v1 — 서명 전)

**작성 시점**: 2026-09-28, study 3 판정(비교 1 A′, 비교 2 B; V3-42) 이후, 사후 진단(V3-43, `data/eval/study3/posthoc_diagnosis.md`) 이후. study 3 결과는 그대로 보고하며 이 문서는 별도의 확인 연구다. 새 판정 세트에서는 아직 어떤 백엔드도 실행하지 않았고 스크린샷도 캡처 전이다. 결정은 사용자가 위임했다("진짜 이번 테스트를 마지막으로 해서 모든 부분에서 조금이라도 geolens가 우위에 있을 수 있도록 해줘").
**원칙**: v3·study 2·3과 같다 — 실행 전 확정, 전 백엔드 동일 적용(생성기 프롬프트·채점기), 판정 기준 선고정, 양방향 예측, 불리한 결과 그대로, 결과를 본 뒤 GT·채점기·메커니즘·signature 불변. **이 연구 뒤에 같은 목적의 study 5는 열지 않는다**(사전등록 3의 같은 진술을 사용자 지시로 한 번 뒤집었음을 §7에 기재).

## 0. 왜 study 4인가
- study 3(새 매뉴얼 의존 세트)에서 정확도는 vanilla_budget 대비 유의하게 앞섰으나(A′) vanilla_vector 대비는 방향 2/3·p 0.165(B), 환각(v5) 조건은 두 비교 모두 불성립. 사후 진단: (i) full_system 손실의 주원인은 **라우터 지연** — 라우팅 정답률 50~57%, 틀린 선택의 70~75%가 뒤처짐; 라우팅이 맞은 스텝의 정확도 0.92~0.94. rerank가 직전 노드에 고착, 후보 풀에 정답 노드 누락(2-hop), R2″ 발화 희소, v7 이력 규칙이 동일 화면에서 한 단계 앞서감. (ii) full_system 고유 환각 플래그는 전부 키보드 키·창 컨트롤 어휘(`Shift`, `F7`, `X(`)이며 `X(`·`Add Data (`는 채점기 토크나이저 버그.
- study 2·3에서 반복된 또 하나의 원인: **워크플로우가 매뉴얼 텍스트로만 저작되어 실제 화면 문자열과 어긋남**(매뉴얼 'Well correlation-Line' ↔ 실제 '19981104-1-04_0037', 'Seis' ↔ 'Seismic', 매뉴얼의 'Fixed table 대화상자' ↔ 이 QGIS 버전의 대화상자 내 패널, 'OpendTect Main Window' 같은 서술형 제목). 라우터는 이 문자열로 화면을 대조하므로 그 노드에서는 구조적으로 불리했다(사전등록 3 §7에 기재). 검증 세트에서는 이미 본 화면이라 드러나지 않고 새 세트에서만 드러나는 것이 "검증은 통과하고 본 테스트는 지는" 패턴의 원인이다.

## 1. 세트
| 세트 | 시나리오 | 상태 |
|---|---|---|
| **판정 세트(테스트)** | E `opendtect__spectral_decomp__01` (§1.5.2a, 9스텝), F `qgis__custom_projection__01` (§6.1.4, 9스텝), G `qgis__aspect_north__01` (§7.3.6, 6스텝) | 워크플로우·시나리오 골격·패턴을 **캡처 전에 매뉴얼만 보고 저작**(`scripts/study4_author.py`, 스테이징 `data/eval/study4/workflows_draft`·`scenarios_draft`; 커밋 해시 §8). 스크린샷은 사용자 캡처(`CAPTURE_GUIDE.md`, 24장) → §3 절차 |
| 개발 세트 | study 2 세트 2 + study 3 세트 3 + v3 QGIS 세트 1 (총 6 시나리오 52스텝; `.study4_dev_opendtect`, `.study4_dev_qgis`) | 결과를 본 세트이므로 판정에 쓰지 않고 게이트 검증에만 쓴다 |

### 1.1 선정 규칙 (판정 세트, 시스템 실행 전)
- 각 시나리오에 no_rag만 3모델 × 1회. 3모델 평균 step accuracy < 0.85이면 채택, 아니면 제외(고치지 않음). 선정 실행의 응답은 선정에만 쓰고 GT·시스템·signature 수정에 참고하지 않는다.
- 결과: `[기재]`

## 2. 실행 전에 확정된 수정 (전 백엔드 동일 또는 full_system 메커니즘; V3-43·V3-44)
| # | 수정 | 근거 |
|---|---|---|
| R3 | **화면 증거 전진**(`ROUTER_SCREEN_ADVANCE=1`, hops 3): rerank(+R1·R2″)가 직전 확정 노드(또는 같은 워크플로우의 이전 노드, 또는 none)를 골랐을 때 직전 노드의 단일 후속 사슬(≤ 3)을 현재 비전 출력과 대조 — (a) 후속 노드의 고유 `screenshot_keywords`가 지금 화면에 있고 직전 화면에는 없었으면(단일 토큰은 10자 이상 또는 숫자 포함일 때만; 말줄임된 화면 라벨은 접두사로 인정) (b) 후속 노드의 expected dialog가 창 제목에 새로 나타났으면(그 대화상자를 기대하는 가장 이른 노드에만 인정, 같은 대화상자의 뒤 노드는 그 턴에 토큰 증거 불인정) (c) 다른 증거가 없고 직전 노드의 대화상자가 제목에서 사라졌으며 다음 엣지가 그 대화상자를 벗어나면 한 칸 — 증거가 있는 가장 먼 후속 노드로 전진. 결정적, 노드 id 없음, 전 워크플로우 공통. 기록된 라우팅 결정 1,578건 재생: 지연 138건 교정·잘못된 이동 0. 텔레메트리 `route_screen_advance` | V3-43 (i) |
| P2 | 후보 풀에 직전 확정 노드의 2-hop 후속 포함(`ROUTER_PRIOR_HOPS=2`) | 정답 노드 풀 누락 |
| R2‴ | R2″ 덮음 기준 0.8 → 0.6(`ROUTER_ADVANCE_MIN_COVERAGE=0.6`, `_edge_covered`와 동일) | 발화 희소 |
| C8 | **조립 v8**(`CONTEXT_ASSEMBLY=v8`): 라우팅된 노드의 들어온 엣지 1개(0번)와 나가는 단일 후속 사슬 3개 엣지를 "동작 → 만들어지는 화면 상태(대화상자·상태 문자열)"로 순서대로 제시하고, 생성기가 **화면과 대조해** 결과가 이미 보이는 동작은 건너뛰고 아직 안 보이는 첫 동작만 지시하도록 규칙 부여(마지막 동작의 결과가 보이고 종단이면 완료 센티널). v7의 이력 규칙은 결과가 화면에 나타나지 않는 엣지(토글·잠금: 대상 노드가 현재 노드에 없는 signature 토큰을 갖지 않음)에만 남김 | 라우팅 ±1~3 오차 흡수; 동일 화면 오전진 제거 |
| G3 | **생성기 프롬프트 v3**(`GEN_PROMPT_VERSION=v3`, 전 백엔드 동일): "스크린샷에 보이거나 Reference Manual Context에 있는 컨트롤·메뉴·필드·키만 언급; 기억에서 단축키·수정자 키·메뉴 경로를 덧붙이지 않음" 한 줄 추가 | V3-43 (ii) — 메트릭 재정의 대신 메커니즘 |
| S6 | **채점기 v6**(`GEOLENS_SCORER=v6`) = v5 + 토크나이저 수정: 라틴 런에 붙은 여는 괄호(`X(`, `Add Data (`)를 라벨에서 제거. 환각 정의 자체는 v5 그대로 | V3-43 (ii) 버그 |
| K1 | **KB signature 검증**(§3): 캡처 후·모델 실행 전, 판정 세트 워크플로우의 expected_dialog·screenshot_keywords를 캡처 화면의 비전 문자열과 기계 대조해 **문자열만** 정정(창 제목·철자·데이터셋 이름). 노드·엣지 구조·edge instruction 불변, 모델 응답 미개입. 도구 `scripts/study4_verify_signatures.py`, 정정 목록은 §3에 기록 | V3-43, 사전등록 3 §7 |
| F4″ | 워크플로우 풀 = 13(study 3의 10 + 새 3). 새 3개는 편입 시 linked_chunks 연결(`relink_chunks_v4.py`), preflight 통과 | 라우팅 난이도 유지 |
| — | 그 외 study 3 동결 구성 그대로: R1 세션 고정, 세션 블록 1, step_match v4 규칙, KB v4, 2패스 래퍼(`run_study4.sh`), knob 스탬프에 R2″·R3 핀 추가(V3-41 결함 해소) | |

### 2.1 검증 게이트 (실행 전, 개발 세트 6 시나리오 × 4 백엔드 × 3 모델 × 1회, `scripts/study4_verify_gate.py`)
- (a) step: full_system ≥ vanilla_vector 모델별(전체) 및 시나리오 6개 중 5개 이상(모델별); (b) hall(v6): full_system ≤ vanilla_vector·vanilla_budget 모델별; (c) 라우팅 정답률(picked == expected) ≥ 0.85, 잘못된 R3 전진(전진 & 오라우팅 & 오답) 0; (d) 천장 시나리오(v3 vector_buffer) full_system ≥ 0.95 모델별. 통과 못 한 항목의 수정은 개발 세트에서만 반복하고, 판정 세트 캡처 화면·응답은 쓰지 않는다.
- 결과: `[기재]`

## 3. GT·KB 절차 (캡처 후, 모델 실행 전)
1. 캡처 검증(지시서 대조; 세션이 축소본으로 확인, 필요 시 재캡처).
2. **K1 signature 검증**: 스크린샷 → Flash 비전(v3 프롬프트, temperature 0) → `study4_verify_signatures.py` 표 → 문자열 정정(예: 대화상자 제목이 'Raster Analysis - Raster Calculator'면 그대로 반영; horizon 목록 이름이 매뉴얼과 다르면 실측 이름) → 결정 로그(`data/eval/study4/K1_signature_log.md`) → 워크플로우 편입·relink·커밋. 노드·엣지·edge instruction·시나리오 패턴은 이 단계에서 바꾸지 않는다(데이터셋 이름이 다른 경우의 시나리오 goal·keywords·patterns 정정은 study 3 H2 선례대로 GT 절차 4에서 별도 기록).
3. 결정적 라우팅 점검(생성기 없음): GT 노드 사슬을 teacher-forced로 두고 R3 증거 대조(`study4_route_replay.py` 방식) — 후속 노드의 증거가 전혀 없는 전이가 있으면 K1 정정이 부족한지 다시 본다(그래픽 전이는 예외로 기록).
4. GT: gemini-2.5-pro 열거(temperature 0) → 스크린샷만 보는 외부 검토(RULES) → 결정(위임) → 커밋 → 서명 전까지 불변. `manual_grounding_sections`는 저작 시점에 기재됨.
5. 선정 실행(§1.1) → 사전등록 최종화·서명 → 확인 실행.
- 수행 기록: `[기재]`

## 4. 사전 예측 (결과 관측 전, 양방향)
| # | 예측 | 임계 | 반증되면 |
|---|---|---|---|
| Q1 | 판정 세트 no_rag 평균 step accuracy < 0.85 (선정 규칙) | — | 세트 제외 |
| Q2 | vanilla_budget > no_rag (매뉴얼 필요 과제) | 2/3 이상 +3pp | 파라메트릭 마스킹 보고 |
| Q3 | 비교 1(full vs vanilla_budget) step accuracy 방향 3/3, p < 0.05 | §5 | §6 |
| Q4 | 비교 2(full vs vanilla_vector) 방향 3/3, p < 0.05 (R3·C8·K1이 라우팅 지연을 제거했다는 가설) | §5 | 지연 제거 실패로 보고 |
| Q5 | 환각(v6): full ≤ vanilla_budget, full ≤ vanilla_vector 각 3/3 (G3가 키 어휘 플래그를 없앤다는 가설) | — | A′ 보고 |
| Q6 | 라우팅(벤치 모드): 노드 단위 정답률 ≥ 0.85 (study 3: 0.50~0.57); R3 전진 발동 ≥ 5회/모델, 잘못된 전진 ≤ 2% | — | 기록 |
| Q7 | 새 시나리오 세 개 모두 no_rag < 0.85(천장 아님) | — | 세트 제외(Q1) |

## 5. 판정 (study 2·3 §5와 동일)
- 판정 지표 step accuracy·hallucination_rate(v6), 기술 지표 goal completion·cost·latency·hall v5. 비교 1 = vs vanilla_budget, 비교 2 = vs vanilla_vector. 층화 순열검정(모델 층, 10,000회, seed 42), 방향 분모 3·동률 미가산, step 조건 = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음, hall 조건 = full ≤ 비교대상 2/3 이상, A/A′/B/C, Holm(패밀리 2) 병기. 집계 단위 replicate(3 시나리오 평균), n = 10, |M| = 3.

## 6. 실행 계획
- 매트릭스: 3모델 × {no_rag, vanilla_budget, vanilla_vector, full_system} × 3시나리오(24스텝) × 10회, 2패스(`run_study4.sh`: OpendTect 패스 태그 `study4_opendtect`, QGIS 패스 `study4_qgis`; 핀은 리터럴 export + 리터럴 preflight 기대값; 서명 태그 `study4-prereg-signed` 없으면 거부). 예상 비용 $30~40(Gemini 약 $12), 약 12~15시간 순차.
- 서명 후: 태그 → `bash scripts/run_study4.sh` → `scripts/verdict_study4.py` → 보고. 실행 중 코드·GT·워크플로우·사전등록 본문 불변; 장애 시 중단 replicate 폐기·재개(`START_REP`).

## 7. 한계
- v3 → study 2 → 3 → 4의 연속 시도이며 사전등록 3의 "study 4 없음"을 사용자 지시로 뒤집었다(V3-43). 논문은 네 연구를 순서대로 모두 보고한다. R3·C8·G3·S6·K1은 study 2·3 결과를 보고 설계했다(판정 세트는 새것이므로 그 자체는 오염되지 않았으나 설계 동기는 사후).
- K1은 판정 세트의 캡처 화면을 KB signature 문자열 정정에 쓴다. 실제 배포에서 워크플로우 저자가 해당 소프트웨어 버전을 보고 만드는 것에 해당하며, 모델 응답은 개입하지 않지만 "테스트 화면을 본 KB"라는 점은 결과 해석에 남긴다.
- 단일 저자 캡처·저작. 판정 세트 3시나리오 24스텝. R3는 단일 후속 사슬에서만 작동하고 그래픽 전이(seed 픽·horizon 추적처럼 화면 문자열이 바뀌지 않는 전이)는 교정하지 못한다(C8이 흡수).
- 개발 세트 검증은 1회 관측이다.

## 8. 서명
- 저작 커밋(캡처 전): `[기재]` / K1 정정 커밋: `[기재]` / GT 확정 커밋: `[기재]` / 작성: `[ ]` / 검토: `[ ]` / 확정 시각(UTC): `[ ]`
