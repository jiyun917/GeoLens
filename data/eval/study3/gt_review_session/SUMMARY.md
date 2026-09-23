# Study 3 GT 외부 검수 요약 (2026-09-23)

## 범위와 방법
- 검수 대상 25장: `opendtect__horizon_2dviewer__01` step 0–5, `qgis__rule_classification__01` step 0–9, `qgis__reclassify_raster__01` step 0–8. OpendTect step 6·7·8은 지시대로 제외(초안의 `visual_state_gt` 그대로, 삭제 안 함).
- 원본 JPEG를 PIL로 3–16배 확대한 크롭(`crops/`, 합성본 `crops/comp_*.png`)을 Read로 확인. 초안 `visible_elements` 전 항목(1,476개)을 대조했고 `current_dialog`/`data_state`/`current_action`은 화면 사실과 비교했다. RULES.md 규칙 3 필드와 `capture_instructions`, 원본 `scenarios/*.json`은 건드리지 않았다.
- `proposed/<scenario>.json`은 원본과 같은 키 순서·indent 2·ensure_ascii=False·줄끝(LF)·끝 개행으로 저장했고, `visual_state_gt`의 `visible_elements`/`data_state` 외에는 원본과 같음을 스크립트로 확인했다(diff 결과: 변경된 줄만 차이).

## 표본 오독률 (규칙 4) — 5% 미만, 반영 진행
- 6장 풀링: **7 / 397 = 1.76%** (형식성 콜론 2건 제외 시 5 / 397 = 1.26%). 스텝별: O s1 4/64, O s4 0/70, Q s4 1/72, Q s8 2/71, R s3 0/54, R s7 0/66. 상세는 `sample_check.md`.
- 따라서 `proposed/` 3개 파일을 작성했다.

## 변경 건수 (`GT_change_list.md`)
| 시나리오 | 수정 | 삭제 | 추가 | data_state | 계 |
|---|---|---|---|---|---|
| opendtect__horizon_2dviewer__01 (s0–s5) | 9 | 20 (중복 15, 잘못된 상태 표기 3, 겹침 라벨 2) | 8 | 1 | 38 |
| qgis__rule_classification__01 | 20 | 1 (중복) | 0 | 1 | 22 |
| qgis__reclassify_raster__01 | 2 | 0 | 4 | 1 | 7 |

주요 수정: O s1 `SEC`→`SEG-Y`, `Scene 1 (checked)`→`Scene 1`, 콜론 제거; O s3 상태줄 `Inl/Crl: 5750, SP: 551`→`TrcNr: 3798, SP: 991`(아랫반만 보임, H6), `[free mem] 50.5/127.6`→`98.9/127.8`, viewer 트리의 체크박스 없는 항목에 붙은 `(unchecked)` 삭제; O s3/s5 겹친 축 라벨을 s4 방식으로 통일; Q s2 규칙 11건 `'landuse'`→`"landuse"`; Q s4 `Scale range [checked]`→`[unchecked]`; Q s6/s8·R s6 제목 하이픈→em dash; Q s7/s8 `Swellendam`→`Swellendam ...`; Q s9 좌표 `8626`→`8826`; R s0 툴박스 `Aspect` 추가(레이어명 `aspect`와 대소문자 무시 중복 처리로 빠진 듯); R s2/s4/s5 `...` 버튼 추가.

## 보류 (`GT_hold_list.md`) — 책임자 결정 필요
- **H1 (가장 큼)** QGIS 글꼴이 마침표를 쉼표처럼 렌더링해 `0.093473`/`0,093473`, `1,548`/`1.548`, `0.0 °`/`0,0 °`, `Gamma 1.00`, 좌표값의 소수점을 화면에서 구분할 수 없다(근거: 소스가 마침표인 `Min. Scale` 헤더가 같은 글리프). 초안 표기 그대로 두고 오독으로 세지 않았다. 마침표/쉼표 통일 방침 결정 필요(검수자는 마침표 권고). 스텝 간 불일치(`1,548` vs `1.548`, `0.0 °` vs `0,0 °`)도 같이 정리 필요.
- **H2** OpendTect s1 키워드 `Well correlation-Line`, s2 키워드 `Seis`(`\bSeis\b`는 화면의 `Seismic`에 매치 안 됨), s8 대안 `Well correlation`, goal의 두 이름 — 화면 데이터명(`19981104-1-04_0037`, `Seismic`)과 불일치. 규칙 3 필드라 미수정.
- **H3** reclassify s1→s2: Raster layer가 자동 채워져 s2 화면이 s1과 동일. s1 기대행동(`aspect` 선택)·s2 노드의 처리 방침.
- H4 reclassify 저장 경로(`C:/GeoLensData/`) vs goal/must_be_true의 `exercise_data/raster_analysis`(패턴은 통과).
- H5 rule_classification initial_state의 AREA 필드 — 화면상 확인 불가.
- H6 O s3 상태줄 TrcNr 끝자리(8/6) 판독 불확실 — 제안값 유지/앞부분만/삭제 중 선택.
- H7 겹친 축 라벨 표기 관례, H8 반쯤 가려진 탭 행(`QGIS Server`) 미추가, H9 `Duplicate Count` 끝글자 잘림 유지, H10 `(checked)`/`[checked]` 혼용과 중복 정리 관례, H11 O s4에 추가한 `?`·`▷`, H12 제외 스텝 참고 사항, H13 `Symbol Levels···` 글리프.

## capture_instructions 와 화면 불일치 (기록만)
O s1–s5(Well correlation-Line/Seis 명칭, s4 Event/Correlation 값은 Mode 탭만 보여 확인 불가, viewer 트리 가려짐), Q s8(지도 뒤 렌더링 확인 불가), R s1/s2(자동 채움), R s3(별도 대화상자가 아닌 패널), R s5(경로). 표는 `GT_change_list.md` 끝에.

## 산출물
`GT_change_list.md`, `GT_hold_list.md`, `sample_check.md`, `proposed/opendtect__horizon_2dviewer__01.json`, `proposed/qgis__rule_classification__01.json`, `proposed/qgis__reclassify_raster__01.json`, `SUMMARY.md`(이 파일), 근거 크롭 `crops/`.
