# GeoLens 재집계 보충 2 — long_context·QGIS ASCII 경계 재채점, 세 채점기 방향 비교, Qwen <think> 잔존 영향

작성일 2026-09-17. 원자료: run_*_unified4_r{1..5}.json (1,920 스텝, judge_score 포함), run_gemini_longctx_r{1..5}_20260807T18*.json (80 스텝), run_gemini_qgis_pilot_r{1..5}_20260813T*.json (120 스텝). 모두 raw JSON 재계산이며 새 벤치·API 호출은 없습니다. 재구현한 채점기는 저장된 matched(2,120 스텝)·hallucinated(Qwen 480 스텝)와 100% 일치함을 먼저 확인했습니다. ASCII 경계 = 정규식의 \b를 (?<![A-Za-z0-9]) / (?![A-Za-z0-9])로 바꾼 것(한글 조사가 영문 토큰에 붙어도 매치). long_context와 QGIS 파일럿에는 judge 점수가 없어(--judge 미실행) 두 채점기만 비교합니다.

## 0. 한눈에 보는 결론

- long_context(Gemini, 5회): 59.2 → 72.5%. 그래도 ASCII 경계에서 Gemini 백엔드 중 최저(no_rag 78.3, vanilla 81.7, full 84.2)라 ‘148배 비싸고 정확도는 최저’ 서술은 유지됩니다.
- QGIS 파일럿: no_rag 62.5 → 82.5, vanilla 62.5 → 82.5, full_system 57.5 → 87.5±0.0. ‘full 57.5 < no_rag 62.5’는 조사 경계 인공물이었고, ASCII 경계에서는 full_system이 최고입니다. 단, step 3(Input layer 선택)은 3 백엔드 15회 모두 ‘Distance에 50 입력’으로 답해 0/5이며 이는 시나리오 정의 문제(상한 87.5%)입니다.
- 세 채점기(원래·ASCII·judge) full vs vanilla 방향: GPT와 Qwen은 셋 다 full 우세(강건), Gemini는 원래 채점기에서만 vanilla 우세(인공물), Claude는 ±1.6pp 안의 동률. 방향 일관성 3/4는 세 채점기 모두에서 성립하지만 ‘어느 3개’인지는 채점기마다 다릅니다.
- Qwen <think> 잔존(480 스텝 중 55, 11.5%; 모두 </think> 없이 잘림)은 예외 없이 matched=True·hallucinated=True로 채점됐습니다. 잔존을 빈 응답으로 처리하면 Qwen Step Acc는 백엔드별 7~20pp, 환각률은 5~20pp 내려가고 루프율은 불변입니다. full vs vanilla는 환각·루프에서 세 변형 모두 full 우세, Step Acc는 strip 변형에서 동률(42.5 vs 42.5)로 바뀌고, judge에서는 full vs no_rag가 역전(28.3 vs 30.0)합니다. Qwen 별도 트랙의 근거가 하나 더 생깁니다.

## 1. long_context (Gemini 2.5 Pro, 3 시나리오 × 5회) ASCII 경계 재채점

| 채점기 | long_context 매크로 | survey_setup | 3d_visualization | attribute | Gemini no_rag / vanilla / graph / vision / full / state |
|---|---|---|---|---|---|
| 원래 | 59.2±9.9 | 75.0 | 45.0 | 57.5 | 66.7 / 75.0 / 70.0 / 77.5 / 72.5 / 76.7 |
| ASCII 경계 | 72.5±2.3 | 75.0 | 85.0 | 57.5 | 78.3 / 81.7 / 80.8 / 90.8 / 84.2 / 91.7 |

- 80 스텝 중 8건이 뒤집혔고 전부 3d_visualization(‘In-line에서 마우스 오른쪽 버튼’, ‘Cross-line에서 …’ 유형)입니다. attribute와 survey_setup은 변화 없음.
- 두 채점기 모두에서 long_context는 Gemini 7개 백엔드 중 최저입니다(원래 59.2 < no_rag 66.7; ASCII 72.5 < no_rag 78.3). 비용 148×는 채점과 무관하므로 ‘매뉴얼 전문 주입은 148배 비용에도 최저 정확도’ 문장은 그대로 쓸 수 있습니다. 다만 격차는 원래 −13.3pp(vs full)에서 −11.7pp로 약간 줄어듭니다.

