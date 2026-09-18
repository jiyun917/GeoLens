# GeoLens 재집계 보충 — 경로별 입력 토큰 · 보조 호출 비용 · 채점–judge 일치도 · Gemini survey_setup 오답

작성일 2026-09-17. 원자료: GeoLens-paper\data\eval\results\run_{gemini,claude,gpt,qwen}_unified4_r{1..5}_20260807T*.json (20개, 1,920 스텝) + unified4_bench.log. §1·§3·§4는 raw JSON만으로 계산했습니다(새 벤치 실행 없음). §2의 토큰 수는 코드와 동일한 설정으로 gemini-2.5-flash에 38회 프로브 호출(생성 호출, 총 비용 약 $0.1)을 보내 usage_metadata에서 읽은 값입니다. 계산 스크립트는 세션 스크래치패드에, 프로브 원자료는 data/eval/results/aux_call_probe_20260917.json에 저장했습니다.

## 0. 한눈에 보는 결론

- ① 비용 절감의 원인은 라우팅이 아니라 컨텍스트 조립기의 문자 예산입니다. full_system의 vector-only 경로(fallback·NONE)조차 입력이 vanilla보다 ~6,300 토큰 적고, 노드가 유지된 스텝은 오히려 fallback보다 ~530 토큰 많습니다. vanilla는 검색 결과(14.6~21.8K자)를 절단 없이 넣고, full_system은 vector 1,500자·graph 3×800자로 자릅니다.
- ② 보조 호출(Gemini Flash vision + rerank)은 thinking이 켜진 채 실행되었고, 스텝당 약 $7.0m(프로덕션 가정 1+1회) 또는 $17.9m(벤치 실행 그대로 1+3.5회)입니다. 이를 더하면 ‘생성기 기준 2.6~4.4배 저렴’은 프로덕션 가정 1.0~1.5배, 벤치 실행 기준 0.5~0.95배(vanilla가 더 저렴)로 바뀝니다.
- ③ 결정적 채점과 LLM judge의 일치율 80.3%, κ=0.572. 정규식은 전체적으로 약간 관대(225 vs 154)하지만, 불일치의 가장 큰 단일 원인은 Python \b가 한글 조사를 단어 문자로 취급해 ‘name에’, ‘Cross-line에서’ 같은 응답을 놓치는 것(regex miss 154건 중 105건, 68%)입니다. ASCII 경계로 재채점하면 1,920스텝 중 126건이 정답으로 바뀌고 매크로 Step Acc가 최대 +15pp 오르지만, full vs vanilla 방향 일관성(3/4)은 유지됩니다.
- ④ Gemini survey_setup full_system에서 5회 모두 틀린 스텝은 step 0 하나이며, 다섯 응답 모두 ‘초록색 + 아이콘을 클릭하세요’ 계열로 judge는 5/5 정답 판정입니다. 정규식(Survey|Create|New|Add)에 아이콘 묘사가 없어서 생긴 false negative입니다.

## 1. 경로별 입력 토큰 — full_system 스텝을 노드 유지 / fallback / NONE으로 분해

분류 기준(per_step 필드): fallback = fallback_activated=True(conf<0.7로 노드 폐기, vector-only); NONE = route_method='none'(rerank가 후보 거절, 노드 없음, vector-only이나 fallback 플래그 없음); 노드 유지 = route_method='llm'이고 fallback 아님(conf≥0.7, 노드 컨텍스트 주입). 값은 스텝 단순평균, n=스텝 수(모델당 80).

