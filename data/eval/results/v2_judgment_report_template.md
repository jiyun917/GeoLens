# V2 판정 보고서 — 4모델 × 6백엔드 unified2 최종 결과

**작성 시점**: v2 실행 완료 직후 (Gemini + Claude + GPT + Qwen 각 5 replicate 완성)
**판정 기준 참조**: `v2_pre_registration.md`
**보고서 구조**: 각 섹션의 `[TBD]`를 v2 스크립트 산출물로 채우면 판정 근거 완성.

---

## 1. 파이프라인 건전성 (4모델 mini-checkpoint 결과)

| 모델 | Empty | 3-gate 발동 | Fallback | Flash aux calls | 상태 |
|------|-------|-------------|----------|-----------------|------|
| gemini | 0/240 | 30/30 ✓ | 0/40 (0%) | 490+ 정상 | ✅ PASS |
| claude | 0/240 | 30/30 ✓ | 0/40 (0%) | 495 정상 | ✅ PASS |
| gpt | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| qwen | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

**로그 스캔 종합**: 429 = [TBD], EMPTY = [TBD], RESOURCE_EXHAUSTED = [TBD].

---

## 2. Final unified matrix (mean±std, n=5 per cell)

`scripts/build_final_table.py --tag unified2` 산출물 삽입.

### gemini
[TBD — 표 삽입]

### claude
[TBD]

### gpt
[TBD]

### qwen
[TBD]

**Goal Comp 각주 재확인**: 3d_visualization의 최종 스크린샷이 penultimate
state이므로 어떤 백엔드도 이 시나리오에서 3-gate 통과 불가. Goal Comp
컬럼은 사실상 survey_setup 단독 (n=5, not n=10). 이 컬럼의 값 차이는
축소된 통계력 아래에서 해석.

---

## 3. Direction consistency (사전등록의 primary 판정 기준)

`scripts/direction_consistency.py --tag unified2` 산출물 삽입.

핵심 pair × 지표 요약 (사전등록 지시 반영):

| Pair | step_acc | faithfulness | goal_comp (n=5 완화) | latency | cost |
|------|----------|--------------|----------------------|---------|------|
| full_system vs vanilla | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| full_system vs no_rag | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| graph_only vs full_system | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| graph_only vs vanilla | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |
| state_path vs full_system | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] |

**방향 일관성 라벨**:
- 4/4 = 보편적 우위 (universal)
- 3/4 = 다수 우위 (majority)
- 2/4 = 혼재 (mixed)
- ≤1/4 = A 열위 (A loses)

---

## 4. Pairwise significance (보조 지표)

`scripts/stats_unified.py --tag unified2` 산출물의 요약. n=5에서 유의성은
관성적으로 낮음. 참고용.

**p < 0.05 (permutation p 기준)로 확실히 유의한 결과 목록**:
[TBD]

---

## 5. Confidence 분포 + P1 데드코드 상태

`scripts/confidence_distribution.py --tag unified2` 산출물 요약.

- 총 routed steps: [TBD]
- Confidence min: [TBD] (임계값 0.7 대비)
- Below-threshold count: [TBD]

**P1 판정** (사전등록 규칙): 4모델 전부 0%면 "안전장치인데 이 데이터셋
에선 발동 안 함" 서술. Threshold 임의 변경 금지.

---

## 6. Retrieval hit rate

`scripts/retrieval_hit_rate.py --tag unified2` 산출물.

| Model | Backend | Workflow hit | Step hit (±1) | Fallback |
|-------|---------|--------------|---------------|----------|
| ... | ... | ... | ... | ... |

---

## 7. Cost paradox 메커니즘 검증

`scripts/output_token_analysis.py --tag unified2` 산출물.

**가설**: workflow context가 generator 출력을 짧게 만들어 hybrid가
vanilla보다 저렴. 이 가설이 성립하려면 백엔드별 output token 분포가
다음 방향이어야 함:
- full_system output tokens < vanilla_vector output tokens

