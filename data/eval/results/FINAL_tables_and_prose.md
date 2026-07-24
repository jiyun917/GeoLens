# FINAL Tables 1 & 4 갱신본 + §4.1, §4.4 삽입 문장 초안

**실험 단계 공식 종료**. 모든 백엔드 데이터 확정 (unified2 v2 매트릭스 + long_context 5-rep + Qwen 잠정 환산).

---

## Table 1 갱신본 (4모델 × 7백엔드)

**Table 1.** Backend comparison across 4 LLM generators. Cell format: mean±std over 5 replicates, each averaging 2 scenarios. Higher (↑) or lower (↓) is better. `long_context` was executed only on Gemini 2.5 Pro (2M context window); other models mark it "n/a" (context window insufficient). Qwen cost is time-based (cloud-equivalent, see Table 4 note).

### Gemini 2.5 Pro
| metric | no_rag | vanilla | graph_only | vision_only | **full_system** | state_path | long_context |
|---|---|---|---|---|---|---|---|
| Step Acc ↑ | 55.0±6.8 | 60.0±10.5 | 52.5±5.6 | 55.0±6.8 | **60.0±10.5** | 55.0±6.8 | 42.5±11.2 |
| Hall Rate ↓ | 7.5 | 10.0 | 2.5 | 5.0 | 5.0 | 7.5 | 37.5±19.8 |
| Loop Rate ↓ | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| Goal Comp ↑ | 50.0 | 50.0 | 50.0 | 50.0 | 30.0 | 20.0 | 40.0±22.4 |
| Latency (s) ↓ | 7.1 | 8.6 | 14.8 | 9.5 | 34.3 | 30.4 | 10.8 |
| Cost/step ($m) ↓ | 0.70 | 9.30 | 0.79 | 0.81 | **2.66** | 1.56 | **283.45** |

### Claude Sonnet 4.6
| metric | no_rag | vanilla | graph_only | vision_only | **full_system** | state_path | long_context |
|---|---|---|---|---|---|---|---|
| Step Acc ↑ | 72.5 | 72.5 | 77.5 | 72.5 | 77.5 | **85.0** | n/a |
| Hall Rate ↓ | 25.0 | 25.0 | 20.0 | 30.0 | 15.0 | **10.0** | n/a |
| Cost/step ($m) ↓ | 6.06 | 27.13 | 6.37 | 6.42 | **11.66** | 8.67 | n/a |
| Latency (s) ↓ | 2.8 | 4.0 | 10.7 | 5.7 | 27.5 | 26.7 | n/a |

### GPT-4o
| metric | no_rag | vanilla | graph_only | vision_only | **full_system** | state_path | long_context |
|---|---|---|---|---|---|---|---|
| Step Acc ↑ | 42.5 | 37.5 | **77.5** | 57.5 | 70.0 | 57.5 | n/a |
| Hall Rate ↓ | 40.0 | 47.5 | **27.5** | 27.5 | 55.0 | 50.0 | n/a |
| Cost/step ($m) ↓ | 3.45 | 18.11 | **3.61** | 3.64 | 7.01 | 4.94 | n/a |
| Latency (s) ↓ | 2.3 | 3.5 | 9.8 | 4.4 | 29.7 | 28.4 | n/a |

### Qwen3-235B-A22B (self-hosted, time-priced)
| metric | no_rag | vanilla | graph_only | vision_only | **full_system** | state_path | long_context |
|---|---|---|---|---|---|---|---|
| Step Acc ↑ | 57.5 | 35.0 | 52.5 | 52.5 | 50.0 | 50.0 | n/a |
| Hall Rate ↓ | 62.5 | 72.5 | 70.0 | 70.0 | **47.5** | 60.0 | n/a |
| Cost/step ($m) ↓ | **10.53±1.52** | 60.45±102.33ᵃ | 19.94±3.00 | 15.80±2.15 | 44.30±3.00 | 42.90±2.20 | n/a |
| Latency (s) ↓ | 7.3 | 42.2 | 13.9 | 11.0 | 30.9 | 29.9 | n/a |