| 모델 | 경로 | n | 입력 토큰 mean±SD | 출력 토큰 | cost/step | Step Acc | (참고) no_rag 입력 | (참고) vanilla 입력 |
|---|---|---|---|---|---|---|---|---|
| gemini | 노드 유지 | 45 | 1,797±241 | 11.3 | $2.360m | 68.9% | 550 | 7,565 |
| gemini | fallback | 20 | 1,269±57 | 8.3 | $1.670m | 95.0% |  |  |
| gemini | NONE | 15 | 1,265±21 | 7.8 | $1.660m | 66.7% |  |  |
| claude | 노드 유지 | 47 | 3,584±319 | 25.8 | $11.137m | 93.6% | 2,056 | 9,218 |
| claude | fallback | 21 | 2,983±141 | 46.4 | $9.646m | 76.2% |  |  |
| claude | NONE | 12 | 2,987±80 | 39.2 | $9.549m | 16.7% |  |  |
| gpt | 노드 유지 | 44 | 2,575±214 | 10.6 | $6.544m | 70.5% | 1,394 | 7,367 |
| gpt | fallback | 20 | 2,045±54 | 7.8 | $5.192m | 85.0% |  |  |
| gpt | NONE | 16 | 2,058±19 | 7.1 | $5.216m | 56.2% |  |  |
| qwen | 노드 유지 | 41 | 1,791±491 | 483 | (시간환산) | 65.9% | 514 | 7,137 |
| qwen | fallback | 18 | 1,102±234 | 538 |  | 38.9% |  |  |
| qwen | NONE | 21 | 1,090±43 | 538 |  | 19.0% |  |  |

컨텍스트 토큰 근사치 = 백엔드 입력 − 같은 모델 no_rag 입력 (프롬프트 골격·스크린샷·완료 스텝을 제외한 순수 매뉴얼 컨텍스트):

| 모델 | vanilla_vector | graph_only | vision_only | state_path | full_system 전체 | full / 노드 유지 | full / fallback | full / NONE |
|---|---|---|---|---|---|---|---|---|
| gemini | +7,014 | +65 | +87 | +215 | +1,015 | +1,247 | +719 | +715 |
| claude | +7,162 | +90 | +114 | +275 | +1,281 | +1,528 | +928 | +932 |
| gpt | +5,973 | +64 | +82 | +200 | +945 | +1,181 | +651 | +664 |
| qwen | +6,623 | +134 | +266 | +119 | +938 | +1,277 | +588 | +576 |

vanilla 검색 결과의 실제 크기(오프라인 재실행, 결정적: get_manual_context(goal, top_k=5) — 임베딩·ChromaDB 로컬, API 없음):

| 시나리오 | vanilla 컨텍스트 문자 수 | 청크 수 (top-5 + 이웃) | 토큰 (o200k 근사) | 앞 1,500자의 토큰 | 맨 앞 [Knowledge Graph] 블록 문자 수 |
|---|---|---|---|---|---|
| survey_setup | 14,652 | 9 | 4,826 | 596 | 1,244 |
| 3d_visualization | 18,814 | 11 | 5,816 | 604 | 1,103 |
| attribute_computation | 21,829 | 15 | 6,614 | 602 | 1,103 |

해석:

- fallback과 NONE 스텝은 vanilla와 완전히 같은 검색(질의 = 시나리오 goal, top-5 + 이웃 + KG triplet)을 수행하지만 build_context_block이 vector_context를 1,500자로 자르기 때문에 컨텍스트가 ~600~700 토큰(vanilla의 약 1/10)입니다. 이것이 비용 차이의 대부분(Gemini 기준 7,014 → 715)입니다.
- 노드 유지 스텝은 여기에 [Current Step]·[Possible Next Steps]·graph_context(linked_chunks, 3×800자)가 얹혀 fallback보다 +530(Gemini)~+600(Claude) 토큰 많습니다. 즉 라우팅은 입력을 늘리는 요인이고, 절감은 절단 예산이 만듭니다.
- 더 중요한 부수 발견: vector_context의 앞 1,500자 중 1,100~1,250자가 [Knowledge Graph] triplet 블록(지질 개념 관계, UI 절차와 무관)이라, fallback/NONE 스텝에 실제로 전달되는 매뉴얼 본문은 첫 청크의 300~400자뿐입니다. fallback 스텝의 높은 정확도(Gemini 95%, GPT 85%)는 매뉴얼 컨텍스트가 아니라 사전학습 지식(파라메트릭 마스킹)으로 설명됩니다.
- 따라서 ‘vanilla_vector에 같은 1,500자 예산을 적용한 조건’이 없어 비용 역설은 아키텍처(라우팅) 효과가 아니라 예산 설계 효과입니다. 논문에서는 이를 그대로 밝히는 것이 안전합니다.