**관측**:
[TBD — 백엔드별 output token mean/median 표 삽입]

**판정**: 가설 유지/기각 [TBD].

---

## 8. Claude 비대칭 재확인 (v1에서 hybrid → hall +12.5pp)

**v1 관측**: Claude에서만 full_system이 vanilla보다 hallucination +12.5pp
증가. 4모델 중 유일 예외.

**v2 관측**:
- Claude full_system hall_rate: [TBD]
- Claude vanilla_vector hall_rate: [TBD]
- Δ: [TBD]
- 다른 3모델의 같은 Δ: gemini=[TBD], gpt=[TBD], qwen=[TBD]

**판정 로직**:
- v2에서도 Claude에서만 hybrid > vanilla (더 나쁜 방향)이면 → discussion
  한 단락: "무관 컨텍스트에 대한 모델별 강건성 차이"
- v2에서 뒤집혔거나 사라졌으면 → v1 관측은 workflow 커버리지 결함의
  부산물로 재분류, discussion에서 빠짐

**판정**: [TBD].

---

## 9. 스토리 A/B/C 판정 (사전등록 대조)

사전등록의 판정 조건 재정리:

**스토리 A (시스템 우위)** 조건:
- full_system > vanilla_vector (step_acc 또는 goal_comp): 4모델 중 3+ 방향 우세
- 그중 1+ 모델에서 perm p < 0.10
- faithfulness도 3+/4 방향 우세
- cost 역설 유지

**스토리 B (조건부 우위)** 조건:
- 위 A 조건 중 일부만 만족 — 지표별로 방향 차이 있거나 모델 의존성 확인
- cost 역설 유지

**스토리 C (여전히 비등)** 조건:
- hybrid 우위 2/4 이하 (지표 3개 통틀어)
- cost 역설조차 뒤집힘

**판정 근거 요약**:
- step_accuracy 방향 우세: [TBD]/4
- faithfulness 방향 우세: [TBD]/4
- goal_completion (n=5 완화): [TBD]/4
- cost 우위 유지: [TBD] (API-priced 모델 기준 3/3 목표)

**최종 판정**: [A / B / C]

---

## 10. 판정 → 행동 매핑 (사용자 사전 합의)

**A 판정 시**:
1. 논문 집필 착수
2. 표 3종 확정 (final matrix, ablation, hit rate)
3. Qualitative figure (r2/r4/r5 환각 사례)
4. Methods에 감사 기록 반영 (`methodology_audit_trail.md`)

**B 판정 시**:
1. 논문 주장 확정: "동등 정확도를 1/N 비용과 더 낮은 환각으로"
   (N은 관측된 배수 삽입)
2. **사용자에게 결정 요청**: attribute 시나리오 추가할지 여부
   (4시간 캡처 → 논문 강도 vs 시간 트레이드오프)
3. Cost paradox와 Claude 비대칭이 헤드라인 발견으로 승격

**C 판정 시**:
1. 발견 중심 논문으로 전환:
   - Zero-shot LLM의 공개 SW 매뉴얼 태스크에서의 예상 밖 강함
   - 3-gate goal_completion + workflow coverage 검증이 벤치마크
     방법론 기여로 승격
2. Cost 역설이 살아있으면 그것이 core finding

---

## 부록 — 실행 이력

| 회차 | 시작 시각 | 완료 시각 | 결과 |
|------|-----------|-----------|------|
| Phase 1 (Gemini) | 2026-07-16 11:09 | 13:09 | ✅ Checkpoint PASS |
| Phase 2 시작 (Claude) | 13:47 | 15:24 | ✅ Mini-checkpoint PASS |
| Phase 2 GPT | 15:24 | [TBD] | [TBD] |
| Phase 2 Qwen | [TBD] | [TBD] | [TBD] |

---

## 서명

이 판정 보고서의 A/B/C 결정은 **사전등록(`v2_pre_registration.md`) 시점의
기준**만으로 이루어짐. 결과를 본 후 기준을 조정하지 않음.