## 2. QGIS 파일럿 (Gemini, 8 스텝 × 5회) ASCII 경계 재채점

| 백엔드 | 원래 Step Acc | ASCII 경계 | 뒤집힌 스텝 | Hall Rate(불변) | Goal Comp(불변) | cost/step(불변) |
|---|---|---|---|---|---|---|
| no_rag | 62.5±8.8 | 82.5±11.2 | 8/40 | 10.0 | 100 | $0.87m |
| vanilla_vector | 62.5±8.8 | 82.5±6.8 | 8/40 | 17.5 | 100 | $4.69m |
| full_system | 57.5±6.8 | 87.5±0.0 | 12/40 | 12.5 | 100 | $2.45m |

스텝별 정답 수(5회 중), 원래 → ASCII:

| 백엔드 | s0 Toolbox | s1 buffer 검색 | s2 Buffer 더블클릭 | s3 Input layer | s4 Distance 50 | s5 ‘…’ 출력 | s6 Save/OK | s7 완료 |
|---|---|---|---|---|---|---|---|---|
| no_rag | 5→5 | 4→4 | 1→5 | 0→0 | 5→5 | 0→4 | 5→5 | 5→5 |
| vanilla_vector | 5→5 | 3→3 | 2→5 | 0→0 | 5→5 | 0→5 | 5→5 | 5→5 |
| full_system | 5→5 | 3→5 | 0→5 | 0→0 | 5→5 | 0→5 | 5→5 | 5→5 |

- 뒤집힌 응답 예: ‘Buffer를 더블 클릭하세요’(s2, 패턴의 더블.?클릭|Buffer가 ‘를’·‘하세요’에 막힘), ‘Buffered 필드 옆의 '...' 버튼을 클릭하세요’(s5, \.\.\.|출력이 조사에 막힘), ‘Processing Toolbox 검색창에 buffer를 입력하세요’(s1). QGIS 시나리오 패턴은 한글 대안(메뉴|검색|입력|더블클릭|선택|저장 …)을 많이 쓰는데, \b 뒤에 한글 조사가 오면 매치되지 않아 OpendTect보다 영향이 큽니다.
- s3는 세 백엔드 15회 모두 ‘Distance 필드에 50을 입력하세요’로 답했습니다. 캡처 화면의 Buffer 대화상자에서 Input layer가 이미 roads_33S로 채워져 있었을 가능성이 높고, 모델은 정당하게 다음 필드로 넘어간 것으로 보입니다. 정답 정의(Input layer 선택)를 캡처 상태에 맞게 손보지 않으면 이 시나리오의 상한은 7/8 = 87.5%입니다. full_system은 ASCII 경계에서 이 상한에 5/5 도달(SD 0).
- 종합결과보고서 §7 정직성 항목 1(‘QGIS full 57.5 < no_rag 62.5, signature 미성숙 조건’)과 paper_discussion_integrated.md §D1의 해당 문장은 ‘원래 채점기에서는 −5pp, 조사 경계를 보정하면 +5pp(87.5 vs 82.5), 세 백엔드 공통으로 s3가 0/5’로 바꿔야 합니다. ‘파라메트릭 마스킹(vanilla == no_rag)’ 관찰은 두 채점기 모두에서 유지됩니다(82.5 = 82.5).

## 3. 세 채점기로 본 full_system vs vanilla_vector 방향 (main matrix, 매크로 mean±SD, n=5)

| 모델 | 원래: full / vanilla → 방향 | ASCII 경계: full / vanilla → 방향 | judge(consensus): full / vanilla → 방향 | 세 채점기 일치? | (참고) no_rag 원래/ASCII/judge |
|---|---|---|---|---|---|
| Gemini | 72.5±9.6 / 75.0±11.4 → vanilla (−2.5) | 84.2±3.5 / 81.7±6.3 → full (+2.5) | 88.3±8.0 / 80.8±4.8 → full (+7.5) | 불일치 — 원래 채점기만 반대(조사 경계 인공물) | 66.7 / 78.3 / 82.5 |
| Claude | 85.0±2.3 / 84.2±1.9 → full (+0.8) | 87.5±0.0 / 87.5±0.0 → 동률 | 84.2±1.9 / 85.8±2.3 → vanilla (−1.6) | 동률권(±1.6pp, SD 이내) | 85.0 / 87.5 / 84.2 |
| GPT | 69.2±3.7 / 60.0±6.3 → full (+9.2) | 81.7±7.0 / 70.8±8.3 → full (+10.8) | 72.5±10.5 / 62.5±2.9 → full (+10.0) | **강건 (3/3 full)** | 50.8 / 65.0 / 62.5 |
| Qwen | 56.7±9.1 / 55.0±6.8 → full (+1.7) | 57.5±9.0 / 55.0±6.8 → full (+2.5) | 28.3±5.4 / 25.0±14.4 → full (+3.3) | 방향은 3/3 full이나 judge 절대값 붕괴(25~28%), §4 strip 변형에서 동률 | 49.2 / 50.0 / 30.0 |

