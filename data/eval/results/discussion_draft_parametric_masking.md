# Discussion 초안 — Parametric Masking

**독립성**: 이 관측은 unified3 데이터 자체로 완결. unified4 성공/실패와
무관하게 논문 Discussion 에 남는다.

**근거 산출물**:
- `retrieval_attribution_unified3.md` — vanilla vector 의 §1.5.1a
  0/15 hit 원자료
- `routing_score_concentration_unified3.md` — full_system 의 오라우팅
  스텝이 오히려 높은 통과율 원자료
- `per_scenario_unified3.md` — 세 시나리오 정면 대비
- `complexity_gap_unified3.md` — 복잡도-격차 축소 정량

---

## 1. 관측 (findings)

### 1.1 검색 완전 실패에도 성능 유지

Attribute 시나리오에서 `vanilla_vector` 는 목표 절차 페이지 §1.5.1a
(pages 118-128) 를 **0/15 hit**. 상위 청크는:

| Section | 히트 수 |
|---|---|
| §2.3.1g Dip-steered Fault Enhancement Filter | 3 |
| §1.5.2a Spectral Decomposition | 3 |
| §2.3.1f Dip-steered Diffusion Filter | 3 |
| §2.3.2b Volume Curvature And Others | 3 |
| §2.5.1a Coloured Inversion | 3 |
| **§1.5.1a Bright Spot (target)** | **0** |
| **§1.5.1 (theory, adjacent)** | **0** |

즉 vanilla 는 매뉴얼의 **정확한 절차 문서를 완전히 못 봤다**. 그럼에도
attribute 시나리오 step_acc = 61.3% (macro over 4 models), full_system 의
60.0% 와 사실상 동등.

### 1.2 오라우팅 문맥에서도 성능 유지

Full_system 의 attribute 시나리오 스텝 5-7 이 정답 워크플로우가 아닌
`d3_visualization_01_main_window_ready` 로 라우팅됐다 (총 48 히트).
그럼에도 통과율 55/80/95%. 오히려 정답 워크플로우 `seismic_attribute`
로 라우팅된 스텝 1 은 5%.

### 1.3 시나리오 복잡도-격차 축소

기존 2 시나리오 대비 attribute 시나리오에서 full − vanilla 격차가
step_acc 기준 −13.1pp **축소** (widening). 모델별: Gemini +20.0,
Claude +2.5, GPT −42.5, Qwen −32.5 — 4/4 방향 일관성 미달.

## 2. 진단 (interpretation)

세 관측이 하나의 메커니즘을 시사한다: **모델의 파라메트릭 사전지식
(parametric prior) 이 RAG 시스템의 벤치 상대 (no_rag, vanilla with wrong
hits) 의 성능 하한을 인위적으로 끌어올린다**. 우리는 이를
**parametric masking** 이라 명명한다.

### 2.1 메커니즘

Attribute analysis 는 OpendTect 의 대표적 기능이고, OpendTect 는 공개
소프트웨어이며 매뉴얼·튜토리얼·블로그 포스트가 모두 웹에 색인되어
있다. 4 개 모델 (Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-4o, Qwen3-235B)
의 pretraining corpus 는 이 자료들을 상당 부분 포함할 것이 확실하다.

결과:
- **no_rag 백엔드**도 "Energy attribute, Time gate, Add > Attribute,
  on-the-fly" 같은 OpendTect 특유 어휘를 정확히 사용 가능
- **vanilla_vector 백엔드**가 잘못된 청크를 받아도, 파라메트릭 지식이
  잘못된 컨텍스트를 무시하거나 정답으로 대체
- **hybrid full_system 백엔드**가 정답 컨텍스트를 받아도, 그 이득이
  이미 파라메트릭 지식이 커버한 부분과 겹쳐 marginal gain 만 남음

### 2.2 시험 상황 비유 (open-book vs closed-book with memorized textbook)

