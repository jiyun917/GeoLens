# Qualitative Examples — Index

논문 discussion/figures용 실증 사례. 매 사례는 **한 번의 실제 벤치 실행**
에서 뽑힌 raw response와 그 시점의 스크린샷/시각 상태로 구성. 사례별로
어떤 시스템 속성을 논증하는지 명시.

## Case 1 — Hallucinated completion in no-RAG baseline

**Path**: `hallucinated_completion_3dviz/`
**Argument**: Vision component 없는 zero-shot LLM은 대화 이력만으로
UI 상태를 환각. r2/r4/r5 (Claude Sonnet 4.6, no_rag)가 3d_visualization
step 3에서 "In-line, Cross-line, Z-slice 모두 로드됨"이라 선언 —
실제 화면에는 2개만.

**Discussion 활용**: "vision-grounded RAG가 왜 필요한가"의 데이터적 증거.
figure: 왼쪽 스크린샷(2슬라이스), 오른쪽 3개 응답 원문.
**Status**: ✅ 준비 완료 (screenshot + README + 5개 응답 원문)

## Case 2 — RAG router mis-routing due to workflow coverage gap

**Path**: `seg_y_import_failure_notes.md` + `seg_y_import_rag_misroute.log`
**Argument**: hand-authored workflow에 없는 태스크는 라우터가 유사한
다른 workflow로 강제 매핑 → 무관 청크가 컨텍스트에 주입 → 잘못된 지시.

**Discussion 활용**: workflow 커버리지가 hybrid RAG의 필수 조건 (아키텍처
결함 아니라 지식베이스 결함) — 우리 프로젝트가 v1→v2에서 진단·수정한
케이스 자체가 이 논점의 데이터.
**Status**: ✅ 기존 자료 (v1 시점)

## Case 3 — (v2 완료 후 추가 예정) Full_system이 no_rag/vanilla를 disambiguate

**계획**: v2 실행 완료 시점에 full_system이 3d_viz step 2 (Cross-line
추가)에서 정답을 낸 replicate를 골라, 같은 스텝의 no_rag/vanilla 응답과
나란히 비교. workflow 노드가 컨텍스트에 들어간 후 지시가 어떻게 달라지는가.

**Discussion 활용**: hybrid의 실제 기여 메커니즘 (retrieval → generation 
품질) 시각화.

## Case 4 — (v2 완료 후 추가 예정) Confidence fallback 실제 발동

**계획**: v2 per_step 로그에서 fallback_activated=True 사례를 추출.
low-confidence 노드가 nulled out되고 vector-only가 대신 답한 응답과,
동일 스텝에서 fallback 없이 low-conf 노드를 그대로 쓴 대체 실험(있으면)
비교.

**Discussion 활용**: P1 설계의 실효성 검증. fallback rate 통계표에 붙는
정성 예시.

## Case 5 — (v2 완료 후, Claude 비대칭이 유지되면) Claude에서 hybrid가 hallucination을 늘리는 예시

**계획**: v1에서 관측된 "Claude만 hybrid가 hall +12.5pp" 패턴이 v2에서도
유지되면, Claude가 무관 workflow 노드 컨텍스트를 어떻게 처리하는지 (또는
잘못 처리하는지) 응답 원문으로 시각화.

**Discussion 활용**: 모델별 무관 컨텍스트 강건성 차이 — LLM 배치 결정에
쓸 수 있는 지식.

## 사례 선정 원칙

- **실제 벤치 실행에서 뽑을 것.** cherry-picked prompt 실험은 금지.
- **한 사례당 한 논점.** 여러 논점을 섞으면 figure 캡션이 길어지고 독자가
  헷갈림.
- **화면 상태와 응답을 나란히 놓을 것.** vision-grounded RAG 논문에서
  "화면-응답 부합성"이 핵심 축이므로 figure 스타일 통일.
- **모델·백엔드·시나리오·replicate 식별자를 반드시 기재.** 감사 가능성.
