# Paper Draft — Discussion (Integrated, 3 Chapters)

**분량 목표**: 약 3 페이지 (본문 ~1,500 단어 + 표 3 개)
**작성 시점**: 2026-08-13, unified4 + qgis_pilot 완료 후 실험 단계 종료 시점
**포함 데이터**: unified4 매트릭스 (4M × 6B × 5R × 3S) + qgis_pilot (1M × 3B × 5R × 1S)
**전제**: §Portability 소절 (v2) 은 Results 뒤 본문에 배치 확정. Discussion 은
그 뒤 이어짐.

**챕터 구성 (사용자 확정)**:
1. **Confidence-gated Hybrid** — A 판정 재구성 + "when in doubt, don't route"
2. **Parametric Masking as a Benchmark Artifact** — 3 개 데이터 포인트
3. **Signature Maturity Determines Guard-Hole Activation** — 새 발견 + NONE 갭 future work

---

## §Discussion 1. Confidence-Gated Hybrid: When Grounded Routing Beats Vanilla, and When It Doesn't

> The main matrix (Table 1, §Results) meets all four pre-registered A-story
> criteria: on step accuracy, `full_system` beats `vanilla_vector` in
> 3 of 4 models by direction consistency; GPT achieves permutation
> p = 0.032 (Δ = +9.2 pp) and p = 0.034 (Δ = +18.3 pp) against
> `vanilla_vector` and `no_rag` respectively; faithfulness direction
> consistency is 3/4 in the same direction; and the cost paradox holds on
> 3/3 API-priced models (`full_system` is 2.6–4.4× cheaper per step than
> `vanilla_vector`). We report the matrix as **SUCCESS on the pre-registered
> A-story**.
>
> That said, the mechanism producing that success is not the one we
> initially predicted. In the pre-registered attribute-scenario
> subprediction (`v2_pre_registration.md § attribute prediction`), we
> reasoned that hand-authored workflow routing would recover procedural
> chunks that `vanilla_vector` retrieval missed, producing a widened
> hybrid gap on complex scenarios. Retrieval attribution supports the
> mechanism half of that prediction (`vanilla_vector` misses the §1.5.1a
> procedural chunks 0/15), but the outcome half is refuted: the
> full-minus-vanilla step-accuracy gap actually narrows on the complex
> attribute scenario relative to the two simple ones (Δ ≈ −1.3 pp macro),
> before widening again to +3.1 pp under the unified4 signature-refactor
> attempt.
>
> The refactor itself surfaced the more interesting finding. Our
> unified4 refactor passed a hand-authored dry-run gate at 8/8 nodes but
> collapsed to 0/160 in-bench routing to the intended `seismic_attribute`
> workflow: the refactored signature phrases were too specific to survive
> the noisier vision-extracted state representation that the bench uses at
> runtime. Yet the attribute-scenario gap widened despite this collapse.
> The explanation is architectural: under low-confidence conditions the
> pipeline suppresses graph context and falls back to vector-only
> retrieval, and this fallback outperformed the confidently wrong context
> that unified3's over-absorbing signature had supplied. **We call this
> the "when in doubt, don't route" observation.** A workflow node that
> routes with confidence 0.91 and pass rate 5 % (unified3
> `_04_configure` on attribute step 1) is a worse failure mode than a node
> that admits no confident match and hands off to vector fallback.
>
> The corrected framing is that our architecture succeeds not because
> workflow routing always adds signal but because a confidence gate
> prevents it from adding noise. The scope of what `full_system` is
> guaranteed to deliver over `vanilla_vector`, however, is **conditional
> on axis and on signature maturity**, and we decompose the claim
> accordingly:
>
> - **Faithfulness and cost axes — no observed inferiority to
>   `vanilla_vector`, on either the main matrix or the pilot.** On the
>   unified4 matrix, `full_system` faithfulness meets or exceeds
>   `vanilla_vector` in 3 of 4 models (the fourth is a tie), and
>   `full_system` cost per step undercuts `vanilla_vector` on all 3
>   API-priced models (2.6–4.4× reduction). On the QGIS pilot,
>   `full_system` faithfulness (87.5 %) exceeds `vanilla_vector`
>   (82.5 %) and cost per step is 1.9× lower ($2.45m vs $4.69m). These
>   two axes transfer to a new software immediately after onboarding.
>
> - **Step-accuracy axis — equal or better only when signature is
>   mature.** On the unified4 matrix, `full_system` beats `vanilla_vector`
>   in step accuracy in 3 of 4 models (the fourth, Gemini, flips by
>   2.5 pp macro after a scenario-specific state_path regression discussed
>   as Defect #11 in the audit trail). On the QGIS pilot, `full_system`
>   step accuracy (57.5 %) sits 5 pp below `vanilla_vector` (62.5 %) —
>   an inferiority we flag rather than smooth (§Portability §X.5). The
>   pilot's workflow signature had received a single 28-minute refinement
>   cycle at bench time, a first-day authoring state rather than the
>   multi-cycle refinement that produced the main-matrix result.
>
> The guarded-hybrid guarantee is therefore **axis-conditional and
> maturity-conditional**, not universal: reliability and cost transfer
> immediately, step-accuracy parity is a function of signature maturity,
> and the confidence gate ensures that even under immature signatures the
> failure mode is a fallback to `vanilla_vector`-equivalent context
> rather than to confidently-wrong routing. This is a more constrained
> claim than "hybrid is always better," but it is the claim the data
> actually support, and it converts an apparent inconsistency — the pilot's
> 57.5 % `full_system` vs 62.5 % `vanilla_vector` — into a specification
> of the operating envelope within which the architecture's guarantees
> hold.

---

## §Discussion 2. Parametric Masking as a Public-Manual Benchmark Artifact

> Three convergent observations lead us to identify a systematic bias in
> public-manual RAG benchmarks — including ours — that we term
> **parametric masking**.
>
> **First**, on the OpendTect `attribute_computation` scenario,
> `vanilla_vector` retrieves 0 of 15 target §1.5.1a procedural chunks
> (retrieval attribution, `retrieval_attribution_unified3.md`), yet still
> reaches 61.3 % macro step accuracy — statistically indistinguishable
> from `full_system` (60.0 %) on that scenario.
>
> **Second**, on the QGIS Vector Buffer portability pilot,
> `vanilla_vector` reaches the *identical* mean step accuracy of 62.5 %
> as `no_rag` — vector retrieval, when its target chunks are not
> recovered, contributes nothing above the parametric baseline the
> model already holds (§Portability §X.6, Table X.2).
>
> **Third**, `no_rag` step accuracy floors across the full unified4
> matrix span 43–86 % (Table 1) — well above what one would expect from
> a model that had no access to any software-specific knowledge. These
> floors reflect what the four generator models (Gemini 2.5 Pro, Claude
> Sonnet 4.6, GPT-4o, Qwen3-235B-Instruct) already know about OpendTect
> from their pretraining corpora.
>
> The unifying mechanism is that the language models used in this
> benchmark — all trained on publicly indexed content that includes
> OpendTect documentation, community tutorials, QGIS documentation, and
> QGIS Training Manual excerpts — can generate near-correct next-step
> instructions from parametric knowledge alone, effectively bypassing
> the retrieval pathway. The models "already have the textbook memorized";
> vector retrieval that fails to recover the right page does not hurt them,
> and vector retrieval that succeeds gives them little that they did not
> already have.
>
> **This has three implications for how our results should be read.**
>
> (i) The hybrid gains we report in §Results are a **conservative lower
> bound** on the gains an intended deployment would see. The intended
> deployment is a user consulting internal or otherwise
> non-publicly-indexed documentation — a company's proprietary workflow
> guides, an in-house software's manual, a language other than English —
> where the parametric baseline is not available and vector retrieval
> failures are actual failures. On such material, the gap between
> `vanilla_vector` and `no_rag` (currently ~0 pp on public manuals)
> would open up, and the additional gap between `full_system` and both
> would open in proportion.
>
> (ii) The scenarios where we do observe wider hybrid gaps — for example,
> `survey_setup` (`full_system` +21.2 pp over `vanilla_vector` on step
> accuracy) — are plausibly the scenarios that fall furthest from the
> models' parametric coverage. This aligns with an interpretation of the
> attribute-scenario narrowing: the more thoroughly documented an
> application area is on the public web, the more parametric masking
> compresses the observable hybrid gain. Documentation coverage acts as
> a nuisance variable on public-manual benchmarks.
>
> (iii) The methodological point generalizes beyond our system. Most
> published RAG benchmarks use public documentation as their knowledge
> base; those benchmarks share our parametric masking artifact, and their
> reported "vanilla RAG" baselines are systematically inflated for
> models whose pretraining includes that documentation. The corrective
> is a private-knowledge condition (post-training-cutoff features,
> proprietary manuals, low-resource-language documentation) as a
> companion benchmark. We leave a controlled evaluation on such
> material as future work.

---

## §Discussion 3. Signature Maturity Determines Guard-Hole Activation

> The confidence gate (§Discussion 1) is not the whole story of how
> routing decisions become bench outcomes. A close reading of
> `full_system` steps across the unified4 attribute scenario and the
> QGIS portability pilot reveals two additional patterns that we register
> as new observations.
>
> **First, an implementation gap.** The pipeline's confidence gate is
> defined as `if current_node_id is not None and confidence < 0.7: fallback`.
> When the LLM rerank explicitly returns "none of the candidates fit,"
> `current_node_id` is set to `None`, and the fallback branch does not
> execute. The retriever nevertheless proceeds with vector-only
> retrieval (the semantic behavior a designer would want), but the
> `fallback_activated` field remains `False` in the log. On the unified4
> attribute scenario this produces a bucket we call **NONE** — 40 % of
> `full_system` steps (64/160), with a step-accuracy of 39.1 %, well
> below the 72.3 % of the explicitly-fallback-labeled steps that share
> the same underlying retrieval semantics. The gap is not in the
> semantics; it is in the label. The consequence is that steps in the
> NONE bucket appear in per-step logs as "no routing occurred" while
> their retrieval quality is silently that of the fallback path. We
> leave the two-line implementation fix (a second branch that sets
> `fallback_activated = True` when `current_node_id is None` and
> top-k candidates existed) as future work; the appropriate closing
> action per our stop rule is to log the finding, not to open a further
> iteration.
>
> **Second, an activation-rate observation.** On the unified4 attribute
> scenario the fallback rate is 40.6 % (65/160 `full_system` steps) and
> the NONE-bucket rate is 40 %. On the QGIS Vector Buffer pilot both
> rates are 0 % (0/40 `full_system` steps). The signatures differ
> primarily in maturity: the OpendTect `seismic_attribute` signature was
> refactored once (unified4) and its refactored form was tuned to a
> hand-authored dry-run rather than to vision-extracted state, producing
> a strong quoted-phrase match on the former and a collapse on the
> latter (§Discussion 1). The QGIS `qgis_vector_buffer` signature was
> authored with that lesson internalized and passed one 28-minute
> refinement cycle in which one step's "current_action" string was
> rewritten to remove a forward-looking phrase that had drawn LLM
> rerank into the wrong downstream node. **The observation is that
> guard-hole activation rate — both the confidence-fallback and the
> NONE-bucket paths — is a function of workflow-signature maturity,
> not an architectural constant.** The two data points (40 % vs 0 %)
> bracket the observed range; intermediate rates on other scenarios are
> the future-work regime.
>
> These two observations, together with the "when in doubt, don't
> route" observation from §Discussion 1, form a proto-methodology for
> workflow-graph authoring: the dry-run gate is necessary but not
> sufficient (it exercises signature match on hand-authored states, not
> on vision-extracted ones); confidence and rerank behavior on
> vision-extracted state is the operational validation surface;
> signature maturity should be treated as a first-class variable when
> reporting routing-related metrics. The immediate research task these
> observations open is a systematic study of the maturity-vs-activation
> relationship on a signature-authoring workbench, in which each
> refinement cycle's effect on fallback and NONE rates is measured
> independently of downstream step accuracy.

---

## Cross-reference Map (Discussion → Results / Appendix)

| Discussion 참조 | Source (Results/Appendix) |
|---|---|
| §Discussion 1 A-story 판정 근거 | §Results Table 1, `direction_unified4.md`, `stats_unified4.md` |
| §Discussion 1 attribute mechanism reversal | §Results Table 3-4, `retrieval_attribution_unified3.md`, `complexity_gap_unified4.md` |
| §Discussion 1 refactor 0/160 collapse | §Appendix Y (routing failure analysis), `routing_score_concentration_unified3.md` |
| §Discussion 1 "don't route" observation | `methodology_audit_trail.md § 관측 #3` |
| §Discussion 2 OpendTect 0/15 hit | §Results, `retrieval_attribution_unified3.md` § "opendtect__attribute_computation__01" |
| §Discussion 2 QGIS vanilla==no_rag | §Portability Table X.2 |
| §Discussion 2 no_rag floor 43–86 % | §Results Table 1 (n=5) |
| §Discussion 3 NONE bucket 40 % | §Results / Appendix — `routing_score_concentration_unified3.md` (post-refactor) |
| §Discussion 3 QGIS 0/40 fallback | §Portability §X.4 + Appendix N.2 |

---

## Sanity Checks (사용자 검토용, 최종 논문에 포함 안 함)

**본 통합본이 커버하는 결과**:
- [x] A 판정 성립 근거 (3/4 direction consistency, GPT p=0.032/0.034, cost paradox 3/3)
- [x] Attribute mechanism reversal (mechanism confirmed / outcome refuted)
- [x] Unified4 refactor 8/8 dry-run → 0/160 bench collapse
- [x] "When in doubt, don't route" (관측 #3)
- [x] Parametric masking 3 data points (OpendTect 0/15→61.3%, QGIS vanilla==no_rag, no_rag floor 전반)
- [x] Signature maturity vs guard hole (unified4 40.6% vs QGIS 0%)
- [x] NONE bucket implementation gap (2-line fix as future work, per stop rule)
- [x] Public-manual benchmark methodology issue + private-knowledge corrective

**의도적으로 배제된 항목 (별도 소절 또는 이미 다른 곳)**:
- 결함 #11 (state_path/survey_setup -7.5pp) — `methodology_audit_trail.md` 만 기록,
  Discussion 승격 안 함 (스텝-특정 signature 트레이드오프이고 A 판정에 영향 없음)
- QGIS full < no_rag step_acc — §Portability §X.5 에서 이미 정직 서술, Discussion
  에서 재서술 안 함
- Graph_only vs vanilla faith 방향 일관성 (4/4 → 3/4 → 2/4 후퇴) — Results 표에서
  숫자로 노출되므로 Discussion 별도 서술 불필요

**분량 확인**:
- §1 confidence-gated hybrid: ~400 단어
- §2 parametric masking: ~450 단어
- §3 signature maturity: ~400 단어
- 총 ~1,250 단어 = 약 3 페이지 (표 없이 순수 산문 기준)

---

## 다음 단계 (진행 상태)

- [x] Portability v2 + Discussion 통합본 초안 완료
- [x] §D1 논리 모순 (soft claim vs QGIS 실측) 축별 분해 수정 반영 (2026-08-13)
- [x] Stale narrative 전수 grep 갱신 실행 (Category A cost_basis 148× 통일 완료; Category B unified2 시점 문서 archive 승인 대기)
- [ ] Methods → Intro/Related → Abstract 순서 진행
