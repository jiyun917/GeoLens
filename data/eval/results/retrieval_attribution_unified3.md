# Retrieval attribution — unified3 pre-registration evidence

Evidence for or against the pre-registered attribute-scenario
prediction (v2_pre_registration.md § attribute prediction).

## Vanilla vector retrieval (deterministic, replayed)

For each scenario, `backend_vanilla_vector` calls `get_manual_context(manual_ids, scenario.goal, top_k=5)`. That is a pure function of the fixed corpus and the fixed query (scenario.goal), so the retrieval we replay here matches bench-time exactly.

### opendtect__survey_setup__01

- query prefix: `OpendTect 첫 실행 후 Survey Setup and Selection 창에서 새 3D survey (My_F3_Survey)를 생성한다. 매뉴얼 1.2.2a에 따라 ini...`
- context length: 14652 chars, 9 chunk headers

**Retrieved chunks (Section / order)**:
  1. 1.2.2a Survey Setup & Load SEG-Y
  2. 1.2.2a Survey Setup & Load SEG-Y
  3. 1.4.4f Setup Survey For Depth Converted Data
  4. 1.2.2a Survey Setup & Load SEG-Y
  5. 1.2.2 SEG-Y Scan Setup & Load
  6. 1.2.2a Survey Setup & Load SEG-Y
  7. 1.2.2a Survey Setup & Load SEG-Y
  8. 1.2.2a Survey Setup & Load SEG-Y
  9. 1.4.4f Setup Survey For Depth Converted Data

### opendtect__3d_visualization__01

- query prefix: `F3 Demo survey에서 seismic 볼륨을 In-line, Cross-line, Z-slice로 3D scene에 표시한다. 각 카테고리 우클릭 시 컨텍스트 메뉴 최상단의...`
- context length: 18814 chars, 11 chunk headers

**Retrieved chunks (Section / order)**:
  1. 1.2.1 Survey Definition
  2. 2.5.1a Coloured Inversion
  3. 1.5 Attribute Analysis & Cross-plots
  4. 1.4.4f Setup Survey For Depth Converted Data
  5. 1.2.2a Survey Setup & Load SEG-Y
  6. 2.5.1a Coloured Inversion
  7. 2.5.1a Coloured Inversion
  8. 1.5 Attribute Analysis & Cross-plots
  9. 1.4.4f Setup Survey For Depth Converted Data
  10. 1.2.2a Survey Setup & Load SEG-Y
  11. 1.2.2a Survey Setup & Load SEG-Y

### opendtect__attribute_computation__01

- query prefix: `F3 Demo survey에서 Energy 속성을 정의하고 In-line 250에 on-the-fly로 표시한다. 매뉴얼 1.5.1a에 따라 툴바의 Attribute 3D 아이콘으...`
- context length: 21829 chars, 15 chunk headers

**Retrieved chunks (Section / order)**:
  1. 2.3.1g Dip-steered Fault Enhancement Filter
  2. 1.5.2a Spectral Decomposition
  3. 2.3.1f Dip-steered Diffusion Filter
  4. 2.3.2b Volume Curvature And Others
  5. 2.5.1a Coloured Inversion
  6. 2.3.1g Dip-steered Fault Enhancement Filter
  7. 2.3.1g Dip-steered Fault Enhancement Filter
  8. 1.5.2a Spectral Decomposition
  9. 1.5.2a Spectral Decomposition
  10. 2.3.1f Dip-steered Diffusion Filter
  11. 2.3.1f Dip-steered Diffusion Filter
  12. 2.3.2b Volume Curvature And Others
  13. 2.3.2b Volume Curvature And Others
  14. 2.5.1a Coloured Inversion
  15. 2.5.1a Coloured Inversion

## Full_system routing distribution

Aggregated across all replicates of `unified3` full_system runs. Reads `picked_node_id` / `picked_workflow_id` from each `per_step` record.

### opendtect__survey_setup__01

- steps scanned across all replicates: 80

**Workflow distribution**:
  - `survey_setup`: 75 steps
  - `d3_visualization`: 5 steps

**Node distribution (top 10)**:
  - `survey_setup_03_choose_initial_setup`: 40 steps (mean conf 0.938)
  - `survey_setup_01_open_selection`: 20 steps (mean conf 0.95)
  - `survey_setup_05_select_survey`: 15 steps (mean conf 0.833)
  - `d3_visualization_01_main_window_ready`: 5 steps (mean conf 0.95)

### opendtect__3d_visualization__01

- steps scanned across all replicates: 80

**Workflow distribution**:
  - `d3_visualization`: 80 steps

**Node distribution (top 10)**:
  - `d3_visualization_01_main_window_ready`: 50 steps (mean conf 0.886)
  - `d3_visualization_05_all_slices_displayed`: 30 steps (mean conf 0.713)

### opendtect__attribute_computation__01

- steps scanned across all replicates: 160

**Workflow distribution**:
  - `seismic_attribute`: 76 steps
  - `d3_visualization`: 54 steps
  - `horizon_tracking`: 13 steps

**Node distribution (top 10)**:
  - `seismic_attribute_04_configure`: 76 steps (mean conf 0.912)
  - `d3_visualization_01_main_window_ready`: 48 steps (mean conf 0.676)
  - `horizon_tracking_08_save`: 13 steps (mean conf 0.612)
  - `d3_visualization_05_all_slices_displayed`: 6 steps (mean conf 0.6)

## Prediction judgment

Fill after inspecting the two sections above:

- **vanilla — attribute scenario**: retrieved chunks' Section field
  - Expected (if prediction confirmed): §1.5.1 (theory p117) or
    unrelated sections dominate; §1.5.1a procedural (p118-128) absent/low.
  - Observed: <fill in from Section list above>

- **full_system — attribute scenario**: workflow distribution
  - Expected (if prediction confirmed): `seismic_attribute` workflow
    dominates. Nodes linked to procedural chunks (`_04_configure`,
    `_06_display`) hit consistently.
  - Observed: <fill in from workflow/node distribution above>

- **Comparison to existing 2 scenarios**: cross-scenario Δ (full − vanilla)
  step_acc + faithfulness should be larger for attribute than for the two
  original scenarios if the retrieval-structuring mechanism dominates.
  See `stats_audit.py --tag unified3` output.

