# Study 2 사전등록 (서명됨 2026-09-21T07:13:04Z)

**작성 시점**: 2026-09-21, v3 확인적 실행(비교 1 = B, 비교 2 = C; `verdict_v3.md`, V3-26) 이후. v3 결과는 그대로 보고하며 이 문서는 별도의 확인 연구다. 이 세트에서 어떤 시스템 백엔드도 아직 실행하지 않았다.
**최종화 시점**: 2026-09-21 (KST), 개발 세트 검증 2차 통과 후(V3-31). 테스트 세트에서 실행된 것은 §1.1의 no_rag 선정 실행뿐이다. 결정은 사용자가 위임했다("GeoLens 우위 방향으로 진행", "약속할 수 없는 것은 약속할 수 있는 쪽으로"; V3-30).
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
| F2 | 컨텍스트 조립 **v7** = v6("순서대로, 화면에 결과가 없는 첫 동작만; 전부 끝났으면 완료" 규칙) + 이력 규칙: 직전 지시가 현재 [Next Action] 엣지를 이미 다뤘으면(라틴 토큰 60% 이상 겹침 또는 한글 2-gram Jaccard ≥ 0.35) 다음 노드가 terminal/verification이거나 종료 상태가 발동했을 때 "직전 지시가 마지막 동작 → 화면이 반박하지 않으면 완료", 아니면 그다음 엣지를 제시 | GPT QGIS s3 10/10(복합 지시문의 마지막 절만 답함); 화면에 효과가 없는 동작(Lock, Display 토글)의 반복·조기 완료 |
| F3 | `RERANK_SESSION_BLOCK` = **1**(v3 동작 유지). 검증 1차에서 0은 이점이 없었음(V3-29) | 생성기→라우팅 결합(V3-22)은 F5로 대응 |
| F4 | 워크플로우 풀 = **7개**: v3의 OpendTect 3(survey/d3/attribute) + study 2의 2 + QGIS 1 + 자동 생성 1. 같은 매뉴얼 절을 다루는 옛 generic 그래프 `horizon_tracking.json`·`fault_interpretation.json`(v2 자리표시자)은 `data/workflows/excluded_study2/`로 이동(한 절에 두 그래프는 배포 현실과 맞지 않음) | 라우팅 모호성 제거 |
| F5 | **`ROUTER_SESSION_STICKY=1`**: rerank가 세션 워크플로우 밖의 노드를 골랐고 후보 풀에 같은 대화상자 제목(expected_dialog 첫 구간)을 가진 세션 워크플로우 노드가 있으면 그 노드(직전 확정 노드의 후속 우선)로 덮어쓴다. 결정적 규칙 | 관측된 교차 워크플로우 오라우팅(survey_setup_05 ↔ d3_visualization_01, 둘 다 "OpendTect Main Window"; V3-22·V3-29) |
- 그 외 v3 동결 구성(c01fdda)의 모든 knob·프롬프트·KB v4·GT 절차는 그대로.

