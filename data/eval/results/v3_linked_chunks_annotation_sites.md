# V3-9 annotation sites — documents citing unified2–4 full_system results

Note to attach at each site: **"unified2–4 full_system was measured without linked_chunks text: every linked_chunks id had been dangling since the 2026-07-27 re-ingest, so graph_context contained only the per-node title/description vector search (audit trail V3-9)."**

## Markdown (data/eval/results, live files only)

### data/eval/results/aggregate_by_backend.md  (4 mentions)
- section **Aggregate — model × backend** — first at line 5: `| claude | full_system | 0.417 ± 0.072 | 0.833 ± 0.072 | 0.000 ± 0.000 | 0.125 ± 0.125 | 47.42s ± 1.71 | $0.01`

### data/eval/results/complexity_gap_unified3.md  (4 mentions)
- section **Complexity-vs-gap analysis — unified3** — first at line 3: `Pre-registered prediction (see `v2_pre_registration.md § attribute prediction`): vanilla_vector should underpe`
- section **full_system − vanilla_vector on Step Acc (pp)** — first at line 7: `## full_system − vanilla_vector on Step Acc (pp)`
- section **full_system − no_rag on Step Acc (pp)** — first at line 16: `## full_system − no_rag on Step Acc (pp)`
- section **full_system − vanilla_vector on Hall Rate (pp, lower = better)** — first at line 25: `## full_system − vanilla_vector on Hall Rate (pp, lower = better)`

### data/eval/results/complexity_gap_unified4.md  (4 mentions)
- section **Complexity-vs-gap analysis — unified3** — first at line 3: `Pre-registered prediction (see `v2_pre_registration.md § attribute prediction`): vanilla_vector should underpe`
- section **full_system − vanilla_vector on Step Acc (pp)** — first at line 7: `## full_system − vanilla_vector on Step Acc (pp)`
- section **full_system − no_rag on Step Acc (pp)** — first at line 16: `## full_system − no_rag on Step Acc (pp)`
- section **full_system − vanilla_vector on Hall Rate (pp, lower = better)** — first at line 25: `## full_system − vanilla_vector on Hall Rate (pp, lower = better)`

### data/eval/results/cost_basis.md  (15 mentions)
- section **3. Gemini long_context ($283.45m / step) — arithmetic check** — first at line 81: `code's arithmetic, and the reported cost ratio to Gemini `full_system``
- section **4. Assumption to acknowledge — Gemini long-context tier pricing** — first at line 110: `step cost stays at **$283.45m** and the ratio to full_system stays at`
- section **5.2 Primary reporting unit — GPU-time / step** — first at line 175: `| full_system    | 30.9±2.1         | 123.6±8.4               | 0.03433 |`
- section **5.3 Dollar conversion — RunPod RTX 6000 Ada Secure Cloud** — first at line 202: `| full_system    | $28.85 ± 1.96 m  |`
- section **5.4 Old vs new Qwen Cost table (ratio-invariance check)** — first at line 214: `| Backend        | Old cost/step ($m) | New cost/step ($m) | Ratio to full_system (old / new) |`
- section **6. Methods paragraph draft (English)** — first at line 251: `> cost ratio to full_system from 106.6× to ~213×.`
- section **6b. Post-unified2 cost ratio evolution (append 2026-08-13)** — first at line 267: `The 106.6× long_context vs full_system cost ratio reported above is the`

### data/eval/results/direction_unified3.md  (24 mentions)
- section **step_accuracy (higher better)** — first at line 12: `| full_system vs vanilla_vector | A (0.74/0.68) | A (0.84/0.83) | A (0.64/0.61) | A (0.61/0.42) | 4/4 models: `
- section **faithfulness (higher better)** — first at line 23: `| full_system vs vanilla_vector | A (0.98/0.95) | A (0.75/0.70) | A (0.68/0.60) | B (0.39/0.45) | 3/4 models: `
- section **hallucination_rate (lower better)** — first at line 34: `| full_system vs vanilla_vector | A (0.02/0.05) | A (0.25/0.30) | A (0.33/0.40) | B (0.61/0.55) | 3/4 models: `
- section **goal_completion_rate (higher better)** — first at line 45: `| full_system vs vanilla_vector | = (0.80/0.80) | B (0.93/1.00) | B (0.73/0.80) | = (0.20/0.20) | 0/2 models: `
- section **mean_latency_sec (lower better)** — first at line 56: `| full_system vs vanilla_vector | B (37.42/11.57) | B (28.58/4.26) | B (26.68/5.11) | B (32.57/9.65) | 0/4 mod`
- section **mean_cost_usd (lower better)** — first at line 67: `| full_system vs vanilla_vector | A (0.00/0.01) | A (0.01/0.03) | A (0.01/0.02) | = (0.00/0.00) | 3/3 models: `

### data/eval/results/direction_unified4.md  (24 mentions)
- section **step_accuracy (higher better)** — first at line 12: `| full_system vs vanilla_vector | B (0.72/0.75) | A (0.85/0.84) | A (0.69/0.60) | A (0.57/0.55) | 3/4 models: `
- section **faithfulness (higher better)** — first at line 23: `| full_system vs vanilla_vector | = (0.93/0.93) | A (0.78/0.76) | A (0.69/0.63) | A (0.50/0.38) | 3/3 models: `
- section **hallucination_rate (lower better)** — first at line 34: `| full_system vs vanilla_vector | = (0.07/0.07) | A (0.23/0.24) | A (0.31/0.37) | A (0.50/0.62) | 3/3 models: `
- section **goal_completion_rate (higher better)** — first at line 45: `| full_system vs vanilla_vector | B (0.80/0.93) | = (1.00/1.00) | A (0.93/0.73) | = (0.40/0.40) | 1/2 models: `
- section **mean_latency_sec (lower better)** — first at line 56: `| full_system vs vanilla_vector | B (40.90/10.31) | B (32.37/3.86) | B (31.17/5.07) | B (35.47/9.69) | 0/4 mod`
- section **mean_cost_usd (lower better)** — first at line 67: `| full_system vs vanilla_vector | A (0.00/0.01) | A (0.01/0.03) | A (0.01/0.02) | = (0.00/0.00) | 3/3 models: `

### data/eval/results/discussion_draft_parametric_masking.md  (6 mentions)
- section **Discussion 초안 — Parametric Masking** — first at line 9: `- `routing_score_concentration_unified3.md` — full_system 의 오라우팅`
- section **1.1 검색 완전 실패에도 성능 유지** — first at line 34: `attribute 시나리오 step_acc = 61.3% (macro over 4 models), full_system 의`
- section **1.2 오라우팅 문맥에서도 성능 유지** — first at line 39: `Full_system 의 attribute 시나리오 스텝 5-7 이 정답 워크플로우가 아닌`
- section **2.1 메커니즘** — first at line 69: `- **hybrid full_system 백엔드**가 정답 컨텍스트를 받아도, 그 이득이`
- section **4. 서술 문장 (Discussion 삽입 후보)** — first at line 116: `> statistically indistinguishable from the hybrid full_system on that`

### data/eval/results/faithfulness_supplement_unified3.md  (8 mentions)
- section **Supplementary Table — 25-cell mean ± sample SD** — first at line 43: `| gemini / full_system | 98.3±3.7 | 1.7±3.7 | ✓ |`
- section **Direction-consistency reproduction (paper Table 3 rows)** — first at line 73: `| full_system vs vanilla_vector | A (98.3/95.0) | A (75.0/70.0) | A (67.5/60.0) | B (39.2/45.0) | 3/4 |`

