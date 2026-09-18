# 채택 전 확인: 조립 버전(v4/v5)이 라우팅에 영향을 주는가 (API 호출 없음, 2026-09-19)

질문(사용자): GPT 벤치의 survey s3 오라우팅이 조립 버전과 무관한가. 라우팅 코드 경로와 rerank 입력이 v4와 v5에서 동일한가.

## 1. 라우팅 코드 경로 — 동일
- `git diff c01fdda d326838 -- api` = `guide_pipeline.py` 1개 파일, 변경은 모듈 상수(`CONTEXT_ASSEMBLY` 기본값, `_CTX_COMPLETION_CHECK`, `_EXAMPLE_RE`, `_tag_examples`)와 `build_context_block()` 내부의 v4/v5 분기뿐.
- `localize_to_graph()`(후보 풀·graph prior·rerank·gate·goal-state)는 바이트 단위로 같고, `build_context_block()`은 localize가 끝난 뒤 그 출력만 받아 호출된다(정적 메서드, 라우팅 상태를 바꾸지 않음).

## 2. rerank 입력 — 동일하지 않음 (간접 결합 경로 1개)
- `_llm_rerank_candidates()`는 `completed_steps`(= 벤치가 넘기는 `prior_responses`, 즉 **직전 스텝들의 생성기 응답**)로 "Instructions already given to the user in this session (oldest first)" 블록을 만들어 프롬프트에 넣고, 결정 규칙이 이를 명시적으로 참조한다: "consistent with the goal and the instructions already given", "If the instructions already given completed a step but the screen has not changed, stay on that step", "pick one of these again if … the instructions already given do not cover all of its actions".
- 생성기 응답은 조립 블록(v4/v5)에 따라 달라지므로, **조립 변경 → 직전 응답 → rerank 프롬프트**의 경로로 라우팅 입력이 달라진다. 벤치 16스텝 중 13스텝(각 시나리오의 s1 이후)이 이 블록을 가진다. dry-run은 `completed_steps=[]`로 돌므로 이 결합을 검사하지 못한다.
- 나머지 입력(후보 목록·visual_state·expected-next·그룹 prior·규칙문)은 조립과 무관하며, 실행 간 차이는 vision 출력의 비결정성(같은 스크린샷에 두 가지 visual_state 변형이 관측됨)뿐이다.

## 3. iteration 6 벤치의 오라우팅 3건 (dry-run과 같은 판정 규칙: expected_workflow_node가 있으면 노드, 없으면 워크플로우 일치)
V3-21에는 "벤치 라우팅 63/64"로 적었으나 손실 분류에서 라우팅 원인 손실만 센 수치였다. 정확한 값: **iteration 5(v4) 64/64, iteration 6(v5) 61/64**.

| 건 | pick | 결과 | iteration 5 같은 모델·스텝과의 rerank 입력 차이 |
|---|---|---|---|
| Claude attribute s2 | 03_select_type (정답 04) | 응답은 정답(손실 없음) | 세션 블록 **동일**, vision 출력 다름 → 조립과 무관 |
| Gemini r1 survey s3 | d3_visualization_01 (교차 워크플로우) | 응답은 정답(손실 없음) | vision 출력 다름 + 세션 블록 다름 → 분리 불가 |
| GPT survey s3 | d3_visualization_01 (교차 워크플로우) | 손실 | 고정부 해시 동일(dc0418bf17), **세션 블록만 다름** → 조립이 유일한 입력 차이 |

GPT survey s3 세션 블록: v4 "2. 'Scan SEG-Y file(s)'를 선택하고 'Next'를 클릭하세요. 3. 'Next'를 클릭하세요." → v5 "2. Survey name을 입력하고 'Scan SEG-Y file(s)'를 선택하세요. 3. 'Scan SEG-Y file(s)'를 선택하세요."

## 4. survey s3 → d3_01 오라우팅의 이력
- 최종 라우팅 코드(21f0dec 그룹 키 수정) 이전: dry-run iter3 1/5, iter4 2/5 오라우팅(교차 워크플로우 그룹 prior가 원인, 21f0dec에서 수정).
- 최종 라우팅 코드 이후: dry-run iter4b·5·6 15/15 정답(세션 블록 없음), iteration 5 벤치 4/4 정답(v4 세션 블록), iteration 6 벤치 2/4 정답(v5 세션 블록).
- 즉 최종 라우팅 코드에서 이 오라우팅이 관측된 것은 v5 벤치 2건뿐이다. rerank는 같은 입력에서도 확률적이므로 인과는 오프라인으로 확정할 수 없다(rerank 재생 실험이 필요: Gemini Flash rerank만 v4 프롬프트 ×N / v5 프롬프트 ×N — API 비용 발생, 사용자 결정).

## 5. 결론
사용자 조건("rerank 입력이 동일하지 않으면 채택을 중단")에 해당한다. 병합·`run_v3.sh` 변경·dry-run·V3-22(채택 사유) 기록은 하지 않았다. 라이브 코드는 c01fdda 그대로.