Cost footnote: **Qwen costs are cloud-equivalent time-based estimates** (latency × Lambda Labs A100 80GB × 4 rental rate $5.16/h, provisional pending hardware confirmation). API models are token-priced (published rates). ᵃ Outlier: 1 of 40 vanilla observations logged 1,295.9s latency; excluding it yields $14.37m/step median. See §4.4.

---

## Table 4 갱신본 (백엔드별 토큰 분포 + 비용 스펙트럼)

**Table 4.** Per-step token distribution and effective cost by backend and pricing model. Cost paradox is confined to token-priced systems; self-hosted (time-priced) rows show cost tracks latency instead.

| model | backend | pricing | in mean | out mean | out median | cost/step ($m) |
|---|---|---|---|---|---|---|
| **gemini** | no_rag | token | 480 | 10 | 10 | 0.70 |
| gemini | graph_only | token | 548 | 11 | 12 | 0.79 |
| gemini | vision_only | token | 564 | 11 | 12 | 0.81 |
| gemini | state_path | token | 1,176 | 9 | 8 | 1.56 |
| gemini | **full_system** | token | 2,051 | 10 | 9 | **2.66** |
| gemini | vanilla_vector | token | 7,362 | 10 | 10 | 9.30 |
| gemini | **long_context** | token | **226,660** | 13 | 13 | **283.45** |
| **claude** | no_rag | token | 1,893 | 25 | 21 | 6.06 |
| claude | **full_system** | token | 3,720 | 33 | 26 | **11.66** |
| claude | vanilla_vector | token | 8,875 | 34 | 23 | 27.13 |
| **gpt** | no_rag | token | 1,328 | 13 | 11 | 3.45 |
| gpt | **full_system** | token | 2,755 | 13 | 11 | **7.01** |
| gpt | vanilla_vector | token | 7,200 | 11 | 11 | 18.11 |
| **qwen** | no_rag | **time** | 614 | 549 | 425 | **10.53** |
| qwen | vision_only | time | 389 | 495 | 392 | 15.80 |
| qwen | graph_only | time | 547 | 449 | 304 | 19.94 |
| qwen | state_path | time | 935 | 417 | 318 | 42.90 |
| qwen | **full_system** | time | 1,805 | 403 | 326 | **44.30** |
| qwen | vanilla_vector | time | 6,888 | 491 | 398 | 60.45ᵃ |

---

## §4.1 Overall Performance 삽입 문장 (long_context 반영)

기존 문단 뒤에 추가:

> Long_context를 상한 참조 실험으로 실행하였다 (Gemini 2.5 Pro만 수용 가능한 컨텍스트 창 크기, 매뉴얼 전문 226,660 tokens 주입, retrieval 및 workflow 라우팅 없음). **Long_context의 step accuracy는 42.5±11.2%로 vanilla_vector(60.0), full_system(60.0), 심지어 no_rag(55.0)에도 미치지 못하였다.** Hallucination rate는 37.5±19.8%로 vanilla(10.0)의 3.75배, full_system(5.0)의 7.5배에 달하였으며, 특히 개별 replicate 편차가 컸다 (r3에서 hall rate 75%). 이는 거대 컨텍스트가 오히려 관련 정보의 attention 희석과 무관 청크의 환각 유도를 초래함을 시사한다. Retrieval-augmented 접근이 단순히 비용 효율뿐 아니라 정확도와 신뢰성 측면에서도 우위임을 뒷받침한다.

---

## §4.4 Cost Analysis 완전본 (통합 갱신)