| 채점기 | full > vanilla인 모델 | 방향 일관성 | full vs no_rag: full 우세 모델 |
|---|---|---|---|
| 원래 step_match | Claude, GPT, Qwen | 3/4 (Gemini 반대) | Gemini, GPT, Qwen (Claude 동률) |
| ASCII 경계 | Gemini, GPT, Qwen | 3/4 (Claude 동률) | Gemini, GPT, Qwen (Claude 동률) |
| LLM judge | Gemini, GPT, Qwen | 3/4 (Claude 반대, −1.6pp) | Gemini, GPT (Claude 동률, **Qwen 반대** 28.3 vs 30.0) |

전체 6 백엔드 × 4 모델 × 3 채점기 (Step Acc %, 매크로):

| 모델 | 백엔드 | 원래 | ASCII | judge | 뒤집힌 스텝(ASCII) |
|---|---|---|---|---|---|
| gemini | no_rag | 66.7 | 78.3 | 82.5 | 7 |
| gemini | vanilla_vector | 75.0 | 81.7 | 80.8 | 4 |
| gemini | graph_only | 70.0 | 80.8 | 82.5 | 7 |
| gemini | vision_only | 77.5 | 90.8 | 90.0 | 8 |
| gemini | full_system | 72.5 | 84.2 | 88.3 | 7 |
| gemini | state_path | 76.7 | 91.7 | 90.0 | 9 |
| claude | no_rag | 85.0 | 87.5 | 84.2 | 3 |
| claude | vanilla_vector | 84.2 | 87.5 | 85.8 | 4 |
| claude | graph_only | 80.0 | 84.2 | 82.5 | 5 |
| claude | vision_only | 83.3 | 87.5 | 77.5 | 5 |
| claude | full_system | 85.0 | 87.5 | 84.2 | 3 |
| claude | state_path | 83.3 | 87.5 | 81.7 | 5 |
| gpt | no_rag | 50.8 | 65.0 | 62.5 | 9 |
| gpt | vanilla_vector | 60.0 | 70.8 | 62.5 | 9 |
| gpt | graph_only | 67.5 | 80.0 | 69.2 | 8 |
| gpt | vision_only | 54.2 | 67.5 | 60.8 | 9 |
| gpt | full_system | 69.2 | 81.7 | 72.5 | 8 |
| gpt | state_path | 72.5 | 79.2 | 73.3 | 5 |
| qwen | no_rag | 49.2 | 50.0 | 30.0 | 1 |
| qwen | vanilla_vector | 55.0 | 55.0 | 25.0 | 0 |
| qwen | graph_only | 49.2 | 54.2 | 32.6 | 4 |
| qwen | vision_only | 62.5 | 62.5 | 25.0 | 0 |
| qwen | full_system | 56.7 | 57.5 | 28.3 | 1 |
| qwen | state_path | 55.0 | 59.2 | 36.7 | 5 |

- 쓸 수 있는 문장: ‘GPT-4o에서 full_system > vanilla_vector 방향은 세 채점기(사전등록 결정적 채점기, 한글 조사 경계를 보정한 변형, 두 모델 합의 LLM judge)에서 모두 유지되며(+9.2 / +10.8 / +10.0pp), 4-모델 방향 일관성 3/4도 세 채점기 모두에서 성립한다.’
- 쓰면 안 되는 문장: ‘Claude·Qwen에서도 채점기에 강건하다.’ Claude는 세 채점기의 차이가 ±1.6pp로 replicate SD 안이라 동률로 서술해야 하고, Qwen은 §4 참조.
- Gemini는 원래 채점기의 반전(−2.5pp)이 ASCII·judge에서 +2.5/+7.5로 바뀌므로, 논문 본문의 ‘Gemini 반전’ 서술에는 ‘조사 경계 인공물에 기인, 보정·judge에서는 full 우세’ 각주가 필요합니다.
- judge는 Qwen에서 25~37%로 결정적 채점(49~63%)의 절반입니다. judge가 응답 앞 500자만 보는데 Qwen 응답 평균 446~609 토큰이고 <think> 잔존 시 추론문만 보게 되기 때문입니다(§4).