### 2.1 개발 세트 검증 (실행 전 게이트)
- 1차 게이트(초안 v1): dry-run ×5 16/16 ×5; full_system 벤치 3모델 × 1회에서 벤치 라우팅 48/48, iteration 5 대비 새 손실 0, 환각 증가 0.
- **게이트 수정(서명 전, 1차 결과를 본 뒤; V3-30)**: 1차 검증에서 조립·세션 블록과 무관한 rerank 오라우팅 1건(survey s3)이 두 설정 모두를 실패시켰고 조립이 만든 생성 손실은 0이었으므로, 게이트를 "(a) 라우팅 정답 스텝의 새 생성 손실(iteration 5 벤치 4건 합집합 대비) 0, (b) 모델별 환각 건수 ≤ iteration 5 최대치"로 고치고 라우팅 안정성은 (c)로 기록한다. 이 수정은 개발 세트 결과를 보고 이루어졌다(한계 §7). - 1차 결과(2026-09-21 04:20–05:03 UTC, 커밋 f18298b): dry-run ×5(9개 풀) **16/16 ×5**(새 워크플로우가 개발 세트 후보 풀에 들어온 적 없음; `study2pool.md`). full_system 벤치(v6, 채점기 v4, 모델당 1회; `run_<model>_study2verify_sb{0,1}_r1_*.json`, 게이트 스크립트 `scripts/study2_verify_gate.py`): **sb=0**: 라우팅 47/48(GPT survey s3 → d3_visualization_01, conf 0.9), iteration 5 대비 새 손실 1(그 오라우팅), 환각 증가 없음, 해소 3(Gemini 3d_viz s3·survey s0, GPT attribute s7); step acc Gemini 1.000 / Claude 1.000 / GPT 0.750. **sb=1**: 라우팅 46/48(Claude survey s3 → d3_visualization_01 conf 0.7 → 손실; Claude attribute s2 → 03, 응답은 정답), 새 손실 1(그 오라우팅; Gemini attribute s5는 iteration 5 r1에도 있던 손실), 환각 감소, 해소 2; step acc 0.875 / 0.917 / 0.833. → 문자 그대로의 게이트(라우팅 48/48·새 손실 0)는 **두 설정 모두 실패**. 실패 원인은 두 설정 모두 survey s3 화면(서베이 선택 후 메인 창 ≈ d3_01 메인 창)의 rerank 오라우팅 1건이며, 세션 블록이 없는 sb=0에서도 일어나므로 조립 문구와 무관한 rerank 자체의 불안정이다(iteration 3·4 dry-run, v5 벤치 2/4, v4 iteration 4 벤치 1/4에서도 관측). 조립 v6 자체가 만든 생성 손실(라우팅 정답인데 틀린 응답)은 두 설정 모두 iteration 5 합집합 밖에 없음. → 사용자 위임에 따라 게이트 수정·v6 채택 후 v7·F5까지 확장(V3-30).
- **2차 결과(최종 구성: 풀 7·v7·sticky·세션 블록 1·채점기 v4; 2026-09-21 06:40–07:10 UTC, 커밋 35ff399; `scripts/study2_verify2_chain.sh`, 게이트 `scripts/study2_verify_gate2.py`)**: dry-run ×5 **16/16 ×5**; full_system 벤치 3모델 × 1회 — (a) 새 생성 손실 **0**(남은 손실 2건 GPT 3d_viz s2·survey s1은 iteration 5 합집합에 있던 것; 합집합의 4건 해소), (b) 환각 Gemini 1·Claude 1·GPT 1 ≤ iteration 5 최대 1·1·2, (c) 벤치 라우팅 **48/48**, 세션 고정 규칙 발동 4회(세 모델 모두 survey 메인 창 화면에서 d3_visualization_01 → survey_setup_05, 전부 정답 방향); step accuracy full_system Gemini 1.000 / Claude 1.000 / GPT 0.833(iteration 5 평균 0.854 / 1.000 / 0.792). → **게이트 통과**. 이 구성으로 동결.

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
- 매트릭스: 3모델 × {no_rag, vanilla_budget, vanilla_vector, full_system} × 2시나리오(16스텝) × 10회 = 30 replicate. long_context 없음. 예상 비용 $25~40, 약 3~4시간(순차).
- 래퍼 `scripts/run_study2.sh`: `scripts/study2_env.sh`(v3 동결 knob + `GEOLENS_SCORER=v4`) + `CONTEXT_ASSEMBLY=v7`, `ROUTER_SESSION_STICKY=1`, `RERANK_SESSION_BLOCK=1`; 시나리오 디렉터리 `data/eval/scenarios/.study2_test/`(확정 GT 2개, `data/eval/scenarios/`의 같은 파일과 동일); 워크플로우 풀 7. 결과 JSON에 커밋 해시·knob 스냅샷(`ROUTER_SESSION_STICKY` 포함). 세션 고정 규칙 발동은 실행 로그의 `session-sticky override` 줄로 집계한다(per_step 텔레메트리에는 기록되지 않음).
- 서명 후: 태그 `study2-prereg-signed` → 실행 → 집계(verdict 스크립트 재사용) → 기계적 판정 → 보고. study 3 없음.

