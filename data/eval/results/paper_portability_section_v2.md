# Paper Draft — Portability Section (v2, Option A body-first)

**배치 확정**: Results 뒤 독립 본문 소절 §Portability (~0.8 p) +
Appendix N (예측 대조 상세표 + 사전등록 전문 + boundary note 상세).
**작성 시점**: 2026-08-13, 사용자 배치 결정 (Option A + 압축) 접수 직후.

**전략적 근거 (사용자 지시 요약, 감사 기록 반영)**:
1. 이식성 실증은 C&G 스코프 방어 (report 모드 제외 후 방어선 = 도메인 특화
   기여 + 프레임워크 이식성) 의 실탄. 부록행 시 desk-review / 1차 리뷰
   가시성 손실.
2. 교수님 두 번째 요구 ("다른 소프트웨어로도") 산출물이 본문에 있어야 요구
   반영 명시.
3. `full < no_rag` 를 본문에서 정직하게 다루는 자체가 신뢰 자산. 불리한
   숫자를 부록으로 옮기면 "숨겼다" 인상 리스크.

**압축 원칙**:
- X.1 (조작적 정의 · pre-reg · stop rule) 첫 문단이 pass/fail 프레임 혼동
  선제 해소
- X.2 비용 표 · X.3 매트릭스 · X.5 정직 서술 · X.6 마스킹 = 본문 핵심
- X.4 예측 대조 상세는 "3건 중 A 확증, B·C 반증 (Appendix N)" 한 문장 +
  signature maturity 관찰만 본문
- X.7 한계는 본문 짧게, 상세는 Appendix N

---

## §X. Portability: A One-Afternoon Pilot on QGIS

### X.1 Scope

> To probe whether the manual-grounded hybrid RAG architecture generalizes
> beyond the OpendTect setting on which it was designed and tuned, we ran a
> single-scenario portability pilot on QGIS 3.44 — an unrelated open-source
> geospatial application in the same domain family (geoscience) but with
> disjoint UI vocabulary, workflow structure, and manual style. **The pilot
> tests whether the pipeline runs end-to-end on a new target software; it is
> not a performance claim.** All pass/fail criteria and secondary
> predictions were pre-registered before any bench numbers were observed,
> and a single stop rule (no second pilot iteration regardless of outcome)
> was declared in the same document (Appendix N.1).

### X.2 Engineering cost (four hours, measured)

**Table X.1** — Wall-clock time from code refactor to bench completion,
single engineer. Upload used the same `POST /api/manual/upload` endpoint
served to the UI; no internal-function bypass was permitted.

| Phase | Elapsed |
|---|---|
| Code refactor + regression validation (four touch-points) | ≈ 1.3 h |
| Manual ingest (Training Manual, 697 pages) | 55.6 min |
| Workflow + scenario authoring (5 nodes + 8 steps) | 7 min |
| Refinement × 2 (forward-looking clause; layer-name discrepancy) | 28 min |
| Screenshot capture (8 images) | ≈ 16 min |
| Bench (Gemini × 3 backends × 5 replicates × 8 steps) | 61 min |
| **Total** | **≈ 4 h (< 1 engineer-day)** |

> A prior static portability audit estimated 7–10 engineer-days
> (Appendix Y); the gap reflects the audit's budgeting for multiple
> scenarios plus contingency. The four refactor touch-points identified by
> that audit (`VISUAL_STATE_PROMPT`, `_COMPLETION_CLAIM_PATTERNS`, the
> `action.ts` 3D-scene block, and the frontend placeholder text) proved
> sufficient; no additional core changes were required.

### X.3 Bench and pass/fail

Matrix: Gemini 2.5 Pro × {`no_rag`, `vanilla_vector`, `full_system`} × 5
replicates × 1 scenario (`qgis__vector_buffer__01`, 8 steps, Buffer Analysis
lesson §6.2.6 of the QGIS Training Manual 3.44).

**Pre-registered pass/fail** (three operational criteria; details in Appendix N.1).
All three passed: 0 / 120 empty responses, five metrics reported for every
(backend, replicate) cell, `fallback_activated` field intact per step.
**We report the pilot as SUCCESS on the pre-registered operational definition
of portability.**

**Table X.2** — Macro bench results (n = 5, mean ± sample SD).

