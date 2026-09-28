# Study 3 사후 진단 (exploratory, post-hoc; 2026-09-28)

**지위**: 서명된 study 3 판정(A′/B, V3-42)은 그대로다. 이 문서는 확인 실행의 응답·라우팅 텔레메트리를 읽고 원인을 분류한 사후 분석이며, 어떤 수치도 판정에 반영되지 않는다. 이 분석을 본 순간부터 study 3 판정 세트(3 시나리오)는 **개발 데이터**가 되어 이후 확인 연구의 판정 세트로 쓸 수 없다.

## 1. 정확도 손실의 주원인 = 라우터의 지연(lag)
full_system 280 스텝/모델에서 라우터가 GT 노드를 고른 비율은 절반 수준이고, 틀린 선택의 70~75%는 **한 노드 이상 뒤처진** 선택이다.

| model | route ok | matched(route ok) | route wrong | matched(route wrong) | wrong: behind / ahead / other |
|---|---|---|---|---|---|
| gemini | 140/280 | 0.921 | 140 | 0.629 | 103 / 11 / 26 |
| claude | 145/280 | 0.931 | 135 | 0.830 | 100 / 15 / 20 |
| gpt | 160/280 | 0.938 | 120 | 0.575 | 87 / 13 / 20 |

라우팅이 맞은 스텝에서 full_system의 정확도는 0.92~0.94로 vanilla_vector 전체(0.75~0.83)를 크게 웃돈다. 즉 격차는 라우팅 지연이 만든 것이다.

### 1.1 지연의 실체 (텔레메트리)
- Reclassify s3–s5(Claude 10/10, GPT 부분): 후보 풀에 03(prior)·04(prior 후속)·02·01·07·06이 있는데 Flash rerank가 매번 `03_raster_layer_aspect`(confidence 0.9)를 고른다. 화면은 이미 테이블 패널(s3)·5x3 테이블(s4)·출력 경로(s5)로 바뀌었다. rerank가 "직전 노드"에 붙는 경향(stickiness). Gemini 세션은 s5에서 06으로 넘어갔는데, 직전 지시문("Reclassified raster … Save to File")이 06과 겹쳤기 때문이다 → rerank의 선택이 직전 생성 응답에 좌우된다.
- s4에서 정답 노드 05(table_filled)는 **후보 풀에 없다**(03의 1-hop 후속만 포함, 임베딩 top-5 밖).
- R2″(history advance)는 모델·시나리오당 0~4회만 발화. 덮음 기준 0.8이 긴 묶음 edge 지시문("Horizon Tracking Settings는 기본값 그대로 두고 … seed를 클릭해 …")에 거의 도달하지 못한다.
- v7의 이력 기반 [Next Action]("previous instruction already covered … continue with Add Row")은 화면이 그대로인 s1→s2(자동 채움)에서 GPT를 한 단계 앞서게 만들었다(GPT reclassify s2 0/10 vs vanilla_vector 10/10).
- Rule s5–s7(Gemini): 노드 03(existing_rules)에 3스텝 고정 → 맥락이 "규칙 전부 삭제"를 계속 지시.
- Horizon s5(GPT 2/10): 05(track_new_settings) 고정 → 맥락 "seed 클릭" → GPT는 "Settings 창을 닫으세요"(허용 안 됨). Claude는 화면을 읽고 맥락을 무시해 8/10.

### 1.2 백엔드 공통 손실(메커니즘 무관, 기록만)
- Claude reclassify s4/s5: 네 백엔드 모두 0/10 — Claude가 s4/s5 화면에서 테이블이 아직 설정되지 않았다고 읽음(화면 오독).
- Gemini rule s5: '+' 버튼 답은 GT 패턴에 없음(사전등록 §1.1에 기록한 엄격성; 전 백엔드 공통).

## 2. 환각(v5) 플래그의 실체
전 플래그를 채점기로 재현했다. full_system 고유 플래그는 전부 **키보드 키·창 컨트롤** 유형이다.
- Claude full: horizon s7 `X(` 10/10("**X(닫기)** 버튼"; 토크나이저가 여는 괄호까지 토큰으로 잡음), reclassify s6 `F7` 6/10(QGIS의 실제 Layer Styling 단축키), rule s2 `Shift` 10/10(Shift-클릭 선택).
- Claude 비교군: rule s2 `Ctrl+A` 10/10. GPT no_rag/vanilla_budget: rule s2 `Delete All` 2~3/10(실재하지 않는 버튼 — 진짜 발명). Gemini no_rag: 숫자 범위·`Properties`.
- 해석: v5 정의("화면·매뉴얼에 근거 없는 UI 참조")로는 정당한 플래그이나, 단축키·수정자 키·창 닫기 X는 어떤 앱에도 있는 일반 어휘라 "발명된 UI 요소"와 다르다. full_system은 그래프 맥락("닫으세요", "Layer Styling 패널을 여세요")을 구체화하면서 이런 일반 어휘를 덧붙인다.

## 3. 고칠 수 있는 것(새 연구에서만; 확정 전 검증)
1. **라우터 R3 = 그래프 제약 상태 추적**: 세션 현재 노드를 유지하고 후보를 {현재, 1~2-hop 후속, 직전}으로 제한, 비전 서술과 각 노드의 기대 상태(signature/expected_dialog/visible elements)의 토큰 덮음으로 점수화해 후속이 현재보다 높으면 전진. rerank의 직전 노드 고착과 뒤로 뛰기를 구조적으로 막는다.
2. 후보 풀에 직전 노드의 2-hop 후속 포함(05 누락 유형).
3. 조립 v8: 이력이 아니라 **화면**으로 "이미 수행됨"을 판단하고, [Next Action] 뒤에 무조건 "이 edge의 결과가 이미 보이면 다음 edge: …"를 붙인다(1단계 지연을 생성기 쪽에서 흡수).
4. 생성기 프롬프트 v3(전 백엔드 공통): 화면·맥락에 없는 단축키·수정자 키·메뉴 경로를 언급하지 않는다.
5. 채점기 토크나이저 버그 수정(여는 괄호가 토큰에 붙는 `X(`, `Add Data (`) — 정의 변경 아님.

## 4. 새 연구의 조건
- 판정 세트: **새 매뉴얼 의존 시나리오**(캡처 새로 필요). study 2·3 세트는 개발·검증 데이터.
- 검증 게이트(확정 전): 개발 세트 5 시나리오 × 3 모델에서 full_system ≥ vanilla_vector(스텝) 전 시나리오, 라우팅 정답률 ≥ 0.85, hall(v5+토크나이저 수정) full = 0.
- 논문은 v3 → study 2 → study 3 → study 4의 순서와 지표 버전 변화를 감사 기록대로 공개한다.
