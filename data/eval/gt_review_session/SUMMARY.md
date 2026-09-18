# 세션 요약 — GT 검수 (gt_review_session, 2026-09-18)

## 무엇을 보았나
- 텍스트: `RULES.md`, `gt_visible_elements_review_v3.md`, `scenarios/*.json` 4개, `manual_excerpts/*.txt` 2개.
- 스크린샷 17장(원본 해상도): 3d_visualization step 1·3, attribute_computation step 0·2·3·4·5·7, survey_setup step 0·2·3, qgis step 0·1·3·7 (B 항목이 있는 스텝 + 규칙 2 표본 3장). 확대 크롭 `survey_s0_add_button_x3.png`, `survey_s0_context.png`.
- 판독이 애매한 부분(QGIS 소수점 구분자·좌표 숫자, Attribute Name 공백)은 PIL로 3–8배 크롭을 스크래치패드(폴더 밖 임시 디렉터리)에 만들어 확인했다. 폴더 안 파일은 읽기만 했고, 폴더에는 §5 산출물만 썼다.
- 열지 않은 것: `data/eval/results`, `*.log`, `run_*.json`, `dev_iter*`, 모델 응답·채점 결과. git · 파이프라인 · 앱 미실행.

## 규칙 2 표본 검수 (sample_check.md)
- survey s0: 4항목, 오독 0. attr s3: 51항목, 오독 0(표기 차이 1). qgis s3: 49항목, 오독 1(좌표 `1026658` ↔ 화면 `1028658`), 표기 차이 3(소수점이 화면은 쉼표).
- **전체 104항목 중 오독 1건 = 0.96%**; 표기 차이까지 보수 합산 5건 = 4.81%. 어느 기준으로도 5% 미만 → 반영 진행. (qgis s3 한 장만의 보수 합산은 8.16%.)

## 변경 (GT_change_list.md → proposed/)
- 총 **19건**. 규칙 1: 14건 (삭제 2 — 3d s1 `OR Select Attribute dialog…`, attr s2 `Input Data = 4 Dip steered median filter`; 라벨 원문 변경 11; 아이콘 표기 1 — survey s0 `Add button` → `New Survey (+)`). 규칙 4: 5건 (qgis s3 visible_elements Input layer 값 명시, data_state, current_action, expected_action_text_pattern, expected_action_keywords).
- 규칙 1 판정 분포(B 25건): 삭제 2 / 변경 12 / 유지 5 / 보류 6.
- 규칙 3: 0건(보류).
- `proposed/` 네 파일 모두 원본과 바이트 왕복 일치를 확인한 뒤 생성(CRLF · 키 순서 · indent 2 · ensure_ascii=False 유지) — diff에는 GT 변경만 나타남. 네 시나리오 모두 변경이 있어 "그대로 복사"된 파일은 없다.

## 보류 (GT_hold_list.md) — 11건
- B 항목 판정 보류 6: 부재 서술 3건(3d s3, attr s5, qgis s7 — 1-b 유지 vs 1-c 삭제 충돌), 상태 서술이 화면과 모순 1건(attr s0 `Parameter panel (empty …)` — 실제로는 Similarity 파라미터로 채워짐), `OK / Save button` 1건(attr s3 — OK 없음, Save는 매뉴얼의 'Save as icon'일 가능성), 복합 라벨 1건(qgis s3 `End cap style, Join style dropdowns`).
- 규칙 3 보류 1 (H7). 부수 보류 4: Edit button 표기(H5), 중복 문자열 6건(H9), A 항목 표기 차이·오독(H10), 규칙 4 부수 불일치(H11).

## survey step 0 결론 (규칙 3)
- 스크린샷: 버튼은 텍스트 없이 문서 + 녹색 원 '+' 아이콘만 있다(크롭 2장으로 확인).
- 매뉴얼 §1.2.2a p.21 Workflow: "2. Click on the New Survey icon ." — Add도 "+"도 아닌 **'New Survey icon'**. → 규칙 3의 "매뉴얼이 다른 이름으로 부르면 보류"에 해당. `expected_action_text_pattern`, `allowed_alternatives` **변경 없음**.
- 별도로 규칙 1-a에 따라 visible_elements의 `Add button`은 '매뉴얼 이름 + 기호' = `New Survey (+)`로 표기를 바꿨다(기존 패턴 `(Survey|Create|New|Add)`와 충돌 없음).

## QGIS step 3 결론 (규칙 4)
- 스크린샷: Input layer 칸에 `roads_33S [EPSG:32733]`가 **이미 채워져 있다**(유일 레이어 자동 선택). 기존 GT의 "No input layer selected yet / about to select roads_33S"는 화면과 불일치.
- 반영: visible_elements 항목에 값 명시, data_state · current_action 정정, 기대 동작 패턴에 `Distance|50|Dissolve` 추가하고 keywords에 `Distance`, `50` 추가(매뉴얼 §6.2.6 step 5의 남은 동작 + goal의 Dissolve). 기존 Input layer / roads_33S 토큰은 '이미 선택돼 있음을 확인'하는 응답도 부합하므로 유지. signature · workflow · capture_instructions는 미변경.
- 주의: 그 결과 step 3과 step 4의 화면 상태가 사실상 같아진다(H11) — 시나리오 설계 차원의 확인이 필요하다.

## 산출물 (모두 이 폴더)
- `sample_check.md`, `GT_change_list.md`, `GT_hold_list.md`, `SUMMARY.md`
- `proposed/opendtect__3d_visualization__01.json` (1항목 삭제), `proposed/opendtect__attribute_computation__01.json` (6항목), `proposed/opendtect__survey_setup__01.json` (4항목), `proposed/qgis__vector_buffer__01.json` (4항목 + data_state · current_action · pattern · keywords)

## 후속 확인 권장 (규칙 밖이라 미수정)
1. H10의 오독 1건(qgis s3 Coordinate)과 표기 차이 4건 정정 여부; 다른 QGIS 스텝의 소수점 표기(`50.000000` 등)도 같은 문제일 가능성(표본 밖, 미검수).
2. H9 중복 문자열 6건 정리 방식.
3. 부재 서술 항목("No …", "… closed")의 일반 규칙(유지 / 삭제) 결정.
4. qgis step 3 keywords의 채점 의미 확인, capture_instructions · step 4와의 정합.
5. 변경 스텝의 `_gt_provenance` 갱신 여부.
