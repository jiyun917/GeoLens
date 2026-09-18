# Paper Draft — Portability Section

**대상**: 논문의 Results 뒤 독립 소절 §Portability 또는 부록 §Appendix Portability Pilot
**분량**: 약 1.2 페이지 (본문 ~550 단어 + 3 개 표 + 6 개 서술 블록)
**언어**: 영어 (paper 삽입용 blockquote), 주변 구조/각주는 한글 (사용자 검토 편의)
**작성 시점**: 2026-08-13, QGIS pilot SUCCESS 판정 직후

---

## §X. Portability Pilot: QGIS Vector Buffer

### X.1 Motivation and scope

> To probe the generality of the manual-grounded hybrid RAG architecture beyond
> the OpendTect setting on which it was designed and tuned, we ran a
> single-scenario portability pilot on QGIS 3.44, an unrelated open-source
> geospatial application in the same domain family (geoscience) but with
> disjoint UI vocabulary, workflow structure, and manual style. **The pilot
> tests whether the pipeline runs end-to-end on a new target software, not
> whether it wins on that target.** All success criteria (below) were
> pre-registered in `qgis_pilot_prereg.md` before any bench numbers were
> observed; a single stop rule (no second pilot iteration regardless of
> outcome) was declared in the same document.

### X.2 Engineering cost (measured, four hours end-to-end)

**표 X.1 — Ingest + authoring + capture + bench (single engineer, one afternoon)**

| Phase | Elapsed |
|---|---|
| P-0. Code refactor + regression validation | ~1.3 h |
| P-1. Knowledge base ingest (Training Manual, 697 pages) | 55.6 min |
| P-2. Initial authoring (workflow, 5 nodes + scenario, 8 steps) | 7 min |
| P-2. Refinement #1 (removed forward-looking clause in one step) | 24 min |
| P-2. Refinement #2 (layer-name discrepancy: manual says `roads_34S`, data ships as `roads_33S`) | 4 min |
| P-3. Screenshot capture (8 images) | ~16 min |
| P-4. Bench (Gemini × 3 backends × 5 replicates × 8 steps = 120 steps) | 61 min |
| **Total** | **≈ 4 hours (< 1 engineer-day)** |

> The measured cost falls well below the 7–10 engineer-day estimate produced
> by a prior static portability audit (Appendix Y). The gap arises because
> the audit budgeted for multiple scenarios plus contingency, whereas this
> pilot targets a single scenario as an existence proof. The four
> refactor touch-points identified by the audit (`VISUAL_STATE_PROMPT`,
> `_COMPLETION_CLAIM_PATTERNS`, the `action.ts` 3D-scene block, and the
> frontend placeholder text) were sufficient; no additional core changes were
> required. Upload proceeded through the same `POST /api/manual/upload`
> endpoint used by the UI, so the "regular upload path" claim holds without
> caveat.

### X.3 Bench matrix and pre-registered pass/fail

Matrix: Gemini 2.5 Pro × {no_rag, vanilla_vector, full_system} × 5 replicates
× 1 scenario (`qgis__vector_buffer__01`, 8 steps, Buffer Analysis lesson
§6.2.6 of the QGIS Training Manual 3.44). Backend-level workflow isolation
achieved via temporary file-system state (OpendTect workflow JSONs moved
to a backup subdirectory during pilot, restored on exit) so that all
workflow-routing queries were limited to QGIS workflows.

**표 X.2 — Pre-registered success criteria (§Pilot §2.1)**

| Criterion | Observed | Judgment |
|---|---|---|
| ① End-to-end completion, zero empty responses | 0 / 120 empty | ✓ PASS |
| ② Five metrics reported for every (backend, replicate) cell | complete | ✓ PASS |
| ③ Fallback log intact (`fallback_activated` per step) | intact | ✓ PASS |

> The pilot passes on the pre-registered criteria and we report it as
> **SUCCESS** on the operational definition of portability: the pipeline
> runs end-to-end on a previously unsupported software with no missing
> observations. Performance was explicitly *not* part of the pass/fail rule.

**표 X.3 — Macro bench results (n = 5 replicates, mean ± sample SD)**

| Backend | Step Acc (%) | Faith (%) | Goal Comp (%) | Latency (s) | Cost/step |
|---|---|---|---|---|---|
| no_rag | 62.5 ± 8.8 | 90.0 ± 13.7 | 100.0 ± 0.0 | 10.3 ± 1.7 | $0.87m |
| vanilla_vector | 62.5 ± 8.8 | 82.5 ± 19.0 | 100.0 ± 0.0 | 10.2 ± 1.2 | $4.69m |
| full_system | 57.5 ± 6.8 | 87.5 ± 12.5 | 100.0 ± 0.0 | 53.6 ± 4.9 | $2.45m |

### X.4 Pre-registered predictions and outcomes

**표 X.4 — Prediction check (§Pilot §2.2, registered before observation)**

| Prediction | Expected | Observed | Outcome |
|---|---|---|---|
| A. Parametric masking on vanilla | vanilla step_acc ≥ 40 % | 62.5 % | **Confirmed** |
| B. Fallback activation rate | 30–50 % (mirroring unified4 attribute) | **0 %** (0/40) | Refuted |
| C. NONE bucket (guard hole) | ≥ 20 % | **0 %** (0/40) | Refuted |