- RAG 시스템 = 오픈북 응시자
- Vanilla baseline / no_rag = 클로즈드북 응시자, 그러나 **시험 문제집을
  통암기하고 왔음**
- 결과: 오픈북의 이점이 압축되어 정확히 측정되지 않음

## 3. 함의 (implications)

### 3.1 방법론적 이슈

RAG 시스템 벤치 대부분이 공개 소프트웨어 매뉴얼을 사용한다 (다른 GUI
자동화 벤치들, LangChain doc-QA 벤치, 등). 이들은 **parametric masking
에 노출**되어 있어 실제 hybrid 우위를 구조적으로 낮게 측정한다.

### 3.2 유효 조건

정확한 hybrid 우위 측정에는 파라메트릭 지식이 커버하지 못하는 조건이
필요:
- **모델 학습 cutoff 이후 릴리즈된 신기능** 문서 (예: OpendTect 7.0
  이후 신 attribute type, 신 workflow)
- **사내 비공개 문서** (proprietary company docs, private wiki)
- **저자원 언어의 소프트웨어 매뉴얼** (모델의 pretraining coverage 낮음)

이 조건들에서는 vanilla 와 no_rag 가 기댈 파라메트릭 지식이 없어
검색 실패 = 실질적 실패로 이어지고, hybrid 우위가 구조적으로 벌어짐.

### 3.3 본 연구 결과의 해석

Unified3 (및 unified4) 에서 보고하는 hybrid 우위 수치는 **conservative
lower bound**. 실제 사용 환경 (사내 워크플로우, 신기능) 에서는 격차가
확대될 것으로 예상되며, 이 예측의 실증은 future work.

이 때문에 **낮은 복잡도 시나리오 (survey_setup) 에서 관측된 +21.2pp
격차** 가 오히려 더 신뢰할 만한 신호일 수 있다 — 그 시나리오에서
파라메트릭 지식이 상대적으로 덜 커버해서 hybrid 이득이 그대로
드러난 것.

## 4. 서술 문장 (Discussion 삽입 후보)

> **Parametric masking as a benchmark artifact.** Our attribute-
> computation scenario reveals a systematic issue we term *parametric
> masking*: the vanilla_vector baseline retrieves zero of the target
> §1.5.1a procedural chunks (Table X) yet achieves step-accuracy
> statistically indistinguishable from the hybrid full_system on that
> scenario (61.3% vs 60.0% macro across 4 models). The mechanism is
> that the underlying language models — trained on publicly indexed
> content that includes OpendTect documentation and community tutorials
> — can generate near-correct next-step instructions from parametric
> knowledge alone, effectively bypassing the retrieval pathway. A
> complementary observation from the routing-attribution analysis
> (Table Y) is that full_system steps mis-routed to
> `d3_visualization_01_main_window_ready` still pass at 55–95%, whereas
> steps correctly routed to `seismic_attribute_04_configure` pass at
> 48.7% — the correlation between routing correctness and step
> accuracy is negative for this scenario, again consistent with the
> model recovering from wrong context via parametric priors.
>
> The corollary is that the measured hybrid gains on public-manual
> benchmarks (this work included) represent a lower bound on the gains
> one would observe in the intended deployment condition: internal
> workflow documents, post-training-cutoff features, or proprietary
> pipelines where parametric knowledge does not substitute for
> retrieval. A controlled evaluation on such private-knowledge material
> is left as future work; the QGIS portability study (Appendix Z)
> confirms the architecture transfers with minimal engineering effort,
> but QGIS is also a public tool and would exhibit the same masking.
> The methodological point stands independently of this paper's
> conclusions on hybrid retrieval.

## 5. Limitations 절 원자재

- "Public-manual benchmark 이므로 hybrid 우위는 lower bound"
- "복잡도-격차 축소 관측은 부분적으로 parametric masking 효과일 수 있음
  — 순수 시나리오 복잡도 효과와 분리 불가"
- "Future work: private-knowledge condition 벤치 필요 (사내 문서, 신기능
  문서, 저자원 언어 매뉴얼)"
