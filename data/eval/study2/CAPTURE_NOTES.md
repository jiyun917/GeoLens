# Study 2 캡처 검증 노트 (2026-09-21)

사용자가 16장을 PNG(1922×1041; fault_sticks step_2만 1920×1032)로 캡처했고 노트는 남기지 않았다. 검증은 Claude(메인 세션)가 축소본(1100 px)으로 각 장을 지시서 조건과 대조해 수행했다. PNG 원본은 `data/eval/study2/originals_png/<scenario_id>/`에 보존하고, 벤치가 읽는 `data/eval/screenshots/<scenario_id>/step_N.jpg`는 원본을 JPEG(quality 92)로 변환한 것이다(이전 세트와 같은 형식).

## opendtect__horizon_autotrack__01 (7장) — 전부 조건 충족
- step_0: Random Line 1에 4 Dip steered median filter, 3D Horizon 비어 있음, Settings 창 없음. 툴바 In-line 130/Step 10 표시.
- step_1: `Horizon Tracking Settings - <New Horizon 1>` Mode 탭, Section Auto-track, Method Seed Trace. 탭은 Mode·Event·Correlation·Properties 4개 — **DipSteer 탭 없음(dip-steering 라이선스 없음)** → 매뉴얼 step 11(Steering = No)은 이 환경에 없음. 트리에 <New Horizon 1>과 하위 Tracking Order/Seed Index/Correlation/Amplitude/Z values(경고 아이콘).
- step_2: Event 탭, Event type Peak, Relative difference, Allowed difference 25, Search window -8 8, Data Display window -16 16, Nr Traces 5, Picked on (비어 있음), WVA 체크.
- step_3: Correlation 탭, Use Correlation Yes, Compare window -40 40, Correlation threshold 60.0, Snap to Event 체크, Data Display window -48 48, Nr Traces 5. seed 없음.
- step_4: seed 클릭 결과 random line 하단 반사면을 따라 **녹색 선(단면 자동 추적)**이 생김 — Section Auto-track 모드에서 seed를 찍으면 단면을 따라 즉시 추적되는 OpendTect 정상 동작이며 3D 패치는 아직 없음. Settings 창은 우상단으로 옮겨져 있고 WVA 파형 표시에 초록 선. 툴바에 Auto-Track/Retrack 아이콘 노출. 상태 표시줄에 좌표·Value 표시.
- step_5: Auto-Track 후 녹색 3D 패치가 단면 밖으로 퍼짐. 트리 하위 항목의 경고 아이콘이 색상 견본으로 바뀜. 상태 표시줄에 좌표·Value·Random Line 1.
- step_6: Lock 후. **step_5와 시각적으로 거의 동일**(차이: 상태 표시줄이 비어 있음). Lock은 화면에 표시되지 않으므로 이 스텝의 '완료' 판단은 세션 이력(직전 지시 Lock)에 의존한다. 패턴은 캡처 전 확정대로 유지.

## opendtect__fault_sticks__01 (9장) — 전부 조건 충족
- step_0: In-line 110에 4 Dip steered median filter, 원근 뷰(In-line view 방향), FaultStickSet 비어 있음. 단층 부위로 축소하지는 않고 인라인 전체가 보임(지시서의 "축소"는 미적용, 영향 없음).
- step_1: 트리에 <New FaultStickSet 1>. 하단에 fault stick 편집 툴바(Copy Selection to / Fault / Create Single New / Select… / 색상 / 가위 / 체크 / 휴지통 / undo·redo)가 나타나고 상태 표시줄 "Picking". → 이 툴바는 s1부터 계속 보인다.
- step_2: `Output selection` 대화상자, Output FaultStickSet 필드 비어 있음, Select…, Replace in tree 체크, OK/Cancel/?. 창 크기 1920×1032.
- step_3: 대화상자 닫힘, 트리 항목 FaultStickSet_01.
- step_4: **step_3과 시각적으로 동일**(Only at Sections 토글은 스틱이 없으면 화면에 드러나지 않음). 이 스텝의 정답(스틱 픽)은 세션 이력에 의존.
- step_5: In-line 110에 녹색 스틱 여러 개(노란 seed 점). 툴바 In-line 110/Step 1.
- step_6: In-line 130(Step 10)에 스틱 여러 개, 화면이 단층 부위로 확대됨. Z-slice 없음.
- step_7: Z-slice 1500에 `9-1 Similarity on F…` 표시, FaultStickSet_01 색상 견본이 보라색, 스틱은 슬라이스 위에 가는 보라 선으로 보임(미선택). 카메라는 완전한 top view가 아니라 비스듬한 뷰(북쪽 위, 인라인 130이 아래에 평면으로 보임). 툴바 Z 1500/Step 4. Fault_01A 없음.
- step_8: 트리 Fault 아래 **Fault_01A**(하위 <right-click> 항목, 파란 색상 견본), 파란 단층면이 인라인 근처에 보임. 카메라 회전됨. 대화상자 없음.

## GT 작성 시 유의
- A s5/s6, B s3/s4는 화면이 같으므로 visual_state_gt의 `data_state`에 "화면상 구별 불가, 상태는 세션 이력으로만 알 수 있음"을 적는다(QGIS s3/s4와 같은 처리). loop_rate 집계에 같은 응답이 잡힐 수 있음을 사전등록 2에 기재.
- 모든 장에 창 제목 `OpendTect V7.0.9 (Windows) *UPDATE AVAILABLE* : F3 Demo 2023 - [Scene 1]`와 툴바(In-line/Step, 색상 범위, OD Seismic 1)가 공통으로 보인다.