본표 비용 문장 제안:

```
[수정 전 — 초록] 이 절감은 그래프 라우팅이 검색 컨텍스트를 압축하는 데서 기인한다.
[수정 전 — 종합보고서 §3.5] full_system은 workflow 노드 컨텍스트를 주입하여 generator의 출력 길이를 짧게 유도… output 감소분이 커서 total 비용 역전.

[수정 후] The per-step cost advantage of full_system over vanilla_vector (2.6–4.4× on generator tokens) arises from the
context-assembly budget, not from routing: full_system caps the vector context at 1,500 characters and the graph context at
3×800 characters (≈0.7–1.2K input tokens), whereas vanilla_vector injects the untruncated retrieval result (14.6–21.8K
characters, ≈6–7K tokens). Steps that fell back to vector-only retrieval cost less than routed steps (e.g., Gemini $1.67m vs
$2.36m), and output length is essentially identical across backends. A vanilla_vector variant with the same character budget
was not evaluated, so the cost gap should be read as a property of the context budget rather than of hybrid retrieval.
```

## 2. 보조 호출(Gemini Flash) 비용 추정

### 2.1 스텝당 호출 횟수

| 호출 | 코드 경로 | 벤치 실행에서의 횟수 | 프로덕션(세션 상태 유지)에서의 횟수 | 근거 |
|---|---|---|---|---|
| vision 상태 추출 | GuideRAGPipeline.recognize_visual_state (gemini-2.5-flash) | 스크린샷당 1회. SHA-256 캐시가 프로세스(=replicate) 단위라 graph_only·full_system·state_path·재-localize가 같은 캐시를 공유 → 실행당 16회(3 시나리오 16 스텝). | 새 스크린샷마다 1회 | guide_pipeline.py:57-63, 192-198 |
| LLM rerank | GuideRAGPipeline._llm_rerank_candidates (gemini-2.5-flash) | 스텝 i에서 이전 스텝 0..i−1 재-localize + 현재 1회 = i+1회(캐시 없음). 시나리오당 채점 스텝 합 n(n+1)/2: survey 10, 3d_viz 10, attribute 36 → 16스텝에 56회 = 스텝당 3.5회. 완료 호출까지 포함하면 (n+1)(n+2)/2 = 15+15+45 = 75회/실행/백엔드. | 스텝당 1회(visited_node_ids를 세션이 보관) | bench_backends.py:520-536, 572-597; unified4_bench.log: ‘localize via LLM rerank’ 2,124 + ‘gave no answer’ 876 = 3,000 = 20 실행 × 2 백엔드(full_system, state_path) × 75 ✓ |
| CLIP·키워드 매칭 | visual_matcher / workflow_graph | 로컬 연산, API 비용 없음 | — | — |

### 2.2 thinking 여부 (코드 확인)

- 두 호출 모두 GenerateContentConfig(response_mime_type='application/json', temperature=0)만 지정하고 thinking_config(thinking_budget)를 설정하지 않습니다(guide_pipeline.py:214-217, 443-446). gemini-2.5-flash는 기본값이 dynamic thinking(켜짐)이므로 벤치 실행 당시에도 thinking 토큰이 출력 단가($2.50/M)로 과금되었습니다.
- 설치된 google-genai 1.3.0은 usage_metadata.thoughts_token_count를 노출하지 않지만, total_token_count − prompt − candidates > 0으로 thinking 토큰이 확인됩니다(아래 프로브). bench_backends.py:291-297 주석도 Gemini 2.5의 thinking 토큰이 별도 과금됨을 인지하고 있습니다.
- 벤치 로그·JSON에는 보조 호출의 토큰이 전혀 기록되지 않았으므로(_record_usage는 생성기 호출에서만 실행) 아래 값은 2026-09-17 프로브로 측정한 것입니다. 2026-08-07 실행 당시의 thinking 길이는 모델 업데이트에 따라 다를 수 있습니다.