### data/eval/results/faithfulness_supplement_unified4.md  (8 mentions)
- section **Supplementary Table — 25-cell mean ± sample SD** — first at line 43: `| gemini / full_system | 92.5±7.5 | 7.5±7.5 | ✓ |`
- section **Direction-consistency reproduction (paper Table 3 rows)** — first at line 73: `| full_system vs vanilla_vector | = (92.5/92.5) | A (77.5/75.8) | A (69.2/63.3) | A (50.0/38.3) | 3/3 |`

### data/eval/results/final_report_to_professor.md  (6 mentions)
- section **1. 판정 결과 — A (시스템 우위)** — first at line 31: `| Gemini | full_system | 72.5 | 92.5 | **$2.13m (4.4× 저렴)** |`
- section **2. 복잡 시나리오 (attribute) 결과** — first at line 47: `| Full_system 은 workflow 라우팅으로 절차 청크 확보 | 47.5% (unified3), **0%** (unified4) | 반증 (unified4) |`
- section **3.2 라우팅 가드 갭 (guarded hybrid 의 미해결 실패 모드)** — first at line 75: `Attribute full_system 160 스텝의 3-layer 분포:`

### data/eval/results/final_unified3_table.md  (4 mentions)
- section **gemini** — first at line 11: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **claude** — first at line 22: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **gpt** — first at line 33: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **qwen** — first at line 44: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`

### data/eval/results/final_unified4_table.md  (4 mentions)
- section **gemini** — first at line 11: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **claude** — first at line 22: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **gpt** — first at line 33: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **qwen** — first at line 44: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`

### data/eval/results/final_unified_table.md  (4 mentions)
- section **gemini** — first at line 9: `| metric | no_rag | vanilla_vector | full_system |`
- section **claude** — first at line 20: `| metric | no_rag | vanilla_vector | full_system |`
- section **gpt** — first at line 31: `| metric | no_rag | vanilla_vector | full_system |`
- section **qwen** — first at line 42: `| metric | no_rag | vanilla_vector | full_system |`

### data/eval/results/intermediate_report_to_professor.md  (2 mentions)
- section **2.1 사전등록 예측의 2-층 판정** — first at line 35: `- Full_system 은 `seismic_attribute` workflow 로 47.5% 라우팅 (부분 확증)`
- section **2.2 파라메트릭 마스킹 (parametric masking) 발견** — first at line 50: `- Full_system 의 오라우팅 스텝도 55/80/95% 통과 — 잘못된 문맥에서도`

