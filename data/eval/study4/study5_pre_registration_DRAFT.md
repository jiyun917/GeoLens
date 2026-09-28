# Study 5 사전등록 (최종안 — 서명 전) — 최종 메커니즘의 새 판정 세트 확인 연구

**작성 시점**: 2026-09-28, study 4(개발 세트 재평가, 실행 중; 사전등록 834d58b) 시작 이후, 새 세트 24장 캡처·GT 열거·K1 signature 검증·라우팅 dry-run 완료 후. **새 판정 세트에서 생성기는 아직 한 번도 실행되지 않았다**(선정 실행 §1.1 전). 결정은 사용자가 위임했다.
**성격**: study 4와 같은 최종 메커니즘(커밋 e330836 계열)을 **처음 보는 판정 세트**에서 확인하는 연구. 사용자 결정(2026-09-28): 이 연구에서 GeoLens가 우위를 얻지 못하면 study 4(개발 세트 재평가, `STUDY-대체`)를 주 결과로 쓴다. 이 문서의 판정은 그 결정과 무관하게 §5대로 기계적으로 낸다.
**원칙**: 실행 전 확정, 전 백엔드 동일 적용, 판정 기준 선고정(study 2·3·4 §5), 양방향 예측, 불리한 결과 그대로, 결과를 본 뒤 GT·채점기·메커니즘·signature 불변, 같은 목적의 재시도 없음.

## 0. 왜 이 세트인가
- 판정 세트 E/F/G는 study 3 사후 진단 뒤(2026-09-28) 매뉴얼만 보고 저작했고, 캡처는 사용자가 지시서대로 했다. 매뉴얼 의존 과제(Spectral Decomposition 파라미터, 사용자 정의 투영 WKT, Raster calculator 식)로 골랐다.
- 이전 세트에서 반복된 실패 원인(라우터 지연, signature와 화면 문자열 불일치)에 대해 메커니즘(R3·R2‴·C8·G3·S6)과 절차(K1)를 마련했고, 이 세트는 그 절차를 처음부터 적용한 첫 세트다.

## 1. 세트
| 세트 | 시나리오 | 상태 |
|---|---|---|
| **판정 세트** (3, 24스텝) | E `opendtect__spectral_decomp__01` (§1.5.2a, 9), F `qgis__custom_projection__01` (§6.1.4, 9), G `qgis__aspect_north__01` (§7.3.6, 6) | 워크플로우·시나리오 골격·패턴은 캡처 전 저작(`scripts/study4_author.py`, 커밋 9ba5b23); 캡처 24장(원본 PNG `data/eval/study4/originals_png/`, 벤치 JPEG quality 85 — §3); GT는 §3 절차 |
| 개발 세트 | study 2·3 세트 5 + v3 QGIS 1 | study 4 게이트(V3-45)에서 검증됨; 이 연구에서는 재실행하지 않음 |

### 1.1 선정 규칙 (판정 세트, 시스템 실행 전)
- 각 시나리오에 no_rag만 3모델 × 1회. 3모델 평균 step accuracy < 0.85이면 채택, 아니면 제외(고치지 않음). 선정 실행의 응답은 선정에만 쓰고 GT·시스템·signature 수정에 참고하지 않는다.
- 결과(2026-09-28 11:10–11:17Z, `run_<model>_study5sel_{opendtect,qgis}_r1_*.json`, 채점기 v6, judge 없음, 스테이징 풀): E `opendtect__spectral_decomp__01` claude 0.778 ✓✓✓✗✓✓✓✗✓ / gemini 0.556 ✓✓✓✗✗✓✓✗✗ / gpt 0.667 ✓✓✓✗✗✓✓✓✗, 평균 **0.667** → 채택; G `qgis__aspect_north__01` 0.833 / 0.833 / 0.833, 평균 **0.833** → 채택; F `qgis__custom_projection__01` claude 0.889 / gemini 1.000 / gpt 0.556, 평균 **0.815** → 채택(규칙상 채택이나 Gemini·Claude no_rag가 천장에 가까움 — §7).