### 2.3 프로브 측정 (gemini-2.5-flash, 코드와 동일 설정, 16 스크린샷 × {vision, rerank} = 32회 + 사전 6회)

| 호출 | n | 입력 토큰 (범위) | 출력 토큰 | thinking 토큰 mean / median (범위) | 지연 mean | 호출당 비용 mean / median | thinking 제외 하한 |
|---|---|---|---|---|---|---|---|
| vision (프롬프트 ~100 토큰 + 1922×1041 JPEG) | 16 | 391 (391–391) | 309 | 672 / 642 (391–996) | 7.8 s | $2.570m / $2.505m | $0.889m |
| rerank (후보 3개, 프롬프트 2.9~3.3K자) | 16 | 913 (831–1,022) | 26 | 1,621 / 1,333 (684–3,690) | 8.8 s | $4.392m / $3.680m | $0.339m |

단가: 입력 $0.30/M, 출력(=candidates+thinking) $2.50/M. 스크린샷 1장이 391−~100 ≈ 290 토큰으로 계산되는 것은 count_tokens와 usage_metadata 양쪽에서 동일하게 확인됩니다. attribute 시나리오의 rerank는 후보가 애매해 thinking이 길어집니다(2,271~3,690).

### 2.4 스텝당 보조 비용과 ‘보조 호출 포함 배율’

| 회계 기준 | 스텝당 보조 비용 | Gemini full+aux vs vanilla $9.27m | Claude full+aux vs vanilla $27.10m | GPT full+aux vs vanilla $17.93m |
|---|---|---|---|---|
| 생성기만 (논문 현재 표) | $0 | $2.13m → 4.4× | $10.60m → 2.6× | $6.08m → 2.9× |
| 프로덕션 가정: vision 1 + rerank 1 (mean) | $6.96m | $9.09m → 1.02× | $17.56m → 1.54× | $13.04m → 1.37× |
| 프로덕션 가정, median thinking | $6.19m | $8.32m → 1.11× | $16.79m → 1.61× | $12.27m → 1.46× |
| 프로덕션 가정, thinking 제외 하한 | $1.23m | $3.36m → 2.76× | $11.83m → 2.29× | $7.31m → 2.45× |
| 벤치 실행 그대로: vision 1 + rerank 3.5 (mean) | $17.94m | $20.07m → 0.46× (vanilla가 저렴) | $28.54m → 0.95× | $24.02m → 0.75× |

- graph_only는 vision 1회/스텝(+$2.57m)이 추가되어 Gemini $0.84m → $3.41m, state_path는 full_system과 같은 보조 호출을 씁니다. Qwen은 시간 환산 비용에 외부 API 비용이 더해져 full_system $33.10m + $6.96m = $40.06m vs vanilla $9.05m.
- 지연 시간 정합성: full_system − no_rag 지연은 4 모델에서 29.2~30.3 s인데, 벤치에서는 vision이 캐시 히트(≈0 s)이고 rerank 3.5회 × 8.8 s ≈ 30.8 s와 맞습니다. 즉 Table 1의 full_system 지연은 대부분 재-localize에 의한 rerank 반복 비용이며, 프로덕션에서는 vision 7.8 s + rerank 8.8 s ≈ 17 s 수준으로 예상됩니다.
- ‘생성기 기준 2.6~4.4배’ 옆에 적을 값: thinking 포함 프로덕션 가정으로 1.0~1.5배, 벤치 실행 회계로는 0.5~0.95배. 논문에는 ‘보조 호출을 포함하면 비용 우위는 사라지거나 역전되며, 남는 차이는 절단 예산에 의한 생성기 입력 감소분(§1)’으로 쓰는 것이 정확합니다.

## 3. 결정적 채점(step_match)과 LLM judge의 일치도