### data/eval/results/methodology_audit_trail.md  (17 mentions)
- section **재채점 결과 (2026-07-15)** — first at line 86: `- gpt_unified full_system: 0.400 → 0.000`
- section **증상** — first at line 105: `Unified matrix v1에서 full_system이 vanilla_vector를 어떤 지표에서도`
- section **진단 (2026-07-15, 사용자 지시로 검증 2 수행)** — first at line 110: `Full_system routing 로그 분석:`
- section **논문에서의 위치** — first at line 174: `Latency trade-off 표: "cached vs uncached full_system"를 v2 로그에서`
- section **관측 #1 — 파라메트릭 마스킹 (parametric masking, 2026-08-07)** — first at line 567: `full_system 의 60.0% 와 사실상 동등.`
- section **관측 #2 — Dry-run 게이트 vs 벤치 실제의 vision-noise 괴리 (2026-08-10)** — first at line 670: `**결과**: unified4 attribute full_system 스텝 중 **65/160 (40.6%) 이 fallback**,`
- section **관측 #3 — "의심될 때는 라우팅하지 마라" (when-in-doubt-don't-route, 2026-08-10)** — first at line 689: `**발견 경로**: unified3 → unified4 에서 attribute full_system step_acc 가`
- section **P-4 벤치 실행 및 판정 결과 (2026-08-13, 프로젝트 마지막 벤치)** — first at line 1092: `재현 안 됨. Full_system 40 스텝 전량 `qgis_vector_buffer` workflow 로`
- section **v3 개발 루프 (2026-09-18 ~) — 목표: full_system이 vanilla_vector·vanilla_budget보다 step accuracy·총** — first at line 1198: `## v3 개발 루프 (2026-09-18 ~) — 목표: full_system이 vanilla_vector·vanilla_budget보다 step accuracy·총비용·지연에서 앞서도록 개선. `
- section **V3-9. 작업 B 준비 — 메커니즘 구현과 linked_chunks 결손 발견 (2026-09-18)** — first at line 1207: `- **발견**: `data/workflows/*.json`의 linked_chunks id 98개(OpendTect 5개 파일 92 + QGIS auto 6)가 unified2–4에 쓰인 `dat`

### data/eval/results/paper_discussion_integrated.md  (16 mentions)
- section **§Discussion 1. Confidence-Gated Hybrid: When Grounded Routing Beats Vanilla, and When It D** — first at line 19: `> criteria: on step accuracy, `full_system` beats `vanilla_vector` in`
- section **§Discussion 2. Parametric Masking as a Public-Manual Benchmark Artifact** — first at line 108: `> from `full_system` (60.0 %) on that scenario.`
- section **§Discussion 3. Signature Maturity Determines Guard-Hole Activation** — first at line 171: `> `full_system` steps across the unified4 attribute scenario and the`

### data/eval/results/paper_portability_section_draft.md  (5 mentions)
- section **X.3 Bench matrix and pre-registered pass/fail** — first at line 53: `Matrix: Gemini 2.5 Pro × {no_rag, vanilla_vector, full_system} × 5 replicates`
- section **X.4 Pre-registered predictions and outcomes** — first at line 98: `> every one of the 40 full_system steps, routing 100 % to the intended`
- section **X.5 Honest handling of `full_system` step accuracy** — first at line 111: `### X.5 Honest handling of `full_system` step accuracy`

### data/eval/results/paper_portability_section_v2.md  (8 mentions)
- section **X.3 Bench and pass/fail** — first at line 66: `Matrix: Gemini 2.5 Pro × {`no_rag`, `vanilla_vector`, `full_system`} × 5`
- section **X.4 Predictions (one-line summary; details in Appendix N.2)** — first at line 93: `> `full_system` steps, routing 100 % to the intended `qgis_vector_buffer``
- section **X.5 Honest handling of `full_system` step accuracy** — first at line 100: `### X.5 Honest handling of `full_system` step accuracy`
- section **N.2 Prediction check — detailed** — first at line 160: `| B | Fallback activation rate on `full_system` | 30–50 % | **0 %** (0/40) | Refuted |`
- section **N.3 Limitations — detailed** — first at line 194: ``full_system` step accuracy on this pilot (57.5 %) should be read`

### data/eval/results/per_scenario_unified3.md  (12 mentions)
- section **Step Acc (%) by scenario** — first at line 13: `| gemini / full_system | 90.0±13.7 | 55.0±11.2 | 77.5±13.7 |`
- section **Hall Rate (%) by scenario** — first at line 42: `| gemini / full_system | 0.0±0.0 | 5.0±11.2 | 0.0±0.0 |`
- section **Goal Comp (%) by scenario** — first at line 71: `| gemini / full_system | 80.0±44.7 | 60.0±54.8 | 100.0±0.0 |`

### data/eval/results/per_scenario_unified4.md  (12 mentions)
- section **Step Acc (%) by scenario** — first at line 13: `| gemini / full_system | 75.0±0.0 | 60.0±28.5 | 82.5±6.8 |`
- section **Hall Rate (%) by scenario** — first at line 42: `| gemini / full_system | 10.0±13.7 | 0.0±0.0 | 12.5±12.5 |`
- section **Goal Comp (%) by scenario** — first at line 71: `| gemini / full_system | 40.0±54.8 | 100.0±0.0 | 100.0±0.0 |`

### data/eval/results/preview_gemini_only.md  (4 mentions)
- section **gemini** — first at line 9: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **claude** — first at line 20: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **gpt** — first at line 31: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`
- section **qwen** — first at line 42: `| metric | no_rag | vanilla_vector | graph_only | vision_only | full_system | state_path |`

### data/eval/results/professor_report_skeleton.md  (4 mentions)
- section **1.3 사전등록 예측 (결과 보기 전 등록됨)** — first at line 36: `> full_system은 workflow 라우팅으로 절차 청크(p118~120)를 확보해`
- section **1.4 결과 (unified3 완료)** — first at line 45: `- Full_system workflow 라우팅: 부분 확증 (`seismic_attribute` 47.5%)`
- section **1.6 해석 (복잡도에 따른 격차 변화)** — first at line 75: `full_system 은 seismic_attribute workflow 로 절차 청크 확보.`

### data/eval/results/pypdf_migration_audit.md  (20 mentions)
- section **Verification (b) — End-to-end benchmark cell equivalence** — first at line 107: `**Method**: Rerun Gemini × full_system, 5 replicates, 2 scenarios (same as`
- section **(b) redefinition — pre-registered before benchmark execution** — first at line 188: `1. **Full_system Step Accuracy within reference ±1 SD**: the v2 unified2`
- section **Benchmark rerun (b): scope** — first at line 204: `- Backends: **full_system, vanilla_vector** (2 cells)`
- section **Verification (b) — results** — first at line 219: `| full_system    | r1 | 0.500 | 0.000 | 0.000 | 0.500 | 0.500 |`
- section **Pre-fixed criteria evaluation** — first at line 245: `| 1 | full_system Step Acc ∈ [49.5, 70.5] (ref 60.0 ± 1 SD) | 57.5 | **PASS** |`
- section **Verdict** — first at line 265: `- full_system Step Accuracy (57.5%) is within ±1 SD of the reference`

### data/eval/results/qgis_pilot_prereg.md  (5 mentions)
- section **2.1 Primary 성공 기준 (existence proof)** — first at line 28: `- ✅ **End-to-end 완주**: Gemini × {no_rag, vanilla_vector, full_system} × 5`
- section **예측 B: Fallback 발동률 (라우팅 가드 갭 재현)** — first at line 66: `> "full_system 스텝의 fallback 발동률이 **30-50%** 사이에서 관측될 것.`
- section **3.1 매트릭스** — first at line 99: `- **Backends**: `no_rag`, `vanilla_vector`, `full_system` (3 개 — 파라메트릭`
- section **3.2 백엔드 격리 원칙 (Q2 옵션 A)** — first at line 107: `- **full_system, graph_only, state_path** (workflow-using) 은 `hint_workflow_id``

### data/eval/results/qgis_pilot_result_report.md  (3 mentions)
- section **예측 B: Fallback 발동률 (라우팅 가드 갭 재현)** — first at line 29: `- 예측: full_system fallback rate 30-50% (unified4 attribute 40.6% 유사)`
- section **백엔드별 지표 (macro, 5 replicates)** — first at line 45: `| gemini / full_system | 57.5±6.8 | 87.5±12.5 | 100.0±0.0 | 53.6±4.9 | $2.45±0.02m |`
- section **Full_system 라우팅 분포** — first at line 47: `## Full_system 라우팅 분포`

### data/eval/results/qwen_cost_estimation.md  (3 mentions)
- section **대안: Table 표기 옵션** — first at line 67: `| qwen full_system | n/a (self-hosted, 30.9s/step) |`

### data/eval/results/reagg_supplement2_20260917.md  (12 mentions)
- section **0. 한눈에 보는 결론** — first at line 8: `- QGIS 파일럿: no_rag 62.5 → 82.5, vanilla 62.5 → 82.5, full_system 57.5 → 87.5±0.0. ‘full 57.5 < no_rag 62.5’는 조`
- section **2. QGIS 파일럿 (Gemini, 8 스텝 × 5회) ASCII 경계 재채점** — first at line 28: `| full_system | 57.5±6.8 | 87.5±0.0 | 12/40 | 12.5 | 100 | $2.45m |`
- section **3. 세 채점기로 본 full_system vs vanilla_vector 방향 (main matrix, 매크로 mean±SD, n=5)** — first at line 42: `## 3. 세 채점기로 본 full_system vs vanilla_vector 방향 (main matrix, 매크로 mean±SD, n=5)`
- section **4. Qwen <think> 잔존이 Step Acc·환각률·루프율에 준 영향** — first at line 108: `| full_system | 56.7±9.1 / 52.6±11.1 / 42.5±9.5 | 50.0±8.8 / 40.4±10.6 / 35.8±8.6 | 6.7±8.6 / 8.0±11.0 / 6.7±8`
- section **5. 종합결과보고서·초안 문장 수정 대상** — first at line 130: `| 종합결과보고서 §7 항목 1, paper_discussion_integrated §D1 | QGIS pilot full_system step_acc 57.5 < no_rag 62.5 (5pp 하`

### data/eval/results/reagg_supplement_20260917.md  (18 mentions)
- section **0. 한눈에 보는 결론** — first at line 7: `- ① 비용 절감의 원인은 라우팅이 아니라 컨텍스트 조립기의 문자 예산입니다. full_system의 vector-only 경로(fallback·NONE)조차 입력이 vanilla보다 ~6,300 `
- section **1. 경로별 입력 토큰 — full_system 스텝을 노드 유지 / fallback / NONE으로 분해** — first at line 12: `## 1. 경로별 입력 토큰 — full_system 스텝을 노드 유지 / fallback / NONE으로 분해`
- section **2.1 스텝당 호출 횟수** — first at line 75: `| vision 상태 추출 | GuideRAGPipeline.recognize_visual_state (gemini-2.5-flash) | 스크린샷당 1회. SHA-256 캐시가 프로세스(=repl`
- section **2.4 스텝당 보조 비용과 ‘보조 호출 포함 배율’** — first at line 104: `- graph_only는 vision 1회/스텝(+$2.57m)이 추가되어 Gemini $0.84m → $3.41m, state_path는 full_system과 같은 보조 호출을 씁니다. Qwen`
- section **3. 결정적 채점(step_match)과 LLM judge의 일치도** — first at line 130: `| full_system | 320 | 81.9% | 0.597 | 35 | 23 | 67.8 | 64.1 |`
- section **3.2 민감도 재채점: \b → ASCII 경계 (사후 분석, 사전등록 채점기는 그대로 둠)** — first at line 168: `| gemini | full_system | 72.5 | 84.2 | +11.7 |`
- section **4. 보너스 — Gemini × survey_setup × full_system: 5회 모두 틀린 스텝** — first at line 193: `## 4. 보너스 — Gemini × survey_setup × full_system: 5회 모두 틀린 스텝`

### data/eval/results/report_ch2_sec31_supplement_20260917.md  (7 mentions)
- section **A.1 구현 파라미터** — first at line 14: `| top-k | 벡터 검색 top_k = 5 (get_manual_context 기본값, vanilla_vector·fallback·full_system 공통). 워크플로우 노드 질의(노드 제목+`
- section **A.4 보조 호출 구조 (생성기 외 LLM 호출)** — first at line 105: `| vision 상태 추출 (recognize_visual_state) | gemini-2.5-flash | temperature=0, response_mime_type='application/js`
- section **B.1 지표 정의 (api/services/evaluation.py, 결정적 채점·LLM 개입 없음)** — first at line 162: `| fallback_rate / mean_route_confidence | fallback_activated 스텝 / 스텝 수; route_method가 있는 스텝의 rerank confidence`
- section **B.2 사전등록 판정 프레임 (v2_pre_registration.md, qgis_pilot_prereg.md)** — first at line 172: `- 방향 일관성 규칙: 지표별로 full_system > vanilla_vector인 모델 수를 세어 4/4 일관 우위, 3/4 다수 우위, 2/4 혼재, ≤1/4 역효과.`

### data/eval/results/retrieval_attribution_unified3.md  (3 mentions)
- section **Full_system routing distribution** — first at line 66: `## Full_system routing distribution`
- section **Prediction judgment** — first at line 119: `- **full_system — attribute scenario**: workflow distribution`

### data/eval/results/run_20260706T075555.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.000 | 0.000 | 0.000 | 0.000 | — | 1.000 |`

### data/eval/results/run_20260708T070651.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.250 | 0.167 | 0.083 | 0.167 | — | 0.000 |`

### data/eval/results/run_claude_r1_20260709T013202.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.500 | 0.250 | 0.083 | 0.333 | — | 0.000 |`

### data/eval/results/run_claude_r2_20260709T070215.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.417 | 0.167 | 0.083 | 0.167 | — | 0.333 |`

### data/eval/results/run_claude_r3_20260709T074928.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.583 | 0.167 | 0.167 | 0.278 | — | 0.000 |`

### data/eval/results/run_claude_unified2_r1_20260716T044752.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.125 | 0.125 | 0.833 | — | 0.500 |`

### data/eval/results/run_claude_unified2_r2_20260716T050634.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.125 | 0.125 | 0.833 | — | 0.500 |`

### data/eval/results/run_claude_unified2_r3_20260716T052513.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.875 | 0.125 | 0.000 | 0.833 | — | 0.500 |`

### data/eval/results/run_claude_unified2_r4_20260716T054311.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.125 | 0.125 | 0.833 | — | 0.500 |`

### data/eval/results/run_claude_unified2_r5_20260716T060359.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.250 | 0.125 | 0.833 | — | 0.500 |`

### data/eval/results/run_claude_unified3_r1_20260806T104335.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.292 | 0.083 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified3_r2_20260806T112244.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.875 | 0.208 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified3_r3_20260806T120218.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.292 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified3_r4_20260806T124231.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.208 | 0.042 | 1.000 | — | 0.667 |`

### data/eval/results/run_claude_unified3_r5_20260806T132047.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.250 | 0.042 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified4_r1_20260807T072511.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.292 | 0.042 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified4_r2_20260807T080539.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.208 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified4_r3_20260807T084832.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.833 | 0.208 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified4_r4_20260807T093052.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.875 | 0.208 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified4_r5_20260807T101322.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.875 | 0.208 | 0.083 | 1.000 | — | 1.000 |`

### data/eval/results/run_claude_unified_r1_20260715T092858.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.750 | 0.250 | 0.125 | 0.833 | — | 1.000 |`

### data/eval/results/run_claude_unified_r2_20260715T094401.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.375 | 0.125 | 0.667 | — | 1.000 |`

### data/eval/results/run_claude_unified_r3_20260715T100148.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.375 | 0.125 | 0.667 | — | 1.000 |`

### data/eval/results/run_claude_unified_r4_20260715T101929.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.375 | 0.125 | 0.667 | — | 1.000 |`

### data/eval/results/run_claude_unified_r5_20260715T103741.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.375 | 0.125 | 0.667 | — | 1.000 |`

### data/eval/results/run_gemini_flash_r1_20260715T074907.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.375 | 0.000 | 0.000 | 0.000 | — | 0.000 |`

### data/eval/results/run_gemini_flash_r2_20260715T081600.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.375 | 0.000 | 0.000 | 0.167 | — | 0.000 |`

### data/eval/results/run_gemini_pdfplumber_verify_r1_20260724T090103.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.500 | 0.000 | 0.000 | 0.500 | — | 0.500 |`

### data/eval/results/run_gemini_pdfplumber_verify_r2_20260724T091322.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.500 | 0.000 | 0.000 | 0.667 | — | 0.000 |`

### data/eval/results/run_gemini_pdfplumber_verify_r3_20260724T092510.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.500 | 0.000 | 0.000 | 0.500 | — | 0.500 |`

### data/eval/results/run_gemini_pdfplumber_verify_r4_20260724T093714.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.000 | 0.000 | 0.667 | — | 0.500 |`

### data/eval/results/run_gemini_pdfplumber_verify_r5_20260724T094856.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.750 | 0.125 | 0.000 | 0.667 | — | 0.500 |`

### data/eval/results/run_gemini_qgis_pilot_r1_20260813T030032.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 12: `| full_system | 0.500 | 0.000 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gemini_qgis_pilot_r2_20260813T031357.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 12: `| full_system | 0.625 | 0.250 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gemini_qgis_pilot_r3_20260813T032511.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 12: `| full_system | 0.625 | 0.250 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gemini_qgis_pilot_r4_20260813T033833.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 12: `| full_system | 0.500 | 0.000 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gemini_qgis_pilot_r5_20260813T035023.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 12: `| full_system | 0.625 | 0.125 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gemini_r1_20260708T090955.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.583 | 0.250 | 0.000 | 0.278 | — | 0.000 |`

### data/eval/results/run_gemini_r1_20260708T091110.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.583 | 0.083 | 0.000 | 0.278 | — | 0.000 |`

### data/eval/results/run_gemini_r1_20260708T092338.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.333 | 0.167 | 0.167 | 0.167 | — | 0.000 |`

### data/eval/results/run_gemini_r1_20260708T093042.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.583 | 0.167 | 0.000 | 0.333 | — | 0.000 |`

### data/eval/results/run_gemini_r1_20260709T003903.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.500 | 0.167 | 0.083 | 0.278 | — | 0.000 |`

### data/eval/results/run_gemini_unified2_r1_20260716T020926.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.000 | 0.000 | 0.667 | — | 0.500 |`

### data/eval/results/run_gemini_unified2_r2_20260716T023441.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.000 | 0.000 | 0.500 | — | 0.500 |`

### data/eval/results/run_gemini_unified2_r3_20260716T025738.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.500 | 0.125 | 0.000 | 0.500 | — | 0.500 |`

### data/eval/results/run_gemini_unified2_r4_20260716T032132.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.125 | 0.000 | 0.667 | — | 0.000 |`

### data/eval/results/run_gemini_unified2_r5_20260716T034430.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.500 | 0.000 | 0.000 | 0.500 | — | 0.000 |`

### data/eval/results/run_gemini_unified3_r1_20260806T060625.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.000 | 0.000 | 0.889 | — | 1.000 |`

### data/eval/results/run_gemini_unified3_r2_20260806T070019.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.792 | 0.000 | 0.000 | 0.778 | — | 0.333 |`

### data/eval/results/run_gemini_unified3_r3_20260806T075546.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.792 | 0.083 | 0.000 | 0.889 | — | 0.667 |`

### data/eval/results/run_gemini_unified3_r4_20260806T084922.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.000 | 0.000 | 0.778 | — | 1.000 |`

### data/eval/results/run_gemini_unified3_r5_20260806T094407.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.000 | 0.042 | 0.889 | — | 1.000 |`

### data/eval/results/run_gemini_unified4_r1_20260807T023501.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.125 | 0.000 | 0.778 | — | 0.667 |`

### data/eval/results/run_gemini_unified4_r2_20260807T033321.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.167 | 0.000 | 0.889 | — | 1.000 |`

### data/eval/results/run_gemini_unified4_r3_20260807T043128.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.875 | 0.083 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gemini_unified4_r4_20260807T052902.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.667 | 0.000 | 0.042 | 0.778 | — | 0.667 |`

### data/eval/results/run_gemini_unified4_r5_20260807T062650.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.000 | 0.000 | 0.778 | — | 0.667 |`

### data/eval/results/run_gemini_unified_r1_20260716T002529.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.250 | 0.000 | 0.667 | — | 1.000 |`

### data/eval/results/run_gemini_unified_r2_20260716T004139.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.375 | 0.125 | 0.000 | 0.500 | — | 1.000 |`

### data/eval/results/run_gemini_unified_r3_20260716T005738.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.000 | 0.000 | 0.667 | — | 1.000 |`

### data/eval/results/run_gemini_unified_r4_20260716T011353.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.500 | 0.000 | 0.000 | 0.500 | — | 0.500 |`

### data/eval/results/run_gemini_unified_r5_20260716T012921.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.625 | 0.125 | 0.000 | 0.667 | — | 0.000 |`

### data/eval/results/run_gemini_v3smoke_r1_20260917T093224.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 15: `| full_system | 1.000 | 0.000 | 0.000 | 1.000 | — | 1.000 |`

### data/eval/results/run_gpt_r1_20260709T031742.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.333 | 0.333 | 0.083 | 0.167 | — | 0.000 |`

### data/eval/results/run_gpt_r2_20260709T070641.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.583 | 0.250 | 0.000 | 0.389 | — | 0.000 |`

### data/eval/results/run_gpt_r3_20260709T075023.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.417 | 0.500 | 0.000 | 0.278 | — | 0.000 |`

### data/eval/results/run_gpt_unified2_r1_20260716T062422.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.500 | 0.000 | 0.833 | — | 0.500 |`

### data/eval/results/run_gpt_unified2_r2_20260716T064431.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.500 | 0.000 | 0.833 | — | 0.500 |`

### data/eval/results/run_gpt_unified2_r3_20260716T070423.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.625 | 0.000 | 0.833 | — | 0.000 |`

### data/eval/results/run_gpt_unified2_r4_20260716T072241.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.625 | 0.000 | 0.833 | — | 0.500 |`

### data/eval/results/run_gpt_unified2_r5_20260716T074239.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.500 | 0.000 | 0.667 | — | 0.000 |`

### data/eval/results/run_gpt_unified3_r1_20260806T135957.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.375 | 0.083 | 0.889 | — | 0.667 |`

### data/eval/results/run_gpt_unified3_r2_20260806T143705.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.333 | 0.042 | 0.889 | — | 0.667 |`

### data/eval/results/run_gpt_unified3_r3_20260806T151302.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.583 | 0.417 | 0.000 | 0.556 | — | 0.667 |`

### data/eval/results/run_gpt_unified3_r4_20260806T155047.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.542 | 0.167 | 0.000 | 0.444 | — | 1.000 |`

### data/eval/results/run_gpt_unified3_r5_20260806T162943.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.333 | 0.000 | 0.556 | — | 0.667 |`

### data/eval/results/run_gpt_unified4_r1_20260807T105516.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.292 | 0.000 | 0.778 | — | 1.000 |`

### data/eval/results/run_gpt_unified4_r2_20260807T113738.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.750 | 0.375 | 0.000 | 0.889 | — | 1.000 |`

### data/eval/results/run_gpt_unified4_r3_20260807T121717.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.667 | 0.292 | 0.000 | 0.556 | — | 0.667 |`

### data/eval/results/run_gpt_unified4_r4_20260807T130044.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.667 | 0.208 | 0.000 | 0.889 | — | 1.000 |`

### data/eval/results/run_gpt_unified4_r5_20260807T134308.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.667 | 0.375 | 0.000 | 0.556 | — | 1.000 |`

### data/eval/results/run_gpt_unified_r1_20260715T092902.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.500 | 0.500 | 0.000 | 0.167 | — | 0.500 |`

### data/eval/results/run_gpt_unified_r2_20260715T094438.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.750 | 0.250 | 0.000 | 0.500 | — | 0.000 |`

### data/eval/results/run_gpt_unified_r3_20260715T100218.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.500 | 0.500 | 0.000 | 0.167 | — | 1.000 |`

### data/eval/results/run_gpt_unified_r4_20260715T101908.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.250 | 0.375 | 0.000 | 0.000 | — | 0.500 |`

### data/eval/results/run_gpt_unified_r5_20260715T103644.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.375 | 0.375 | 0.000 | 0.000 | — | 0.000 |`

### data/eval/results/run_qwen_r1_20260709T021512.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.583 | 0.583 | 0.167 | 0.389 | — | 0.000 |`

### data/eval/results/run_qwen_r2_20260709T070556.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.167 | 0.250 | 0.000 | 0.278 | — | 0.000 |`

### data/eval/results/run_qwen_r3_20260709T074956.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 13: `| full_system | 0.250 | 0.167 | 0.167 | 0.167 | — | 0.000 |`

### data/eval/results/run_qwen_unified2_r1_20260716T080248.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.375 | 0.375 | 0.000 | 0.167 | — | 0.000 |`

### data/eval/results/run_qwen_unified2_r2_20260720T024532.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.625 | 0.000 | 0.333 | — | 0.000 |`

### data/eval/results/run_qwen_unified2_r3_20260716T091429.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.500 | 0.500 | 0.000 | 0.167 | — | 0.000 |`

### data/eval/results/run_qwen_unified2_r4_20260716T093908.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.500 | 0.000 | 0.333 | — | 0.000 |`

### data/eval/results/run_qwen_unified2_r5_20260716T100341.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.375 | 0.375 | 0.000 | 0.333 | — | 0.500 |`

### data/eval/results/run_qwen_unified3_r1_20260807T001235.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.667 | 0.708 | 0.000 | 0.667 | — | 0.000 |`

### data/eval/results/run_qwen_unified3_r2_20260806T075817.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.500 | 0.583 | 0.083 | 0.556 | — | 0.333 |`

### data/eval/results/run_qwen_unified3_r3_20260806T084439.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.667 | 0.583 | 0.083 | 0.889 | — | 0.333 |`

### data/eval/results/run_qwen_unified3_r4_20260806T093206.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.583 | 0.500 | 0.042 | 0.556 | — | 0.333 |`

### data/eval/results/run_qwen_unified3_r5_20260806T102110.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.625 | 0.667 | 0.125 | 0.778 | — | 0.000 |`

### data/eval/results/run_qwen_unified4_r1_20260807T142449.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.542 | 0.625 | 0.042 | 0.889 | — | 0.667 |`

### data/eval/results/run_qwen_unified4_r2_20260807T151241.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.583 | 0.500 | 0.083 | 0.889 | — | 0.000 |`

### data/eval/results/run_qwen_unified4_r3_20260807T155946.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.708 | 0.542 | 0.000 | 0.889 | — | 0.333 |`

### data/eval/results/run_qwen_unified4_r4_20260807T164820.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.458 | 0.417 | 0.000 | 0.222 | — | 0.333 |`

### data/eval/results/run_qwen_unified4_r5_20260807T173614.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 14: `| full_system | 0.542 | 0.417 | 0.208 | 0.556 | — | 0.667 |`

### data/eval/results/run_qwen_unified_r1_20260715T092900.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.750 | 0.625 | 0.000 | 0.833 | — | 0.000 |`

### data/eval/results/run_qwen_unified_r2_20260715T094643.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.000 | 0.375 | 0.125 | 0.000 | — | 0.000 |`

### data/eval/results/run_qwen_unified_r3_20260715T100624.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.375 | 0.500 | 0.000 | 0.667 | — | 0.500 |`

### data/eval/results/run_qwen_unified_r4_20260715T102524.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.375 | 0.500 | 0.000 | 0.333 | — | 0.500 |`

### data/eval/results/run_qwen_unified_r5_20260715T104510.md  (1 mentions)
- section **Aggregate (mean across scenarios)** — first at line 10: `| full_system | 0.250 | 0.375 | 0.000 | 0.167 | — | 0.500 |`

### data/eval/results/statistical_analysis.md  (6 mentions)
- section **step_accuracy** — first at line 165: `| full_system | 0.417 [0.375, 0.500] | 0.425 [0.325, 0.500] | 0.417 [0.250, 0.625] | 0.292 [0.125, 0.625] |`
- section **faithfulness** — first at line 174: `| full_system | 0.833 [0.750, 0.875] | 0.875 [0.750, 0.975] | 0.667 [0.500, 0.875] | 0.708 [0.375, 0.875] |`
- section **goal_completion_rate** — first at line 183: `| full_system | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |`
- section **loop_rate** — first at line 192: `| full_system | 0.125 [0.000, 0.250] | 0.050 [0.000, 0.100] | 0.000 [0.000, 0.000] | 0.083 [0.000, 0.125] |`
- section **mean_latency_sec** — first at line 201: `| full_system | 47.420 [45.654, 49.071] | 50.591 [48.518, 53.251] | 49.814 [45.653, 53.852] | 52.294 [49.602, `
- section **mean_cost_usd** — first at line 210: `| full_system | 0.010 [0.010, 0.010] | 0.002 [0.002, 0.002] | 0.006 [0.006, 0.006] | 0.000 [0.000, 0.000] |`

### data/eval/results/stats_audit.md  (56 mentions)
- section **Statistics audit — Table 2 permutation p-values** — first at line 5: `**CI direction convention**: every row that involves `full_system` reports Δ mean, Cohen's d, and the 95% boot`
- section **Full pairwise family (this audit)** — first at line 25: `- **Quality metrics only** (step_accuracy, hallucination_rate, loop_rate, goal_completion_rate): 48 tests. Thi`
- section **The four focal contrasts — corrections + effect sizes + 95% CI** — first at line 34: `| gpt | full_system vs no_rag | step_accuracy | +27.5 | +2.46 | 0.025 | 1.000 | 1.000 | 1.000 | +27.50 [+15.00`
- section **Full family — all 72 pairwise tests** — first at line 56: `| gemini | full_system vs no_rag | step_accuracy | +5.00pp | +0.57 | 0.684 | 1.000 | 1.000 | [-5.00, +15.00] |`
- section **Manuscript wording draft (English)** — first at line 127: `> **Multiple comparisons.** The full reported family comprises 72 pairwise tests (3 backend pairs × 6 metrics `

### data/eval/results/stats_audit_unified3.md  (56 mentions)
- section **Statistics audit — Table 2 permutation p-values** — first at line 5: `**CI direction convention**: every row that involves `full_system` reports Δ mean, Cohen's d, and the 95% boot`
- section **Full pairwise family (this audit)** — first at line 25: `- **Quality metrics only** (step_accuracy, hallucination_rate, loop_rate, goal_completion_rate): 48 tests. Thi`
- section **The four focal contrasts — corrections + effect sizes + 95% CI** — first at line 34: `| gpt | full_system vs no_rag | step_accuracy | +7.5 | +0.58 | 0.544 | 1.000 | 1.000 | 1.000 | +7.50 [-5.00, +`
- section **Full family — all 72 pairwise tests** — first at line 56: `| gemini | full_system vs no_rag | step_accuracy | +18.33pp | +2.78 | 0.009 | 0.626 | 0.626 | [+10.83, +25.83]`
- section **Manuscript wording draft (English)** — first at line 127: `> **Multiple comparisons.** The full reported family comprises 72 pairwise tests (3 backend pairs × 6 metrics `

### data/eval/results/stats_audit_unified4.md  (56 mentions)
- section **Statistics audit — Table 2 permutation p-values** — first at line 5: `**CI direction convention**: every row that involves `full_system` reports Δ mean, Cohen's d, and the 95% boot`
- section **Full pairwise family (this audit)** — first at line 25: `- **Quality metrics only** (step_accuracy, hallucination_rate, loop_rate, goal_completion_rate): 48 tests. Thi`
- section **The four focal contrasts — corrections + effect sizes + 95% CI** — first at line 34: `| gpt | full_system vs no_rag | step_accuracy | +18.3 | +1.97 | 0.033 | 1.000 | 1.000 | 1.000 | +18.33 [+8.33,`
- section **Full family — all 72 pairwise tests** — first at line 56: `| gemini | full_system vs no_rag | step_accuracy | +5.83pp | +0.41 | 0.559 | 1.000 | 1.000 | [-10.00, +22.50] `
- section **Manuscript wording draft (English)** — first at line 127: `> **Multiple comparisons.** The full reported family comprises 72 pairwise tests (3 backend pairs × 6 metrics `

### data/eval/results/stats_unified.md  (54 mentions)
- section **step_accuracy (higher better)** — first at line 11: `| gemini | no_rag vs full_system | 0.525 | 0.550 | -0.025 | -0.37 | 8.0 | 0.725 | 1.000 | full_system |`
- section **hallucination_rate (lower better)** — first at line 28: `| gemini | no_rag vs full_system | 0.000 | 0.100 | -0.100 | -2.14 | 4.0 | 0.110 | 0.166 | no_rag |`
- section **loop_rate (lower better)** — first at line 45: `| gemini | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |`
- section **goal_completion_rate (higher better)** — first at line 62: `| gemini | no_rag vs full_system | 0.600 | 0.500 | +0.100 | 1.00 | 4.0 | 0.377 | 1.000 | no_rag |`
- section **mean_latency_sec (lower better)** — first at line 79: `| gemini | no_rag vs full_system | 6.679 | 53.450 | -46.771 | -14.50 | 4.0 | 0.009 | 0.009 | no_rag ✓ |`
- section **mean_cost_usd (lower better)** — first at line 96: `| gemini | no_rag vs full_system | 0.001 | 0.002 | -0.002 | -12.99 | 4.0 | 0.009 | 0.009 | no_rag ✓ |`
- section **GEMINI — hybrid (full_system) vs vanilla_vector focus** — first at line 108: `# GEMINI — hybrid (full_system) vs vanilla_vector focus`
- section **Same pair, other models — is Gemini's pattern unique?** — first at line 123: `| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |`

### data/eval/results/stats_unified2.md  (58 mentions)
- section **Pipeline health — routing confidence + fallback rate** — first at line 12: `| gemini | full_system | 0.91 | 0% |`
- section **step_accuracy (higher better)** — first at line 42: `| gemini | no_rag vs full_system | 0.550 | 0.600 | -0.050 | -0.89 | 6.9 | 0.402 | 0.690 | full_system |`
- section **hallucination_rate (lower better)** — first at line 59: `| gemini | no_rag vs full_system | 0.075 | 0.050 | +0.025 | 0.43 | 6.6 | 0.684 | 1.000 | full_system |`
- section **loop_rate (lower better)** — first at line 76: `| gemini | no_rag vs full_system | 0.000 | 0.000 | +0.000 | 0.00 | inf | 1.000 | 1.000 | tie |`
- section **goal_completion_rate (higher better)** — first at line 93: `| gemini | no_rag vs full_system | 0.500 | 0.300 | +0.200 | 1.63 | 4.0 | 0.185 | 0.449 | no_rag |`
- section **mean_latency_sec (lower better)** — first at line 110: `| gemini | no_rag vs full_system | 7.075 | 34.281 | -27.206 | -16.61 | 4.3 | 0.007 | 0.009 | no_rag ✓ |`
- section **mean_cost_usd (lower better)** — first at line 127: `| gemini | no_rag vs full_system | 0.001 | 0.003 | -0.002 | -71.57 | 4.2 | 0.007 | 0.009 | no_rag ✓ |`
- section **GEMINI — hybrid (full_system) vs vanilla_vector focus** — first at line 139: `# GEMINI — hybrid (full_system) vs vanilla_vector focus`
- section **Same pair, other models — is Gemini's pattern unique?** — first at line 154: `| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |`

### data/eval/results/stats_unified3.md  (60 mentions)
- section **Pipeline health — routing confidence + fallback rate** — first at line 12: `| gemini | full_system | 0.82 | 18% |`
- section **step_accuracy (higher better)** — first at line 42: `| gemini | no_rag vs full_system | 0.558 | 0.742 | -0.183 | -4.40 | 6.3 | 0.008 | 0.009 | full_system ✓ |`
- section **hallucination_rate (lower better)** — first at line 59: `| gemini | no_rag vs full_system | 0.000 | 0.017 | -0.017 | -1.00 | 4.0 | 0.377 | 1.000 | no_rag |`
- section **loop_rate (lower better)** — first at line 76: `| gemini | no_rag vs full_system | 0.008 | 0.008 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |`
- section **goal_completion_rate (higher better)** — first at line 93: `| gemini | no_rag vs full_system | 0.800 | 0.800 | +0.000 | 0.00 | 6.6 | 1.000 | 1.000 | tie |`
- section **mean_latency_sec (lower better)** — first at line 110: `| gemini | no_rag vs full_system | 8.861 | 37.417 | -28.556 | -54.93 | 8.0 | 0.000 | 0.009 | no_rag ✓ |`
- section **mean_cost_usd (lower better)** — first at line 127: `| gemini | no_rag vs full_system | 0.001 | 0.002 | -0.001 | -126.64 | 4.3 | 0.005 | 0.009 | no_rag ✓ |`
- section **GEMINI — hybrid (full_system) vs vanilla_vector focus** — first at line 139: `# GEMINI — hybrid (full_system) vs vanilla_vector focus`
- section **Same pair, other models — is Gemini's pattern unique?** — first at line 154: `| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |`

### data/eval/results/stats_unified4.md  (58 mentions)
- section **Pipeline health — routing confidence + fallback rate** — first at line 12: `| gemini | full_system | 0.72 | 18% |`
- section **step_accuracy (higher better)** — first at line 42: `| gemini | no_rag vs full_system | 0.667 | 0.725 | -0.058 | -0.64 | 6.1 | 0.545 | 0.561 | full_system |`
- section **hallucination_rate (lower better)** — first at line 59: `| gemini | no_rag vs full_system | 0.008 | 0.075 | -0.067 | -1.94 | 4.5 | 0.124 | 0.172 | no_rag |`
- section **loop_rate (lower better)** — first at line 76: `| gemini | no_rag vs full_system | 0.000 | 0.008 | -0.008 | -1.00 | 4.0 | 0.377 | 1.000 | no_rag |`
- section **goal_completion_rate (higher better)** — first at line 93: `| gemini | no_rag vs full_system | 0.800 | 0.800 | +0.000 | 0.00 | 8.0 | 1.000 | 1.000 | tie |`
- section **mean_latency_sec (lower better)** — first at line 110: `| gemini | no_rag vs full_system | 10.629 | 40.904 | -30.274 | -36.82 | 8.0 | 0.000 | 0.009 | no_rag ✓ |`
- section **mean_cost_usd (lower better)** — first at line 127: `| gemini | no_rag vs full_system | 0.001 | 0.002 | -0.001 | -65.97 | 4.2 | 0.007 | 0.009 | no_rag ✓ |`
- section **GEMINI — hybrid (full_system) vs vanilla_vector focus** — first at line 139: `# GEMINI — hybrid (full_system) vs vanilla_vector focus`
- section **Same pair, other models — is Gemini's pattern unique?** — first at line 154: `| metric | model | full_system | vanilla | Δ | perm p | hybrid helps? |`

### data/eval/results/table1_full_sd_unified3.md  (8 mentions)
- section **Table 1 (compact) — core metrics** — first at line 20: `| gemini / full_system | 74.2±4.6 | 1.7±3.7 | 0.8±1.9 | 37.4±0.8 | $2.21±0.03m |`
- section **Appendix A — Goal Completion** — first at line 52: `| gemini / full_system | 80.0±29.8 |`

### data/eval/results/table1_full_sd_unified4.md  (8 mentions)
- section **Table 1 (compact) — core metrics** — first at line 20: `| gemini / full_system | 72.5±9.6 | 7.5±7.5 | 0.8±1.9 | 40.9±1.3 | $2.13±0.05m |`
- section **Appendix A — Goal Completion** — first at line 52: `| gemini / full_system | 80.0±18.3 |`

### data/eval/results/unified3_judgment_template.md  (24 mentions)
- section **2. Table 1 (compact) — 25 cells × 5 metrics** — first at line 55: `| gemini / full_system  | **74.2±4.6** | 1.7±3.7 | 37.4±0.8 | $2.21±0.03m |`
- section **3.2 full_system routing 분포 (attribute 시나리오)** — first at line 88: `### 3.2 full_system routing 분포 (attribute 시나리오)`
- section **3.4 종합 판정 (attribute prediction)** — first at line 141: `| 3.2 full_system workflow 라우팅 | 부분 확증 (47.5% seismic_attribute) |`
- section **해석** — first at line 185: `훨씬 빈번하므로, aggregate 25-cell 표의 full_system 우위 (Gemini`
- section **5. 3d_visualization goal_completion refinement 대조** — first at line 203: `| full_system | 70.0 |`
- section **6. Long_context 3 시나리오 확장 결과** — first at line 239: `**비교 (Gemini full_system macro-avg 74.2% step vs long_context 64.2% step)**:`
- section **7. 통계 감사 (unified3)** — first at line 262: `- **Qwen step_acc, full_system vs vanilla_vector: p = 0.025** (permutation),`
- section **8. Faithfulness 부록 (unified3)** — first at line 286: `| full_system vs vanilla_vector | 3/4 (Qwen 반대) |`
- section **9. Cost 회계 (unified3)** — first at line 300: `- **long_context vs full_system**: 106.6× → **142.9×** (§6)`
- section **10. 판정 결론 (A/B/C 프레임)** — first at line 309: `**A (시스템 우위)**: full_system 이 3+ 모델에서 방향성 우위, 최소 1 모델 p<0.10, faith 도 3+/4`

### data/eval/results/unified4_judgment_template.md  (12 mentions)
- section **1. 파이프라인 건전성** — first at line 26: `| Scenario | full_system fallback | Notes |`
- section **2. Table 1 (compact) — 25 cells** — first at line 50: `| gemini / **full_system** | 72.5±... | 7.5±... | 40±... | **$2.13m** |`
- section **4. 비열화 확인 (기존 2 시나리오)** — first at line 136: `| survey_setup | full_system | 80.0% | 78.8% | −1.3 | ✓ tolerance 내 |`
- section **6. Long_context 3 시나리오 (unified4 재실행)** — first at line 178: `**Cost 비율**: Gemini full_system $2.13m vs long_context $315.56m = **148×**`
- section **7. 통계 감사 (unified4)** — first at line 185: `- **GPT step_acc, no_rag vs full_system: perm p = 0.032, Δ = +18.3pp** ✓`
- section **8. Cost 회계 (unified4)** — first at line 196: `| Model | full_system | vanilla_vector | 배율 (vanilla / full) |`

### data/eval/results/v2_pre_registration.md  (13 mentions)
- section **스토리 A — 시스템 우위 ("hybrid가 이긴다")** — first at line 30: `- full_system이 vanilla_vector보다 step_accuracy 또는 goal_completion에서 **최소 3/4 모델에서 방향성 우위** (개별 p 무관)`
- section **방향 일관성 스코어링 규칙 (n=5 보완)** — first at line 77: `- `full_system > vanilla` (더 나은 방향)인 모델 수 카운트`
- section **사전 등록된 "예상 밖" 경계선** — first at line 86: `- 어느 모델이든 no_rag가 full_system을 step_accuracy에서 유의하게 이김 (RAG가 오히려 방해)`
- section **예측 진술 (unified3 결과 보기 전에 못박음)** — first at line 125: `> full_system은 workflow 라우팅으로 절차 청크(p118~120)를 확보해`
- section **예상 정량 결과** — first at line 145: `| full_system Step Acc (attribute) | vanilla 대비 유의한 우위 | 예: full 55%+ vs vanilla 30% |`
- section **예측 확증 판정 기준 (사전 고정)** — first at line 157: `3. **full_system의 라우팅**: attribute 시나리오의 full_system`
- section **비열화 조건 (기존 시나리오 보호)** — first at line 288: `- 기존 2 시나리오의 `full_system`, `graph_only`, `state_path` step_acc`

### data/eval/results/workflow_node_signature_audit.md  (3 mentions)
- section **Impact on `unified2` routing distribution** — first at line 28: `Audit of the 5 replicates × 4 models × 2 scenarios full_system +`
- section **Consequence for benchmark comparability** — first at line 49: `downstream retrieval content in `full_system` / `state_path` cells.`

## Word documents (~/Downloads)

### ACAGS_manuscript_template_GeoLens.docx  (4 mentions)
- p34 · **4.2 Retrieval backends** — `7 backends: no_rag, vanilla_vector, graph_only, vision_only, full_system, state_path, long_context (Gemini onl`
- p46 · **4.6 Cost basis** — `All costs were computed from token counts using base list prices (July 2026; Gemini 2.5 Pro $1.25/$10.00, Clau`
- p48 · **5. Results** — `Order: 5.1 main comparison (Table 1, full_system vs vanilla: 3/1/0, 3/0/1, 3/0/0; macro +13.1pp / −8.1pp / −60`
- p63 · **Data and code availability** — `The full evaluation pipeline, workflow graphs, scenario definitions, deterministic scorers, per-replicate logs`

### ACAGS_manuscript_template_GeoLens_영어.docx  (4 mentions)
- p31 · **4.2 Retrieval backends** — `7 backends: no_rag, vanilla_vector, graph_only, vision_only, full_system, state_path, long_context (Gemini onl`
- p43 · **4.6 Cost basis** — `All costs were computed from token counts using base list prices (July 2026; Gemini 2.5 Pro $1.25/$10.00, Clau`
- p45 · **5. Results** — `Order: 5.1 main comparison (Table 1, full_system vs vanilla: 3/1/0, 3/0/1, 3/0/0; macro +13.1pp / −8.1pp / −60`
- p60 · **Data and code availability** — `The full evaluation pipeline, workflow graphs, scenario definitions, deterministic scorers, per-replicate logs`

### GeoLens_종합결과보고서_final.docx  (15 mentions)
- p34 · **1.2 평가 대상** — `Core 6: no_rag, vanilla_vector, graph_only, vision_only, full_system, state_path`
- p42 · **1.3 집계 단위** — `실행 = replicate (시나리오 평균): 시나리오 지표를 실행 내 평균. e.g. Gemini/full_system replicate 값 = 3 시나리오 평균.`
- p84 · **3.4 통계 유의성 (permutation p, n=5 replicates × 10K resample, **미보정**)** — `해석: n=5 small-sample 한계로 대부분 non-sig. Primary A 조건 (최소 1 모델 p<0.10) 은 GPT full_system 관련 2 건으로 충족.`
- p88 · **3.5 비용 구조 분해** — `Cost paradox (API-paid 3 모델, full_system 이 vanilla 보다 저렴):`
- p133 · **5.2 벤치 결과 (macro, n=5)** — `주요 관찰: vanilla == no_rag 62.5% 완전 동률 (파라메트릭 마스킹 극단 사례, §6.2 참조). full_system step_acc 는 5.0 pp 하회 (§7 정직성 항목).`
- p139 · **5.3 예측 대조** — `Full_system 40 스텝 전량 qgis_vector_buffer workflow 정확 라우팅 (100%). 통과율 57.5%.`
- p153 · **6.1 Confidence-gated Hybrid: 축별 조건부 우위 (§D1)** — `Mechanism reversal 정직 서술: attribute 시나리오 사전등록 예측의 절반 (mechanism: vanilla 0/15 hit) 은 확증되었으나, 절반 (outcome: 격차 확`
- table1 · **(table)** — `사이클 | 시점 | 주요 목적 · 변경 | 판정 | 발견된 결함/관측`
- table2 · **(table)** — `Cell (Model / Back | Step Acc (%) ↑ | Hall (%) ↓ | Loop (%) ↓ | Latency (s) ↓ | Cost/step ($) ↓`
- table6 · **(table)** — `Model | Contrast | Metric | Δ | perm p`
- table10 · **(table)** — `Backend | Step Acc (%) | Faith (%) | Goal Comp (%) | Latency (s) | Cost/step`
- table12 · **(table)** — `# | 항목 | 논문 프레임`