## 2. 실행 전에 확정된 메커니즘 (study 4 사전등록 §2와 동일; 커밋 e330836 계열)
| # | 수정 | 근거 |
|---|---|---|
| R3 | 화면 증거 전진(`ROUTER_SCREEN_ADVANCE=1`, hops 3; 키워드 증거·대화상자 출현/소멸·말줄임 접두사·크롬 어휘 제외) | V3-43 |
| P2 | 2-hop 후속 후보 풀(`ROUTER_PRIOR_HOPS=2`) | |
| R2‴ | 이력 전진 덮음 0.6 + 화면 가드 G1/G2 | V3-45 |
| C8 | 조립 v8(뒤 1·앞 3 엣지, 화면 판단, 반복·묶음·한 동작 규칙) | |
| G3 | 생성기 프롬프트 v3(단축키·메뉴 경로 금지, 전 백엔드) | |
| S6 | 채점기 v6(토크나이저 수정) | |
| K1 | **KB signature 검증**(§3): 캡처 후 비전 문자열과 대조해 문자열만 정정 — 수행 완료, 로그 `data/eval/study4/K1_signature_log.md` | |
| F4‴ | 워크플로우 풀 = 13(study 4의 10 + 새 3, linked_chunks 연결 완료 `relink_chunks_v4.py --manual study4_ot/study4_qgis --dir`). 실행 전 풀 편입(본 실행 종료 후) | 라우팅 난이도 유지 |
| J85 | 벤치 JPEG quality 85(§3; 균일 적용) | 비전 모델의 이미지 특이 반복 루프 회피 |
| — | 그 외 study 4 구성 그대로(R1, 세션 블록 1, step_match v4, KB v4, 2패스 병렬 래퍼 `run_study4.sh`를 태그 `study5`로) | |

### 2.1 게이트
- 개발 세트 게이트는 study 4 사전등록 §2.1의 결과(V3-45)를 그대로 인용한다((a)(b)(c) PASS). 이 세트에 대해서는 §3의 K1·dry-run 기준만 적용한다.

## 3. GT·KB 절차 (캡처 후, 모델 실행 전) — 수행 기록
1. **캡처 검증**: 24장 지시서 대조(세션, 축소본·확대본 열람). 재캡처 없음. 버전 차이는 캡처자 노트(`CAPTURE_NOTES.md`): 'Select Horizons'(7.0.9), 'Positions', 'Select RGB Attributes' 창 통과, Input Data 자동 채움, QGIS 3.44 'Input layers'·'1 input selected'·따옴표 식 등.
2. **벤치 JPEG**: quality 92로 변환한 `qgis__custom_projection__01/step_0.jpg`에서 Flash 비전이 반복 생성 루프(504/2,990토큰 잘못된 JSON)에 빠져 24장 모두 quality 85로 재인코딩(원본 PNG 불변, 화면 내용 동일). 비전 캐시 24/24 정상. 이 결정은 모델 실행 전이며 전 백엔드 공통(비전은 full_system만 쓰므로 실질 영향은 full_system의 라우팅 입력).
3. **K1 signature 검증·정정**(`study4_verify_signatures.py` → `study4_apply_k1.py`, 로그 `K1_signature_log.md`): E 노드 02 dialog 'Select Horizons / Select Input Horizon(s)', 03 'Positions / Position', 04 키워드 `<right-click>`·`Z values`, 05 'Similarity'; G 노드 02·04 'Input layers'·'0/1 input(s) selected', 03 따옴표 식·'Expression is valid' 제거; F 노드 08 'User-defined'. 정정 후 대화상자 24/24 일치, 키워드 122/129 화면 존재(나머지 7개는 매뉴얼 이름 별칭 유지). 노드·엣지·edge instruction 불변.
4. **라우팅 dry-run**(생성기 없음, `study4_route_dryrun.py`, 스테이징 풀 13): chained 23/24 = 0.958, teacher 23/24 = 0.958(≥ 0.85). 유일한 불일치는 E s0(빈 scene 시작 화면에서 다른 워크플로우의 시작 노드 선택; 세션 이력 없는 첫 스텝의 동점 화면). 정정하지 않음.
5. **GT**: gemini-2.5-pro 열거(temperature 0, `gt_enumerate_study2.py --dir study4`, 24장, $0.80) → 초안(`gt_apply_study4.py`: 열거 라벨 전부 + 세션의 화면 사실) → 스크린샷만 보는 외부 검토(RULES, 표본 오독률 5% 중단 규칙) → 결정(위임, H-항목) → 확정 → 서명 전까지 불변. H4: G s2 패턴에 'Input layers?' 별칭 추가(매뉴얼 'Reference layer(s)' 병기); H5: E initial_state에 버전 사실 기재. 수행 기록: 외부 검토(별도 에이전트, 폴더 밖 미열람) 표본 오독률 1.34%(6/449; 공백 차이 제외 0.89%) < 5%; 1,498항목 검수, 삭제 1·정정 32·추가 36, data_state 정정 6스텝, current_dialog·current_action 변경 없음. 결정(위임): B-1 QGIS 소수점 마침표(검토자 픽셀 비교) 수용; H6 F s6 패턴에 'User[- ]?Defined' 별칭(3.44 그룹 라벨 'User-defined'); 나머지 보류 항목은 검토자 표기 유지. 확정 GT `data/eval/scenarios/.study5_test_opendtect/`, `.study5_test_qgis/`(+ `data/eval/scenarios/` 사본), 로그 `data/eval/study4/GT5_final_applied_log.md`(H6 패턴의 셸 이스케이프 손상 1건을 스크립트로 복구·검증한 기록 포함).
6. 선정 실행(§1.1) → 최종화·서명 → 본 실행.