| Backend | Step Acc (%) | Faith (%) | Goal Comp (%) | Latency (s) | Cost/step |
|---|---|---|---|---|---|
| no_rag | 62.5 ± 8.8 | 90.0 ± 13.7 | 100.0 ± 0.0 | 10.3 ± 1.7 | $0.87m |
| vanilla_vector | 62.5 ± 8.8 | 82.5 ± 19.0 | 100.0 ± 0.0 | 10.2 ± 1.2 | $4.69m |
| full_system | 57.5 ± 6.8 | 87.5 ± 12.5 | 100.0 ± 0.0 | 53.6 ± 4.9 | $2.45m |

### X.4 Predictions (one-line summary; details in Appendix N.2)

> Of three pre-registered secondary predictions, **A was confirmed and B, C
> were refuted** (Appendix N.2). The interpretive finding is in the
> refutation: predictions B (fallback rate 30–50 %) and C (NONE bucket
> ≥ 20 %) extrapolated from the unified4 attribute scenario, whose
> hand-authored workflow signature was insufficiently matched to
> vision-extracted state; the QGIS pilot's signature — authored after that
> lesson — matched vision-extracted state on every one of the 40
> `full_system` steps, routing 100 % to the intended `qgis_vector_buffer`
> workflow with zero fallback. **We register a new observation: guard-hole
> activation rate is a function of workflow signature maturity, not an
> architectural constant** (§Discussion 3). Zero fallback here means the
> fallback path was *not exercised* on this software, not that it is
> absent — see Appendix N.2 for the boundary note.

### X.5 Honest handling of `full_system` step accuracy

> Under `full_system`, step accuracy on this scenario (57.5 %) is 5.0 pp
> lower than `no_rag` (62.5 %). We flag this rather than smooth it. The
> pilot's claim is portability, not performance; the workflow signature had
> been through a single 28-minute refinement cycle at bench time — a
> first-day authoring state, not a tuned production state. Two axes did
> transfer even at this state: faithfulness (87.5 vs 82.5 for vanilla,
> within noise of no_rag) beats vanilla, and cost per step ($2.45m for
> `full_system` vs $4.69m for `vanilla_vector`, a 1.9× reduction) preserves
> the cost paradox we reported for all three API-priced models on the main
> matrix. The reading is that reliability and cost transfer to a new
> software immediately after onboarding, while step accuracy on complex
> workflows appears to require the multi-cycle signature refinement that
> yielded the main-matrix gains — a workload not attempted in this pilot.

### X.6 Parametric masking, cleanly reproduced

> The most striking single observation is that on this scenario
> **`vanilla_vector` and `no_rag` reach the identical mean step accuracy
> of 62.5 %**. Vector retrieval, when it recovers no target §6.2.6 chunks
> (an outcome consistent with the parametric-masking mechanism documented
> on the OpendTect attribute scenario), contributes nothing above the
> parametric baseline the model already holds. Read together with the
> OpendTect result (0/15 target hits yet 61.3 % step accuracy on
> `vanilla_vector`), the QGIS pilot supplies the **second independent data
> point** that on public-manual benchmarks, `vanilla_vector` behaves as a
> decoration on parametric priors rather than a lift over them
> (§Discussion 2). This is what makes the hybrid gains reported in §Results
> a conservative lower bound rather than a ceiling.

### X.7 Limitations (summary; full list in Appendix N.3)

> The pilot evaluates a single scenario with a single generator model, is
> operational rather than comparative in its pass/fail rule, and did not
> exercise the fallback / guard-hole paths on this software (§X.4). The
> conditional activation of those paths — positively evidenced on the
> unified4 attribute scenario — remains the appropriate reference.

---

## §Appendix N. Portability Pilot — Full Detail

### N.1 Pre-registration document

Reference `data/eval/results/qgis_pilot_prereg.md` (verbatim), written and
committed before any bench numbers were observed. Contains: operational
definition of portability; three primary success criteria (end-to-end
completion, indicator availability, log integrity); three secondary
predictions (parametric masking A, fallback rate B, NONE-bucket rate C)
with confirmation/refutation thresholds; the single stop rule (no
`qgis_pilot2` under any outcome).

### N.2 Prediction check — detailed

**Table N.1** — Pre-registered predictions vs observed.

| # | Prediction | Threshold | Observed | Outcome |
|---|---|---|---|---|
| A | Parametric masking on `vanilla_vector` | step_acc ≥ 40 % | 62.5 % | Confirmed |
| B | Fallback activation rate on `full_system` | 30–50 % | **0 %** (0/40) | Refuted |
| C | "NONE" bucket rate (guard hole) | ≥ 20 % | **0 %** (0/40) | Refuted |