## 4. Qwen <think> 잔존이 Step Acc·환각률·루프율에 준 영향

잔존 정의: 응답에 <think>가 있고 </think>가 없는 경우(max_tokens=1024로 잘려 _strip_thinking이 제거하지 못함). 480 스텝 중 55건(11.5%), 백엔드별 no_rag 6, vanilla 8, graph 9, vision 16, full 9, state 7 (모두 /80). </think>가 남은 응답은 0건. 잔존 응답 길이는 ~4,300~4,500자로 전부 영어 추론문입니다.

| 집계(풀링) | n | matched | hallucinated | looped |
|---|---|---|---|---|
| 잔존 응답 | 55 | 100.0% | 100.0% | 0.0% |
| 정상 응답 | 425 | 42.8% | 42.4% | 13.9% |

세 변형: 원래 / 제외(잔존 스텝을 분모·분자에서 제거) / strip(잔존을 빈 응답으로 처리 → matched=False, hallucinated=없음, looped=False). 매크로 mean±SD, n=5.

| 백엔드 | Step Acc 원래 / 제외 / strip | Hall Rate 원래 / 제외 / strip | Loop Rate 원래 / 제외 / strip |
|---|---|---|---|
| no_rag | 49.2±8.0 / 44.9±9.5 / 40.0±9.6 | 40.0±12.0 / 34.5±12.3 / 30.8±10.5 | 21.7±7.5 / 23.4±9.7 / 21.7±7.5 |
| vanilla_vector | 55.0±6.8 / 47.1±9.9 / 42.5±9.9 | 61.7±13.0 / 57.7±17.5 / 49.2±13.9 | 15.0±6.3 / 18.0±9.2 / 15.0±6.3 |
| graph_only | 49.2±9.9 / 43.1±8.1 / 40.0±8.6 | 67.5±6.8 / 63.4±9.6 / 58.3±9.3 | 2.5±5.6 / 2.9±6.4 / 2.5±5.6 |
| vision_only | 62.5±12.5 / 53.8±13.8 / 42.5±12.6 | 54.2±22.2 / 44.6±25.9 / 34.2±18.3 | 10.0±7.0 / 12.9±8.8 / 10.0±7.0 |
| full_system | 56.7±9.1 / 52.6±11.1 / 42.5±9.5 | 50.0±8.8 / 40.4±10.6 / 35.8±8.6 | 6.7±8.6 / 8.0±11.0 / 6.7±8.6 |
| state_path | 55.0±10.8 / 50.8±10.5 / 48.3±10.0 | 56.7±9.6 / 52.3±10.5 / 50.0±10.6 | 5.8±7.0 / 6.6±7.5 / 5.8±7.0 |

| 대비 | 지표 | 원래 | 제외 | strip |
|---|---|---|---|---|
| full vs vanilla | Step Acc | 56.7 vs 55.0 → full | 52.6 vs 47.1 → full | 42.5 vs 42.5 → **동률** |
| full vs vanilla | Hall Rate | 50.0 vs 61.7 → full | 40.4 vs 57.7 → full | 35.8 vs 49.2 → full |
| full vs vanilla | Loop Rate | 6.7 vs 15.0 → full | 8.0 vs 18.0 → full | 6.7 vs 15.0 → full |
| full vs no_rag | Step Acc | 56.7 vs 49.2 → full | 52.6 vs 44.9 → full | 42.5 vs 40.0 → full |
| full vs no_rag | Hall Rate | 50.0 vs 40.0 → no_rag | 40.4 vs 34.5 → no_rag | 35.8 vs 30.8 → no_rag |
| full vs no_rag | Loop Rate | 6.7 vs 21.7 → full | 8.0 vs 23.4 → full | 6.7 vs 21.7 → full |