judge: bench_judge.py consensus 모드(claude-haiku-4-5-20251001 + gemini-2.5-flash, 둘 중 max → 관대). unified4 main matrix 1,920 스텝 중 judge_score가 None인 1건 제외, 1,919 스텝.

|  | judge = 1 | judge = 0 | 합계 |
|---|---|---|---|
| step_match = True | 1,038 | 225 | 1,263 (65.8%) |
| step_match = False | 154 | 502 | 656 |
| 합계 | 1,192 (62.1%) | 727 | 1,919 |

일치율 80.3%, Cohen's κ = 0.572 (moderate). 정규식이 judge보다 전체적으로 약간 관대합니다(regex pass·judge fail 225 > regex fail·judge pass 154).

| 구분 | n | 일치율 | κ | regex pass·judge fail | regex fail·judge pass | step_match acc | judge acc |
|---|---|---|---|---|---|---|---|
| claude | 480 | 89.6% | 0.717 | 25 | 25 | 75.6 | 75.6 |
| gemini | 480 | 80.4% | 0.457 | 28 | 66 | 72.7 | 80.6 |
| gpt | 480 | 79.2% | 0.536 | 47 | 53 | 65.4 | 66.7 |
| qwen | 479 | 71.8% | 0.433 | 125 | 10 | 49.5 | 25.5 |
| no_rag | 320 | 82.5% | 0.630 | 28 | 28 | 61.6 | 61.6 |
| vanilla_vector | 320 | 82.5% | 0.626 | 36 | 20 | 65.3 | 60.3 |
| graph_only | 319 | 81.2% | 0.595 | 33 | 27 | 64.3 | 62.4 |
| vision_only | 320 | 75.3% | 0.475 | 51 | 28 | 66.2 | 59.1 |
| full_system | 320 | 81.9% | 0.597 | 35 | 23 | 67.8 | 64.1 |
| state_path | 320 | 78.1% | 0.503 | 42 | 28 | 69.7 | 65.3 |
| survey_setup | 480 | 79.0% | 0.462 | 39 | 62 |  |  |
| 3d_visualization | 480 | 76.9% | 0.392 | 63 | 48 |  |  |
| attribute_computation | 959 | 82.6% | 0.652 | 123 | 44 |  |  |

### 3.1 불일치 원인 분해

regex fail · judge pass (154건) — 정규식이 놓친 정답:

| 원인 | 건수 | 설명 / 예시 |
|---|---|---|
| Python \b가 한글 조사를 단어 문자로 취급 | 105 (68%) | ‘Survey name에 My_F3_Survey를 입력하세요’ → \b(Survey name)\b 불일치(‘e’와 ‘에’ 사이에 경계 없음). ‘Cross-line에서 마우스 오른쪽 버튼을…’, ‘Tree scene에서 250을 우클릭’ 동일. \b를 (?<![A-Za-z0-9])…(?![A-Za-z0-9])로 바꾸면 105건 회복. |
| 영문 토큰 없는 한국어 의역 | 33 | ‘새 측량 아이콘을 클릭합니다’, ‘초록색 더하기 아이콘을 클릭합니다’(survey step0), ‘다음을 클릭하세요’(=Next). |
| 기타 | 16 | ‘Z-slice에서 Add Data를 선택’(3d_viz step2: 다음 단계로 건너뜀, judge가 관대), ‘SEG-Y 파일 경로를 지정하여 스캔’(키워드 미포함) 등. |

regex pass · judge fail (225건) — 정규식이 통과시킨 오답:

| 원인 | 건수 | 설명 / 예시 |
|---|---|---|
| Qwen 장문 응답에 <think> 블록 잔존 | 53 (전부 Qwen) | max_tokens=1024로 잘려 </think>가 없으면 _strip_thinking이 제거하지 못함 → 추론문 안의 키워드가 매치. Qwen 응답의 8~20%(백엔드별 6~16/80)에 <think>가 남아 있음. |
| attribute step6 패턴에 단독 OK/Select/선택 포함 | 38 | ‘Energy [-28,+28]가 선택된 상태에서 OK 버튼을 클릭’ — judge는 Select 대화상자에서 Attributes 라디오·Energy 선택이 먼저라고 판단. |
| 3d_viz step1 trap 미포착 | 28 | ‘Cross-line을 우클릭하고 Add Default Data’ — 대상이 Cross-line(오답)인데 패턴이 ‘Add Default Data’만으로 통과. |
| 3d_viz step3 대안 패턴이 요소 이름만으로 통과 | 17 | ‘Z-slice 노드를 우클릭하세요’ — 완료 스텝인데 In-line/Cross-line/Z-slice 언급만으로 매치. |
| attribute step0 패턴에 기본값 ‘Similarity’ 포함 | 15 | ‘Similarity 드롭다운을 클릭하세요’ — 실제 기대 행동은 Energy 선택. |
| attribute step7 (완료 스텝) 대안 패턴 | 6 | 요소 이름 언급으로 통과. |
| 기타 | 68 | ‘Survey Data Root … 버튼을 클릭’(survey step0에 Survey 포함), 조사 없는 키워드 우연 일치 등. |

### 3.2 민감도 재채점: \b → ASCII 경계 (사후 분석, 사전등록 채점기는 그대로 둠)

1,920 스텝을 동일 규칙으로 재구현해 저장된 matched와 100% 일치함을 확인한 뒤(불일치 0/1,920), 정규식의 \b만 ASCII 문자 경계로 바꿔 다시 채점했습니다. 126 스텝이 False→True로 바뀝니다(Claude 25, Gemini 42, GPT 48, Qwen 11; 집중 스텝: attribute step5 28, survey step1 26, 3d_viz step1 19, step2 17).

| 모델 | 백엔드 | 원래 Step Acc | 재채점 | Δ |
|---|---|---|---|---|
| gemini | no_rag | 66.7 | 78.3 | +11.7 |
| gemini | vanilla_vector | 75.0 | 81.7 | +6.7 |
| gemini | graph_only | 70.0 | 80.8 | +10.8 |
| gemini | vision_only | 77.5 | 90.8 | +13.3 |
| gemini | full_system | 72.5 | 84.2 | +11.7 |
| gemini | state_path | 76.7 | 91.7 | +15.0 |
| claude | no_rag | 85.0 | 87.5 | +2.5 |
| claude | vanilla_vector | 84.2 | 87.5 | +3.3 |
| claude | graph_only | 80.0 | 84.2 | +4.2 |
| claude | vision_only | 83.3 | 87.5 | +4.2 |
| claude | full_system | 85.0 | 87.5 | +2.5 |
| claude | state_path | 83.3 | 87.5 | +4.2 |
| gpt | no_rag | 50.8 | 65.0 | +14.2 |
| gpt | vanilla_vector | 60.0 | 70.8 | +10.8 |
| gpt | graph_only | 67.5 | 80.0 | +12.5 |
| gpt | vision_only | 54.2 | 67.5 | +13.3 |
| gpt | full_system | 69.2 | 81.7 | +12.5 |
| gpt | state_path | 72.5 | 79.2 | +6.7 |
| qwen | no_rag | 49.2 | 50.0 | +0.8 |
| qwen | vanilla_vector | 55.0 | 55.0 | 0.0 |
| qwen | graph_only | 49.2 | 54.2 | +5.0 |
| qwen | vision_only | 62.5 | 62.5 | 0.0 |
| qwen | full_system | 56.7 | 57.5 | +0.8 |
| qwen | state_path | 55.0 | 59.2 | +4.2 |