## 4. 사전 예측 (결과 관측 전, 양방향)
| # | 예측 | 임계 | 반증되면 |
|---|---|---|---|
| Q1 | 판정 세트 no_rag 평균 step accuracy < 0.85 (선정 규칙) | — | 세트 제외 |
| Q2 | vanilla_budget > no_rag (매뉴얼 필요 과제) | 2/3 이상 +3pp | 파라메트릭 마스킹 보고 |
| Q3 | 비교 1(full vs vanilla_budget) 방향 3/3, p < 0.05 | §5 | 보고 |
| Q4 | 비교 2(full vs vanilla_vector) 방향 3/3, p < 0.05 | §5 | 지연·K1 부족으로 보고 |
| Q5 | 환각(v6): full ≤ vanilla_budget, full ≤ vanilla_vector 각 3/3 | — | A′ 보고 |
| Q6 | 라우팅(벤치 모드) 노드 단위 정답률 ≥ 0.85(dry-run 0.958); R3 잘못된 전진 ≤ 2% | — | 기록 |
| Q7 | F s4(WKT 입력)에서 no_rag는 PROJCRS 문자열을 내지 못하고 RAG 백엔드는 낸다 | — | 기록 |

## 5. 판정 (study 2·3·4 §5와 동일)
- 판정 지표 step accuracy·hallucination_rate(v6), 기술 지표 goal completion·cost·latency·hall v5. 비교 1 = vs vanilla_budget, 비교 2 = vs vanilla_vector. 층화 순열검정(모델 층, 10,000회, seed 42), 방향 분모 3·동률 미가산, step 조건 = 방향 ≥ 2/3 & raw p < 0.05 & 유의한 역방향 없음, hall 조건 = full ≤ 비교대상 2/3 이상, A/A′/B/C, Holm(패밀리 2) 병기. 집계 단위 replicate(3 시나리오 등가중 평균), n = 10, |M| = 3.

## 6. 실행 계획
- 매트릭스: 3모델 × {no_rag, vanilla_budget, vanilla_vector, full_system} × 3시나리오(24스텝) × 10회, 2패스(`TAG=study5 bash scripts/run_study4.sh` 변형 `run_study5.sh`: OpendTect 패스 태그 `study5_opendtect`, QGIS 패스 `study5_qgis`; 리터럴 핀·preflight; 서명 태그 `study5-prereg-signed` 없으면 거부), 모델별 병렬 3프로세스. 예상 비용 $30(Gemini ≈ $12, Claude ≈ $11, GPT ≈ $7), 약 7시간. **study 4 본 실행이 끝난 뒤 잔액 확인 후 시작**(사용자 결정).
- 판정 `scripts/verdict_study5.py`(태그만 다른 사본). 실행 중 코드·GT·워크플로우·사전등록 본문 불변; 장애 시 중단 replicate 폐기·재개.

## 7. 한계
- 단일 저자 캡처·저작. 3 시나리오 24스텝. K1은 판정 세트의 캡처 화면을 KB 문자열 정정에 썼다(모델 응답 미개입; "테스트 화면을 본 KB"). 라우팅 dry-run은 Flash rerank를 판정 세트 화면에 돌린 것이다(생성기 없음; 결과로 signature를 더 고치지는 않았음).
- E는 매뉴얼의 Amplitude Spectrum 확인 단계와 horizon output 단계를 생략한 부분 과제. F의 WKT 입력(s3) 패턴은 `PROJCRS|Van Der Grinten|6371000|BASEGEOGCRS`로 저작돼 투영 이름만 말해도 통과한다(goal에 이름이 있음) — 선정 실행에서 Gemini no_rag 1.000, Claude 0.889로 F는 천장에 가깝고 변별력이 낮다. 선정 규칙(평균 0.815 < 0.85)상 채택하되 패턴은 고치지 않는다(선정 응답을 GT 수정에 쓰지 않는 원칙). F에서의 동률은 우위 판정에 기여하지 못할 수 있다.
- v3 → 2 → 3 → 4 → 5의 연속 시도(V3-43 이후 사용자 지시).

## 8. 서명
- 저작 커밋(캡처 전): 9ba5b23 / K1 정정 커밋: 91f85e6 (relink·q85: 603df13) / GT 확정 커밋: 05f856d / 선정 커밋: 39d8cb5 이후 결과 파일 / 작성: `[SIGN]` / 검토: `[SIGN]` / 확정 시각(UTC): `[SIGN]`
