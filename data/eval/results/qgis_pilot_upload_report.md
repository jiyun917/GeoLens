# QGIS Pilot — Training Manual 업로드 결과

**실행 완료 (UTC)**: 2026-08-13T00:56:30+00:00
**서버**: `http://127.0.0.1:8000` (env: GEOLENS_SOFTWARE_ID=qgis)
**업로드 경로**: `POST /api/manual/upload` (UI 와 동일 정규 HTTP 엔드포인트)
**KB 범위**: Training Manual 단독 (Desktop User Guide 제외 — 감사 기록 참조)

## 이식 비용 표 — 첫 실측값

| PDF | 크기 (MB) | 페이지 | 업로드 (UTC) | 완료 (UTC) | 소요 | manual_id | chunks | auto wf |
|---|---|---|---|---|---|---|---|---|
| QGIS-3.44-TrainingManual-en.pdf | 90.4 | 697 | 2026-08-13T00:00:52+00:00 | 2026-08-13T00:56:30+00:00 | 55.6 min | `bf2804feea57434bb79b749134ed1df0` | 733 | 1 |

**t1 주석**: ChromaDB 최종 write 시각과 auto workflow 파일 mtime 중 최댓값. `status=ready` 전환은 두 write 이후 발생하므로 실제 완료 시각과 초 단위 차이만 존재.

**참조 조건 (OpendTect unified4)**: Training Manual 454p, chunk_count 486, workflow_count 2 (hand-authored + 2 auto). 이식 비용 표에 나란히 배치하면 페이지 대비 ~1.5× 크기 문서에 대해 인제스트 처리량이 실측됨.

## Auto Workflow 발견

**Prefix (hint_workflow_id 용)**: `auto_bf2804feea57434bb79b749134ed1df0__*`
**개수**: 1

### `auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s`

- **이름**: ★☆☆ Follow Along: Implementing a Systematic Sampling Plot Design
- **노드 수**: 3
- **에지 수**: 2
- **파일**: `data/workflows/auto_bf2804feea57434bb79b749134ed1df0__follow_along_implementing_a_systematic_s.json`

**관찰**: AutoGraphBuilder 가 QGIS Training Manual 에서 1 개 workflow 만 추출. OpendTect Training Manual (454p) 은 2 개 auto workflow. QGIS 매뉴얼이 절차형 튜토리얼 (Follow Along 섹션) 이 특정 스타일로 구성되어 있어 auto-extraction 이 특정 섹션만 잡은 것으로 보임. Pilot 시나리오는 이 auto workflow 를 사용하거나, 필요 시 hand-author 추가 (OpendTect 의 seismic_attribute 와 동일 방식).

## QA — 무작위 청크 10개 샘플

Collection: `manual_bf2804feea57434bb79b749134ed1df0` (전체 733 chunks, 10개 sample)

**Chunk 1** — Section: `Lesson: Symbology` / Page: 36 / id: `918c23bd03b54554...`

> [Section: Lesson: Symbology, Page: 36, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual You can also use this field to set the Map Scale manually. 1. In the Status Bar, click on the Scale text field. 2. Type in 50000 and press Enter. This will redraw the features in the Map Canvas to reflect the scale ...

**Chunk 2** — Section: `★★☆ Follow Along: Adding Symbol Layers` / Page: 43 / id: `814110203d884fc7...`

> [Section: ★★☆ Follow Along: Adding Symbol Layers, Page: 43, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual Note You can use your mouse wheel to zoom in increments. Alternatively, use the zoom tools to zoom to a window: 2.4.6 ★★☆ Follow Along: Adding Symbol Layers Now that you know how to change simpl...

**Chunk 3** — Section: `★☆☆ Follow Along: Changing Label Options` / Page: 86 / id: `0923e4c68f254ed6...`

> [Section: ★☆☆ Follow Along: Changing Label Options, Page: 86, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual 7. Click Apply You’ll see that this adds a colored buffer or border to the place labels, making them easier to pick out on the map: 72 Chapter 3. Module: Classifying Vector Data...

**Chunk 4** — Section: `★★☆ Follow Along: Tool: Reshape Features` / Page: 173 / id: `310cd08bfcf548bc...`

> [Section: ★★☆ Follow Along: Tool: Reshape Features, Page: 173, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual 3. Undo your edit before continuing with the exercise for the next tool. 5.2.6 ★★☆ Follow Along: Tool: Reshape Features The Reshape Features tool is used to extend a polygon feature or cut aw...

**Chunk 5** — Section: `★☆☆ Follow Along: Extract the Buildings` / Page: 225 / id: `efc921f49fd34202...`

> [Section: ★☆☆ Follow Along: Extract the Buildings, Page: 225, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual 3. Click Run and close the dialog 4. You will probably find that not much seems to have changed. If so, move the well_located_houses layer to the top of the layers list, then zoom in. 6.2. Les...

**Chunk 6** — Section: `★☆☆ Follow Along: Preparing the Map Data` / Page: 465 / id: `ddb8354c231c4c7b...`

> [Section: ★☆☆ Follow Along: Preparing the Map Data, Page: 465, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual 14.9.1 ★☆☆ Follow Along: Preparing the Map Data Open the QGIS project from the parameters calculations lesson, forest_inventory.qgs. Keep at least the fol- lowing layers: • forest_stands_2012...

**Chunk 7** — Section: `Installing under Ubuntu` / Page: 495 / id: `c9acf5e9cc12446b...`

> [Section: Installing under Ubuntu, Page: 495, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] CHAPTER SIXTEEN MODULE: SPATIAL DATABASE CONCEPTS WITH POSTGIS / POSTGRESQL Spatial Databases allow the storage of the geometries of records inside a Database as well as providing functionality for querying and retrieving the rec...

**Chunk 8** — Section: `Clipping and merging raster layers` / Page: 577 / id: `4139c6a75c64431e...`

> [Section: Clipping and merging raster layers, Page: 577, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual Note Recent versions have a more complex interface. Make sure at least one compression method is selected. With this layer that contains the bounding box of the raster layer that we want to obtain,...

**Chunk 9** — Section: `Iterative execution of algorithms` / Page: 642 / id: `c86b6d2842924717...`

> [Section: Iterative execution of algorithms, Page: 642, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual Doing this for all the watersheds will produce the result we are looking for, but it doesn’t look like a very practical way of doing it. Instead, let’s see how to automate that select and crop routi...

**Chunk 10** — Section: `More iterative execution of algorithms` / Page: 644 / id: `cef64f019aea48e9...`

> [Section: More iterative execution of algorithms, Page: 644, Source: ./data\uploads\bf2804feea57434bb79b749134ed1df0_QGIS-3.44-TrainingManual-en.pdf] QGIS Training Manual Add the model to you models folder, so it is available in the toolbox, and execute it. Select the DEM and watersheds basins. The algorithm will generate tables for all the basins and place them...

## 다음 단계 (P-2 시나리오 정의)

이식 비용 표 첫 실측값 확보 완료. P-2 시나리오 정의 단계 진입:

- 후보 워크플로우 선정 (auto workflow 활용 or hand-author)
- QGIS-Training-Data 샘플 데이터로 수행 가능한 6~8 스텝 시나리오
- 시나리오 정의 후 라우팅 dry-run + 매뉴얼 스텝↔시나리오 스텝 대조표 (체크포인트 8, 9 — 사용자 응답 대기)