- full_system vs vanilla_vector 방향(step_acc): 원래 Gemini B / Claude A / GPT A / Qwen A (3/4) → 재채점 Gemini A(84.2 vs 81.7) / Claude 동률(87.5 vs 87.5) / GPT A(81.7 vs 70.8) / Qwen A(57.5 vs 55.0). A 판정 조건(3/4 방향 일관성)은 유지되고, Gemini의 반전이 사라집니다.
- 효과가 Gemini·GPT에 집중되는 이유: 두 모델은 UI 이름을 따옴표·굵게 없이 조사에 바로 붙여 씁니다(‘Survey name에’). Claude는 **굵게**·따옴표로 감싸 경계가 생기고, Qwen은 영어 장문이라 영향이 작습니다. 즉 현재 채점기는 모델의 표기 습관에 따라 다르게 불이익을 줍니다.
- 방어 논리로 쓸 수 있는 문장: 결정적 채점기는 judge와 κ=0.57로 일치하며, 불일치의 최대 원인은 한글 조사 경계 처리(사후 분석에서 126/1,920 스텝, 백엔드 간 방향 일관성 불변)이고, 관대 방향의 오류는 특정 스텝 패턴(attribute step0/6, 3d_viz step1/3)과 Qwen의 잘린 <think> 블록에 집중되어 백엔드 비교에 체계적 편향을 주지 않습니다. 사전등록 채점기는 변경하지 않고 이 재채점을 민감도 분석으로 보고합니다.

## 4. 보너스 — Gemini × survey_setup × full_system: 5회 모두 틀린 스텝

스텝별 정답 수(5 replicate): step 0 = 0/5, step 1 = 5/5, step 2 = 5/5, step 3 = 5/5 → 시나리오 Step Acc 75.0±0.0(per_scenario_unified4.md와 일치). 5회 모두 틀린 스텝은 step 0 하나입니다.

| rep | 라우팅 노드 (conf) | 응답 원문 | step_match | judge |
|---|---|---|---|---|
| r1 | survey_setup_01_open_selection (0.95) | 초록색 '+' 아이콘을 클릭하세요. | False | 1 |
| r2 | survey_setup_01_open_selection (0.95) | 플러스 아이콘을 클릭합니다. | False | 1 |
| r3 | survey_setup_01_open_selection (0.95) | 초록색 플러스 아이콘을 클릭하세요. | False | 1 |
| r4 | survey_setup_01_open_selection (0.95) | 초록색 플러스 아이콘을 클릭하세요. | False | 1 |
| r5 | survey_setup_01_open_selection (0.95) | '+' 아이콘을 클릭하세요. | False | 1 |

- step 0 정답 정의: pattern (?i)\b(Survey|Create|New|Add)\b, keywords [Survey, Create, New] (AND), 대안 \b(Add)\b. 화면의 해당 버튼은 텍스트 없는 초록색 + 아이콘이라 모델이 시각적으로 묘사했고(정확한 지시), judge는 5/5 정답. 정규식에 ‘+|플러스|더하기|plus’ 대안이 없어 생긴 false negative입니다. 라우팅은 5회 모두 정답 노드(step 1 노드, conf 0.95)였습니다.
- 같은 스텝의 전체 120 응답(4 모델 × 6 백엔드 × 5회) 중 65개가 +/플러스/더하기를 언급하고, 정규식 통과는 91개입니다. 즉 이 스텝의 정규식 미스는 Gemini 특유가 아니라 아이콘 묘사 방식의 문제입니다.
- 참고: 목표 판정(완료 호출)에서는 r2·r3만 ‘완료’를 냈고 r1·r4·r5는 ‘Tree scene에서 In-line을 우클릭하세요’(다음 워크플로우로 진행)를 내어 goal_completion 2/5 = 40%입니다(표의 40.0±54.8). step 3 r5는 d3_visualization_01_main_window_ready(conf 0.95)로 오라우팅됐지만 ‘완료’로 정답.

## 5. 산출물

- 이 문서: Downloads\GeoLens_재집계_보충_2026-09-17.docx; 동일 내용 마크다운 data/eval/results/reagg_supplement_20260917.md
- 프로브 원자료: data/eval/results/aux_call_probe_20260917.json (32회 호출의 prompt/candidates/thinking 토큰, 지연, 응답)
- judge 불일치 379건 목록: 세션 스크래치패드 judge_disagreements.json (모델·rep·백엔드·시나리오·스텝·응답 220자)