- 잔존 응답은 추론문 안에 기대 키워드가 거의 항상 등장해 matched=True가 되고, 따옴표·‘X 버튼’ 패턴이 다수라 hallucinated=True가 됩니다. 즉 Qwen의 Step Acc는 잔존이 올리고, 환각률도 잔존이 올립니다(두 효과가 같은 스텝에서 동시에 발생). 루프율은 잔존 응답이 서로 다르므로 영향이 없습니다.
- 잔존 비율이 vision_only(20%)에서 가장 높아 vision_only의 62.5%가 가장 크게 부풀려졌습니다(strip 42.5). 백엔드 간 잔존 비율이 6~16/80으로 다르므로 원래 채점의 Qwen 백엔드 순위는 신뢰할 수 없습니다.
- judge는 잔존 55건 중 52건을 0으로 판정했습니다. 잔존 제외 시 Qwen judge 정확도는 no_rag 30.8, vanilla 26.7, graph 34.4, vision 30.5, full 37.9, state 37.6으로 소폭 오르지만 여전히 결정적 채점의 절반 수준입니다.
- Qwen 별도 트랙 근거 정리: (1) 텍스트 전용 모델이라 스크린샷을 보지 않는 유일한 생성기, (2) 셀프호스팅 시간 환산 비용으로 API 모델과 단위가 다름, (3) 채점기 처리(잔존 strip)에 따라 full vs vanilla Step Acc 방향이 동률로 바뀌고 judge에서는 full vs no_rag가 역전, (4) judge 절대값이 25~37%로 다른 모델(62~90%)과 동떨어짐. 환각·루프 축에서는 full 우세가 세 변형에서 유지되므로 ‘Qwen에서도 hybrid가 환각·루프를 줄인다’는 서술은 가능합니다.
- 수정 권고(코드): _strip_thinking에 ‘</think> 없는 <think>는 이후 전부 제거’ 분기를 추가하거나 Qwen max_tokens를 늘려야 합니다. 논문 표는 사전등록 채점기를 유지하되 이 민감도 결과를 각주 또는 부록으로 넣는 것을 권합니다.

## 5. 종합결과보고서·초안 문장 수정 대상

| 위치 | 현재 | 수정 |
|---|---|---|
| 종합결과보고서 §7 항목 1, paper_discussion_integrated §D1 | QGIS pilot full_system step_acc 57.5 < no_rag 62.5 (5pp 하회), signature 온보딩 직후 미최적 조건 | 원래 채점기 57.5 vs 62.5; 한글 조사 경계 보정 시 87.5 vs 82.5(= vanilla 82.5). 하회는 채점 인공물이며 s3(Input layer)는 세 백엔드 공통 0/5. faith·cost 축 서술은 불변. |
| 초록·5.3절 long_context | 148배 비용에도 해당 모델 백엔드 중 최저 정확도 | 유지. (원래 59.2 / 보정 72.5, 두 경우 모두 Gemini 최저) |
| §D1 ‘Gemini 반전 −2.5pp’ | Gemini는 vanilla 우세 | 각주: 조사 경계 보정 +2.5pp, judge +7.5pp로 full 우세 → 인공물 |
| Table 1 Qwen 행 | Step Acc 49~63, Hall 40~68 | 각주: <think> 잔존 11.5%가 Step Acc·Hall을 동시에 부풀림; strip 시 Step Acc 40~48, Hall 31~58. Qwen 별도 트랙 근거 4건(§4). |
| 4.4절 채점 한계 | substring-lenient matching limitation | 추가: Python \b와 한글 조사 문제(1,920 스텝 중 126 + long_context 8 + QGIS 28 뒤집힘), 방향 일관성 3/4는 세 채점기에서 유지, GPT만 세 채점기 강건 |

## 6. 산출물

- 이 문서: Downloads\GeoLens_재집계_보충2_2026-09-17.docx; 마크다운 data/eval/results/reagg_supplement2_20260917.md
- 계산 스크립트: 세션 스크래치패드 three_scorer.py (세 채점기·long_context·QGIS), Qwen 잔존 분석은 인라인 스크립트(재구현 채점기가 저장값과 0 불일치 확인 포함)
- 이전 보충(경로별 토큰·보조 호출·judge 일치도·Gemini survey_setup): Downloads\GeoLens_재집계_보충_2026-09-17.docx