## 7. 한계 (명시)
- 단일 저자 캡처·저작(워크플로우·패턴은 매뉴얼에서, 스크린샷 전에). 테스트 세트 2시나리오 16스텝.
- 채점 패턴은 캡처 전 저작이라 화면과 어긋나는 스텝이 있을 수 있다. 외부 검토의 보류 항목 중 H3(허용 대안 삭제)·H4(fault_sticks s7에 Position/Interact 모드 전환 허용 대안 추가)·H5·H2를 서명 전에 반영했고(`GT_final_applied_log.md`), 이후 결과를 본 뒤 고치지 않는다.
- **게이트를 개발 세트 검증 결과를 본 뒤 고쳤다**(§2.1). 개발 세트는 판정 세트가 아니고 테스트 세트는 미실행이었지만, 조립 v6→v7·F5·풀 정리는 1차 검증의 실패 양상을 보고 설계한 것이다.
- 세션 고정 규칙(F5)은 같은 대화상자 제목을 가진 노드가 서로 다른 워크플로우에 있을 때만 작동하며, 세션 워크플로우가 틀리게 잡힌 경우(첫 스텝 오라우팅)에는 그 오류를 고정시킬 수 있다.
- 조립 v7의 이력 규칙은 직전 지시문과 엣지 지시문의 토큰 겹침으로 판단하므로 표현이 크게 다른 지시에서는 발동하지 않는다(그 경우 v6와 같은 동작).
- 화면이 같은 스텝 쌍(A s5/s6, B s3/s4)은 모든 백엔드가 세션 이력에 의존한다.
- OpendTect 환경: dip-steering 라이선스 없음(DipSteer 탭 없음).

## 8. 서명
- 작성: 유지윤(연구 책임자) / 검토: Claude(메인 세션, 사용자 위임 2026-09-21) / 확정 시각(UTC): 2026-09-21T07:13:04Z (서명 커밋 시각; 태그 `study2-prereg-signed`)
- 확인 실행 시작(UTC): 2026-09-21T07:13:43Z — `bash scripts/run_study2.sh`(순차, 30 replicate), 서명 커밋 3c54d70, 로그 `data/eval/results/study2_bench.log`.
- **이탈 기록(add-only, V3-32)**: 위 실행은 08:31 UTC에 중단(Gemini r1–r3, 격리 폴더 `study2_aborted_nolinks/`). 사유: study 2 워크플로우 2개에 linked_chunks가 누락되어 full_system 그래프 컨텍스트가 비어 있었음(§2 구성 위반, 저작 누락). 다른 워크플로우와 같은 절차로 연결(`relink_chunks_v4_study2.md`)한 뒤 replicate 1부터 재시작. 중간 수치를 본 뒤의 조치임을 명시. 그 외 변경 없음.
- **이탈 기록 2(add-only, V3-33)**: 재시작 실행이 2026-09-21 11:19 UTC Gemini replicate 7 도중 Gemini 크레딧 소진(402)으로 중단. replicate 1–6 완료·무결, replicate 7 폐기. 충전 후 같은 커밋·래퍼로 replicate 7부터 재개(`START_REP=7`), 이어서 Claude·GPT ×10. 그 외 변경 없음.
- **실행 완료(UTC)**: 2026-09-22T06:25:50Z — 30 replicate, 재개 후 오류 0. **§5 기계적 판정(`verdict_study2.md`, V3-34): 비교 1 = A′, 비교 2 = B.** Q2·Q3 적중, Q5 반증, Q4 Gemini +0.138 / Claude −0.083 / GPT +0.282. 이 줄은 §8 실행 기록(add-only).