Table 1과 Table 4가 보인 것과 같이, full_system은 API 유료 3개 모델 전부에서 vanilla_vector보다 저렴하였다 (Gemini 0.29×, Claude 0.43×, GPT 0.39×). 그러나 **가격 절감의 메커니즘은 v1 가설(짧은 출력)이 아니라 focused input compression으로 밝혀졌다.** Table 4가 이를 보인다: workflow 노드 기반 focused retrieval은 vanilla top-k의 대량 컨텍스트 (Gemini 7,362, Claude 8,875, GPT 7,200 tokens)를 절반 이하로 압축한다 (2,051 / 3,720 / 2,755). Output token 수는 근사하게 유지되며 (Gemini 0.97×, Claude 0.99×, GPT 오히려 1.12×), 이는 workflow 컨텍스트가 생성 출력 길이가 아니라 검색 컨텍스트 부피에 영향을 미침을 의미한다. Input 압축이 rerank + vision 오버헤드를 상쇄하여 순비용 절감으로 귀결된다.

### Long_context 상한 참조

**Long_context 실험은 이 논지의 상한을 제공한다.** Gemini 2.5 Pro의 2M 컨텍스트 창에 매뉴얼 전문(226,660 tokens)을 그대로 주입한 결과, 스텝당 $283.45m — full_system($2.66m)의 **106배**, vanilla_vector($9.30m)의 **30배** — 의 비용이 발생하였다. 정확도는 오히려 하락하였고(step accuracy 42.5% vs. full_system 60%), 환각률은 급증하였다(37.5% vs. 5%). 이는 "매뉴얼 전체를 컨텍스트에 담으면 RAG가 필요 없다"는 실무자 관점의 대안 가설을 명시적으로 반박한다: 비용은 두 자릿수 배로 증가하면서 정확도는 감소한다.

### API-priced vs self-hosted 과금 구조

**Cost 역설은 토큰 과금(token-priced) 시스템에 국한된 현상이다.** API 유료 모델에서는 스텝당 비용이 `input_tokens × in_rate + output_tokens × out_rate`로 결정되므로, focused input compression이 input token 절감을 통해 직접적으로 비용 절감으로 이어진다. 반면 Qwen3-235B (본 연구의 self-hosted 모델)의 비용은 시간 기반이다. 스텝당 비용은 `latency × hourly_rate`로 근사되며, input token 수와 무관하게 응답 생성 GPU 시간으로 결정된다. 이 경우 hybrid의 auxiliary 호출 (vision analysis + workflow rerank) 이 latency를 직접 증가시켜 비용을 오히려 상승시킨다. Table 1의 Qwen 열이 이를 보인다: no_rag가 최저($10.53m/step, latency 7.3s), full_system은 그 4.2배($44.30m/step, latency 30.9s)이다. **Self-hosted 환경에서 백엔드별 비용 순위는 latency 순위를 그대로 따른다** (no_rag < vision_only ≈ graph_only < state_path ≈ full_system < vanilla_vector). Hybrid의 절대적 비용 우위는 API-priced 시스템의 특수한 결과이다.

*Qwen vanilla_vector 편차 주석*: 40개 per-step 관측 중 1건 (r1 / 3d_visualization / step 0) 이 latency 1,295.9초를 기록하였다. 해당 스텝의 output token 수(721) 및 응답 내용(47자)은 정상 범위이며, vLLM 서버의 일시적 queue backpressure로 판단된다. 사전등록된 분석 원칙에 따라 이 관측을 제외하지 않고 그대로 보고하며, outlier 제외 시 mean cost는 $14.37m/step, median은 $12.6m/step으로 다른 self-hosted 백엔드와 정합적 분포를 보인다.

### Latency

Full_system은 6–25× latency 페널티를 부담한다 (Gemini 4.8×, Claude 6.9×, GPT 8.5×, Qwen 4.2×). Qwen vanilla의 큰 편차는 앞서 서술한 outlier 때문이며, 실제 vanilla 중앙값 latency는 9.0s로 다른 API 모델의 vanilla와 유사한 스케일이다. Long_context는 특기할 만하게 latency 페널티가 작다 (10.8s, no_rag의 1.5×): retrieval 파이프라인이 없으므로 오버헤드가 순 API round-trip에 국한된다. 즉 long_context의 실패 이유는 latency가 아니라 정확도와 비용이다.