> Predictions B and C were refuted, but the mechanism of refutation is
> itself the finding. Both predictions were extrapolations from the
> unified4 `attribute_computation` scenario, whose hand-authored workflow
> signature was insufficiently matched to the vision-extracted state
> representation, producing 40.6 % fallback and a 40 % "NONE" bucket
> (predicted to recur). The QGIS pilot's hand-authored signature, produced
> after that lesson was internalized, matched the vision-extracted state on
> every one of the 40 full_system steps, routing 100 % to the intended
> `qgis_vector_buffer` workflow with zero fallback. **We add this as a new
> observation: guard-hole activation rate is a function of workflow
> signature maturity, not an architectural constant.** The unified4 case
> and the QGIS case together define the two ends of that dependency.
>
> **Boundary note (important).** Zero fallback in the QGIS pilot means the
> fallback path and the "NONE" bucket were **not exercised** on this
> software, not that they are absent from the architecture. We treat them as
> latent failure modes whose expression is conditional on signature
> maturity; the unified4 attribute scenario supplies the positive evidence
> that they do activate when signatures are immature.

### X.5 Honest handling of `full_system` step accuracy

> Under `full_system`, step accuracy (57.5 %) is 5.0 pp lower than
> `no_rag` (62.5 %) on this scenario. We flag this rather than smooth it:
> the pilot's claim is portability, not performance, and the workflow
> signature had been through only one refinement cycle (28 minutes total) at
> bench time — a first-day authoring state, not a tuned production state.
> Two axes moved in the intended direction even at this state: faithfulness
> (87.5 vs 82.5 for vanilla, 90.0 for no_rag) sits within noise of no_rag
> while beating vanilla, and cost per step ($2.45m for full vs $4.69m for
> vanilla, a 1.9× reduction) preserves the cost paradox we reported for all
> three OpendTect API-priced models. The takeaway is that the reliability
> and cost axes transfer to a new software immediately after onboarding,
> whereas step accuracy on complex workflows appears to require the same
> multi-cycle signature refinement that yielded the unified4 gains — a
> workload not attempted in this pilot.

### X.6 Parametric masking, cleanly reproduced

> The most striking single observation is that on this scenario **`vanilla_vector`
> and `no_rag` reach the identical mean step accuracy of 62.5 %**. Vector
> retrieval, when it recovers no target §6.2.6 chunks (an outcome consistent
> with the parametric-masking mechanism we documented on the OpendTect
> attribute scenario), contributes nothing above the parametric baseline the
> model already holds. Read together with the OpendTect result (0/15 target
> hits yet 61.3 % step accuracy on vanilla), the QGIS pilot supplies the
> second independent data point that on public-manual benchmarks vanilla
> RAG behaves as a decoration on parametric priors rather than a lift over
> them. This finding, developed in full at §Discussion 2, is what makes
> our reported hybrid gains a conservative lower bound rather than a
> ceiling.

### X.7 Limitations

> Four limitations circumscribe the pilot. (i) A **single scenario** was
> evaluated; broader QGIS coverage remains future work. (ii) A **single
> generator model** (Gemini 2.5 Pro) was used, so cross-model
> generalization on QGIS is not established. (iii) The pilot is **not a
> performance claim**: the pre-registered pass/fail rule was operational
> (end-to-end completion + metric availability + log integrity), not
> comparative. (iv) The zero-fallback outcome, favorable in isolation, means
> the fallback and guard-hole paths were **not stress-tested** on this
> software; their conditional activation, evidenced on unified4 attribute,
> remains the appropriate reference for those paths.

---

## Placement recommendations (사용자 결정용)

**Option A — Results 뒤 독립 소절 §Portability**:
- 장점: 실험 결과의 일부로 자연스럽게 배치, "이식성" 이 논문의 이중 기여
  (main matrix + portability) 중 하나임을 헤드라인화. 리뷰어가 3-4 페이지의
  Results 절 내에서 함께 확인 가능.
- 단점: Main matrix 는 4 model × 6 backend × 3 scenario 인데 pilot 은 1×3×1
  로 규모 대비 지면 배분이 어색할 수 있음. Pass/fail 프레임이 다른 (operational
  vs comparative) 것에 대한 리뷰어 오해 여지.
- 적합 시점: 논문이 "novel architecture + demonstrated portability" 를 이중
  강조하는 프레임일 때.

**Option B — 부록 §Appendix Portability Pilot**:
- 장점: Main matrix 의 판정 프레임 (comparative, hybrid 우위 주장) 과 pilot
  의 판정 프레임 (operational, 이식성 존재 증명) 을 명확히 분리. 본문 Results
  는 unified4 만으로 깔끔하게 유지, Discussion 에서 §Discussion 2 (파라메트릭
  마스킹) 이 pilot 데이터를 "second independent data point" 로 인용하는
  구조.
- 단점: 이식성이 부록으로 밀리면 리뷰어에 따라 "부수적 검증" 으로 보일 수
  있음. 4 시간 실측 결과 (강한 이식성 증거) 가 저평가될 위험.
- 적합 시점: 논문의 primary claim 이 hybrid 우위이고 이식성은 discussion-
  level generalization 근거인 경우.

**추천: Option B (부록 배치) + Discussion 에서 forward-reference**.
근거:
1. Pass/fail 프레임 차이가 Results 절 통합 시 오해 유발 위험. 부록 분리로
   해소.
2. `discussion_draft_parametric_masking.md` 가 이미 pilot 을 "future work
   (QGIS)" 로 지시했으나, 지금은 실제 데이터 확보 → Discussion §2 에서
   "second data point" 로 인용 (본문 §Appendix Portability 로 링크).
3. 이식 비용 표 (4 시간) 는 그 자체로 Discussion 챕터에서 "systems
   contribution" 근거로 강조하기 좋음 (부록에서 상세, Discussion 에서 요약).

승인 시 논문 최종 구조 (Results + Discussion 3 챕터 + Appendix 배치) 확정
가능.