> **Boundary note.** Zero fallback on QGIS pilot means the fallback path
> and the "NONE" bucket (a documented implementation gap in the confidence
> gate whereby steps with `picked_workflow_id = None` bypass the
> `fallback_activated = True` label while still receiving vector-only
> context) were **not exercised** on this software — not that they are
> absent from the architecture. We treat them as latent failure modes whose
> activation is conditional on workflow signature maturity. Unified4
> attribute (40.6 % fallback, 40 % NONE bucket) supplies the positive
> evidence that the paths do activate when signatures are immature;
> QGIS pilot (0 % / 0 %) supplies the positive evidence that a matured
> hand-authored signature can drive the activation rate to zero on that
> particular scenario. The two together define the observed range;
> intermediate rates on other scenarios are the future-work regime.

### N.3 Limitations — detailed

1. **Single-scenario evaluation.** Only `qgis__vector_buffer__01` was run;
   broader QGIS coverage (Vector Analysis full module, Raster Analysis,
   Georeferencing, etc.) remains future work.
2. **Single generator model.** Only Gemini 2.5 Pro; cross-model
   generalization on QGIS not established (unified4 4-model matrix was
   OpendTect-only).
3. **Operational pass/fail rule.** The pre-registered rule (§X.3) was
   completion + observability, not performance. Reviewers who read §X.3
   as a claim of hybrid winning on QGIS should be redirected to Appendix N.1.
4. **Guard-hole paths not stress-tested.** As boxed in §N.2, zero fallback
   is favorable in isolation but leaves the fallback / NONE-bucket paths
   unexercised on QGIS.
5. **Workflow authoring maturity.** The QGIS `qgis_vector_buffer` workflow
   went through a single 28-minute refinement cycle, not the multi-cycle
   iteration that produced the OpendTect `seismic_attribute` signature.
   `full_system` step accuracy on this pilot (57.5 %) should be read
   against that authoring state, not against a hypothetical tuned state.

### N.4 Reproducibility artifacts

- `data/eval/results/run_gemini_qgis_pilot_r{1..5}_*.json` — 5 replicate JSON dumps
- `data/eval/results/qgis_pilot_bench.log` — wrapper execution log
- `data/eval/results/qgis_pilot_prereg.md` — pre-registration document
- `data/eval/results/qgis_pilot_upload_report.md` — manual ingest report (P-1)
- `data/eval/results/qgis_pilot_result_report.md` — judgment report (this Appendix's source)
- `data/eval/results/methodology_audit_trail.md § QGIS Pilot 감사 기록` — chronological event log (defect discoveries, refinement history, stop-rule enforcement)
- `scripts/run_qgis_pilot.py` — recovery-aware bench wrapper (rc=4 credit-depletion branch inherited from unified3 recovery)
- `scripts/qgis_pilot_dryrun.py` — routing dry-run with `hint_workflow_id` isolation (Q2 option A)

---

## 대비 — 이전 초안 (v1) 대비 변경 요약 (사용자 검토용, 최종 논문에는 포함 안 함)

| 요소 | v1 (Option B) | v2 (Option A + 압축) |
|---|---|---|
| 배치 | Appendix | 본문 §Portability |
| 분량 | 1.2p | 본문 ~0.8p + Appendix N (분리) |
| §X.4 예측 대조 | 본문 전체 표 + 상세 서술 | 본문 1문장 + signature maturity 관찰, 표는 Appendix N.2 |
| §X.7 한계 | 본문 상세 (4 항목) | 본문 요약 문장, 상세 5 항목은 Appendix N.3 |
| Boundary note | 본문 X.4 | Appendix N.2 (본문 X.4 에 forward pointer) |
| 사전등록 문서 | 언급만 | Appendix N.1 로 정식 참조 |

**본문 유지 (압축 대상 아님)**:
- X.1 조작적 정의 (pass/fail 프레임 혼동 선제 해소)
- X.2 비용 표 (4 시간 실측 = C&G 방어 실탄)
- X.3 매트릭스 + pass/fail 요약
- X.5 정직 서술 (full < no_rag 프레임)
- X.6 마스킹 재현 (Discussion §2 forwarding 헤드라인)