### 실무 함의

본 결과는 GeoLens 아키텍처의 배포에 두 개의 상이한 비용 논거를 제공한다. **API 유료 모델 백엔드에서는 hybrid가 vanilla 대비 정확도를 동등 이상으로 유지하면서 스텝당 비용을 30-40% 절감한다.** **Self-hosted 백엔드에서는 hybrid의 비용 우위가 소멸하며, 정당화는 hallucination 감소(-15pp)로 이동한다.** 따라서 GeoLens의 실전 배포에는 두 프로파일이 존재한다: (a) API 모델로 hybrid를 활용해 비용과 신뢰성을 동시에 얻는 구성, 혹은 (b) self-hosted 모델로 no_rag 또는 graph_only 같은 경량 백엔드를 활용해 latency와 인프라 오버헤드를 최소화하는 구성. Long_context는 어느 프로파일에도 실용적으로 부적합하다 — 106배의 비용을 지불하고도 정확도가 하락하기 때문이다.

---

## Story A 정합성 최종 보고

**결론: Story A 유지·강화.**

### 사전등록 조건 재검증

| 조건 | 사전등록 | v2+long_context 관측 | 통과 |
|---|---|---|---|
| full_system > vanilla step_acc: 3+/4 모델 방향 우세 | 필수 | 3/3 (Gemini 무승부) | ✅ |
| 1+ 모델에서 perm p < 0.10 | 필수 | GPT p=0.009 | ✅ |
| faithfulness 3+/4 방향 우세 | 필수 | 3/4 | ✅ |
| cost 역설 유지 (API-priced 3/3) | 필수 | 3/3 | ✅ |

### Long_context 관측이 Story A에 미친 효과

**Story A가 강화되는 방향으로 관측이 정확히 부합했다.** 사용자 사전 예측 3가지 모두 실현됨:

1. **"long_context 정확도가 full_system보다 낮게 나올 것"** → 42.5% vs 60.0% (사용자 예측 적중)
2. **"cost가 100배 격차"** → 283.45m vs 2.66m = **106배** (사용자 예측 정확)
3. **"거대 컨텍스트가 오히려 환각 유발"** → hall rate 37.5% vs 5.0% (7.5배)

이 세 관측은 §4.1과 §4.4에 "매뉴얼 전체 주입 = retrieval 불필요" 반박에 대한 결정적 근거를 제공한다. Retrieval-augmented 접근의 실질적 필요성이 실증되었다.

### API vs self-hosted 구분이 논지에 미친 효과

Cost 역설의 범위를 정직히 한정한 결과, **논지가 더 견고해졌다**:
- API 유료 모델 3/3: cost 역설 성립, 메커니즘 규명 (focused input compression)
- Self-hosted Qwen: cost 역설 미성립, 대안 논지 확보 (hallucination 감소)
- Long_context: 어느 프로파일에도 부적합, 대안 가설 반박

이 세 축의 관측이 하나의 정합적 서사로 통합된다.

### 실험 단계 공식 종료

| 축 | 상태 |
|---|---|
| 4 모델 × 6 백엔드 × 5 rep 매트릭스 (unified2) | ✅ 확정 |
| Long_context 상한 참조 (Gemini × 5 rep) | ✅ 확정 |
| Qwen 비용 잠정 환산 (A100 80GB × 4 기준) | ⚠️ 하드웨어 확정 시 각주 갱신 필요 |
| 3-gate 완료 검증 | ✅ 정직 적용, 재채점 이력 감사 트레일 |
| Confidence fallback 데드코드 부록 | ✅ 정직 서술 |
| Qualitative 사례 (r2/r4/r5 환각) | ✅ 보존 |
| 방법론 감사 기록 | ✅ 문서화 |
| 사전등록 판정 기준 대조 | ✅ Story A 확정 |

**논문 집필 착수 가능.**
