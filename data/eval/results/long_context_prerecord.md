# Long-context 베이스라인 사전 기록

**작성 시점**: v3 실행 개시 전. 실행 결과 관측 없이 사전 등록.

## 매뉴얼 전문 규모

| 지표 | 값 |
|------|-----|
| 원본 PDF | `Introduction-To-OpendTect-and-OpendTect-Pro-Training-Manual-7-0.pdf` |
| ChromaDB 청크 수 | 486 |
| 재조립 텍스트 문자 수 | 769,334 |
| 토큰 수 (cl100k_base 기준) | 191,433 |
| 실측 Gemini API input tokens (step 0 smoke test) | 226,637 |

토큰 수 차이(191K vs 227K)는 Gemini의 자체 토크나이저가 cl100k_base보다 다국어 텍스트에 더 촘촘하게 분해하기 때문. Gemini 실측치를 실제 비용 산정에 사용.

## 컨텍스트 한도 정책

- Gemini 2.5 Pro 컨텍스트 한도: **2,000,000 tokens** (input)
- 매뉴얼 전문 실측: 226,637 tokens (~11.3% 사용)
- **잘라내기 없이 전문 그대로 주입**
- 향후 다른 매뉴얼에서 한도 초과 시 대비 정책 (본 실험에 미적용):
  - 우선순위 1: 시나리오 태그된 챕터 유지
  - 우선순위 2: Overview / Getting Started 유지
  - 우선순위 3: 부록/색인 제거

## 재조립 방식

`(page, chunk_index)` 순으로 정렬된 청크를 `\n\n` 구분자로 연결. Source 헤더는 각 청크에 포함된 채 유지 (원본 PDF의 페이지 위치 정보 보존).

## 실행 조건

- 모델: Gemini 2.5 Pro만 (다른 모델의 컨텍스트 한도로는 확장 불가)
- 시나리오: 2개 (survey_setup + 3d_visualization)
- Replicates: 5
- 총 에피소드: 2 × 5 = 10
- 총 스텝: 10 × 4 = 40
- 파이프라인 태그: `unified2` 동결 유지 (bench_runner.py, evaluation.py 변경 없음)
- 3-gate 채점 그대로 적용
- 백엔드 등록 파일: `api/services/bench_backends.py`에 `backend_long_context` 추가만, 다른 백엔드/파이프라인 코드 변경 없음

## 사전 예측 (관측 전 등록)

- Input tokens: ~226,637 (전 스텝 동일, prior_responses 누적으로 약간 증가 예상)
- 스텝당 비용: 매뉴얼 부분만 226,637 × $1.25/M = **~$0.283** + 시스템 프롬프트/응답
- Vanilla_vector(스텝당 $0.0093) 대비 약 **30배 비싼 것으로 예상**
- Full_system(스텝당 $0.00266) 대비 약 **100배 비쌀 것으로 예상**
- 정확도: 열린 질문 — 다음 4가지 결과 시나리오 모두 가능
  1. long_context > full_system 정확도 (RAG 오버헤드 대비 매뉴얼 접근성 우위)
  2. long_context ≈ full_system (정보량 vs 정보 집중의 상쇄)
  3. long_context < full_system (긴 컨텍스트 attention 희석)
  4. long_context ≈ no_rag (매뉴얼 정보를 활용 못 함)

## Story A 방어 논리 (사전 등록)

long_context가 정확도에서 full_system을 능가하더라도 Story A는 유지된다. 방어 논리:

- 비용 축 유지: long_context $0.28/step vs full_system $0.003/step = ~100배 격차
- 실용 시스템 관점: 매 스텝 매뉴얼 전문을 주입하는 것은 실시간 인터랙션에서 비현실적
- Retrieval의 존재 이유: "동등 정확도를 1/N 비용에" 프레이밍이 오히려 강화됨

## 로그 및 산출물

- 실행 로그: `data/eval/results/long_context_gemini.log`
- 결과 파일: `data/eval/results/run_gemini_longctx_r{1..5}_<TS>.json`
- Mini-checkpoint: `v2_checkpoint.py --tag longctx --model gemini` (별도 태그)
