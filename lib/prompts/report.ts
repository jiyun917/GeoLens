interface CaptureInfo {
  description: string;
  dataType: string;
}

export type ReportLanguage = "ko" | "en";
export type ReportTemplate = "detailed" | "academic" | "brief" | "qc" | "custom";

export interface ReportSectionDef {
  id: string;
  en: string;
  ko: string;
  promptEn: string;
  promptKo: string;
}

export const ALL_SECTIONS: ReportSectionDef[] = [
  { id: "data_overview", en: "Data Overview", ko: "자료 개요",
    promptEn: "## Data Overview\n- Data type, acquisition parameters, coverage area, and data quality assessment (2-3 lines)\n",
    promptKo: "## 자료 개요\n- 자료 종류, 취득 파라미터, 범위, 품질 평가 (2-3줄)\n" },
  { id: "abstract", en: "Abstract", ko: "요약",
    promptEn: "## Abstract\n- Objective, methods, key findings, significance (3-4 lines)\n",
    promptKo: "## 요약\n- 목적, 방법, 주요 발견, 의의 (3-4줄)\n" },
  { id: "methods", en: "Data and Methods", ko: "자료 및 방법",
    promptEn: "## Data and Methods\n- Data type, acquisition, processing, interpretation methodology (3-5 lines)\n",
    promptKo: "## 자료 및 방법\n- 자료 종류, 취득, 처리, 해석 방법론 (3-5줄)\n" },
  { id: "observations", en: "Key Observations", ko: "주요 관찰",
    promptEn: "## Key Observations\n- Describe what you see: reflector patterns, amplitude variations, curve shapes, anomaly distributions (4-6 lines)\n- Be specific: reference locations (left/center/right, shallow/deep)\n",
    promptKo: "## 주요 관찰\n- 이미지에서 보이는 것을 구체적으로 기술: 반사면 패턴, 진폭 변화, 커브 형태, 이상대 분포 (4-6줄)\n- 위치를 명시 (예: 단면 좌측/중앙/우측, 천부/심부)\n" },
  { id: "structural", en: "Structural Interpretation", ko: "구조 해석",
    promptEn: "## Structural Interpretation\n- Identify faults (type, dip, displacement), folds (geometry, wavelength), fracture zones (3-5 lines)\n- Deformation history: timing, overprinting, reactivation\n- Relate to regional tectonic framework\n",
    promptKo: "## 구조 해석\n- 단층(유형, 경사, 변위량), 습곡(기하, 파장), 파쇄대 식별 (3-5줄)\n- 변형사: 시기적 선후관계, 중첩 변형, 재활성화\n- 지역 지구조 환경과의 연관성\n" },
  { id: "stratigraphic", en: "Stratigraphic Interpretation", ko: "층서 해석",
    promptEn: "## Stratigraphic Interpretation\n- Key surfaces: sequence boundaries, flooding surfaces, unconformities (3-5 lines)\n- Depositional units: geometry, stacking patterns (progradation, retrogradation, aggradation)\n- Depositional environments and facies\n",
    promptKo: "## 층서 해석\n- 주요 층서면: 시퀀스 경계, 범람면, 부정합 (3-5줄)\n- 퇴적 단위: 형태, 적층 패턴(전진, 후퇴, 수직적층)\n- 퇴적환경 및 상 분포 해석\n" },
  { id: "process", en: "Geological Process Analysis", ko: "지질학적 과정 분석",
    promptEn: "## Geological Process Analysis\n- Geological processes that produced the observed features (2-4 lines)\n- Temporal evolution in chronological order\n- Fluid migration, diagenesis, post-depositional modification indicators\n",
    promptKo: "## 지질학적 과정 분석\n- 관찰된 특징을 형성한 지질학적 과정 (2-4줄)\n- 시간적 변화: 지질 역사를 시간 순서로 복원\n- 유체 이동, 속성작용, 퇴적 후 변형의 지시자\n" },
  { id: "discussion", en: "Interpretation and Discussion", ko: "해석 및 논의",
    promptEn: "## Interpretation and Discussion\n- Structural interpretation with evidence (3-5 lines)\n- Stratigraphic interpretation and depositional model (3-5 lines)\n- Comparison with published models (2-3 lines)\n- Limitations and alternatives (2-3 lines)\n",
    promptKo: "## 해석 및 논의\n- 구조 해석과 근거 (3-5줄)\n- 층서 해석 및 퇴적 모델 (3-5줄)\n- 기존 연구와의 비교 (2-3줄)\n- 한계점 및 대안적 해석 (2-3줄)\n" },
  { id: "cross_comparison", en: "Cross-Comparison Analysis", ko: "교차 대비 분석",
    promptEn: "## Cross-Comparison Analysis\n- Spatial/depth correlations between different data types (2-4 lines)\n- Distinguish multi-dataset vs single-source interpretations\n",
    promptKo: "## 교차 대비 분석\n- 서로 다른 자료 간 공간적/심도적 대응 관계 (2-4줄)\n- 복수 자료 지지 해석과 단일 자료 기반 해석 구분\n" },
  { id: "summary", en: "Summary and Recommendations", ko: "종합 평가 및 제언",
    promptEn: "## Summary and Recommendations\n- Key conclusions integrating interpretations (2-3 lines)\n- Geological significance (1-2 lines)\n- Suggested follow-up analyses (1-2 lines)\n",
    promptKo: "## 종합 평가 및 제언\n- 해석을 통합한 핵심 결론 (2-3줄)\n- 지질학적 의의 (1-2줄)\n- 추가 분석 방향 제안 (1-2줄)\n" },
  { id: "conclusions", en: "Conclusions", ko: "결론",
    promptEn: "## Conclusions\n- Numbered key conclusions (3-5 lines)\n- Implications for exploration/research (1-2 lines)\n- Recommendations for future work (1-2 lines)\n",
    promptKo: "## 결론\n- 번호 매긴 핵심 결론 (3-5줄)\n- 탐사/연구 시사점 (1-2줄)\n- 향후 연구 방향 (1-2줄)\n" },
  // === QC (Quality Control) sections ===
  { id: "qc_data_info", en: "Data Information", ko: "자료 정보",
    promptEn: "## Data Information\n- Data type, format, acquisition parameters if identifiable (2-3 lines)\n- Coverage, line/trace count, sampling interval, record length\n",
    promptKo: "## 자료 정보\n- 자료 종류, 포맷, 취득 파라미터 (2-3줄)\n- 범위, 라인/트레이스 수, 샘플링 간격, 기록 길이\n" },
  { id: "qc_noise", en: "Noise Assessment", ko: "노이즈 평가",
    promptEn: "## Noise Assessment\n- Overall noise level: Good / Moderate / Poor\n- Noise types identified: random noise, coherent noise, ground roll, air wave, cultural noise (2-4 lines)\n- Signal-to-noise ratio assessment by depth/time zone\n- Frequency band: dominant frequency, bandwidth adequacy for target depth\n",
    promptKo: "## 노이즈 평가\n- 전체 노이즈 수준: 양호 / 보통 / 불량\n- 식별된 노이즈 유형: 랜덤 노이즈, 코히런트 노이즈, 지표파, 공중파, 인공 노이즈 (2-4줄)\n- 심도/시간 구간별 신호 대 잡음비 평가\n- 주파수 대역: 우세 주파수, 목표 심도 대비 대역폭 적정성\n" },
  { id: "qc_reflector", en: "Reflector Quality", ko: "반사면 품질",
    promptEn: "## Reflector / Signal Quality\n- Reflector continuity: Continuous / Intermittent / Poor (by zone)\n- Multiple reflections: present / absent, type (water-bottom, peg-leg, interbed)\n- Amplitude consistency across the section\n- Phase consistency and polarity\n- Migration artifacts or velocity pull-up/push-down\n",
    promptKo: "## 반사면 / 신호 품질\n- 반사면 연속성: 연속적 / 단속적 / 불량 (구간별)\n- 다중반사(멀티플): 유무, 유형 (해저면, 페그레그, 층간)\n- 단면 전체 진폭 일관성\n- 위상 일관성 및 극성\n- 구조보정 인공물 또는 속도 풀업/푸시다운\n" },
  { id: "qc_artifacts", en: "Artifacts & Anomalies", ko: "인공물 및 이상",
    promptEn: "## Artifacts & Anomalies\n- Missing traces or dead traces: location, extent\n- Amplitude anomalies: abnormally high/low zones\n- Processing artifacts: ringing, edge effects, operator artifacts\n- Spatial aliasing indicators\n- DC bias or baseline drift\n",
    promptKo: "## 인공물 및 이상\n- 결측 트레이스 / 불량 트레이스: 위치, 범위\n- 진폭 이상: 비정상적으로 높거나 낮은 구간\n- 처리 인공물: 링잉, 에지 효과, 오퍼레이터 인공물\n- 공간 앨리어싱 지시자\n- DC 바이어스 또는 기준선 드리프트\n" },
  { id: "qc_welllog", en: "Well Log QC", ko: "검층 QC",
    promptEn: "## Well Log Quality Control\n- Spike detection: abnormal spikes in curves, location and severity\n- Washout zones: caliper log anomalies, unreliable intervals\n- Sensor malfunction indicators: flat-lining, impossible values, sudden jumps\n- Depth correction: depth shift indicators, casing points\n- Curve consistency: agreement between related curves (e.g., density vs sonic)\n",
    promptKo: "## 검층 품질 관리\n- 스파이크 감지: 커브의 비정상적 스파이크, 위치와 심각도\n- 워시아웃 구간: 캘리퍼 로그 이상, 신뢰성 낮은 구간\n- 센서 오작동 지시자: 플랫라인, 불가능한 값, 급격한 변화\n- 심도 보정: 심도 이동 지시자, 케이싱 포인트\n- 커브 정합성: 관련 커브 간 일치도 (예: 밀도 vs 음파)\n" },
  { id: "qc_verdict", en: "QC Verdict & Recommendations", ko: "QC 판정 및 권고",
    promptEn: "## QC Verdict\n- Overall data quality rating: GOOD / ACCEPTABLE / POOR / REJECT\n- Usability assessment: suitable for interpretation as-is, needs reprocessing, or unusable\n- Specific zones/intervals with quality concerns (list with depth/time ranges)\n\n## Recommendations\n- Required preprocessing steps before interpretation\n- Suggested reprocessing parameters or techniques\n- Areas requiring additional data acquisition\n",
    promptKo: "## QC 판정\n- 전체 자료 품질 등급: 양호 / 허용 / 불량 / 부적합\n- 활용 가능성: 현재 상태로 해석 가능 / 재처리 필요 / 사용 불가\n- 품질 우려 구간 (심도/시간 범위 명시)\n\n## 권고사항\n- 해석 전 필요한 전처리 단계\n- 권장 재처리 파라미터 또는 기법\n- 추가 자료 취득이 필요한 영역\n" },
];

export const PRESET_SECTIONS: Record<string, string[]> = {
  detailed: ["data_overview", "observations", "structural", "stratigraphic", "process", "summary"],
  academic: ["abstract", "methods", "observations", "discussion", "conclusions"],
  brief: ["data_overview", "observations", "summary"],
  qc: ["qc_data_info", "qc_noise", "qc_reflector", "qc_artifacts", "qc_welllog", "qc_verdict"],
};

export function buildCustomFormatSection(sectionIds: string[], isEn: boolean): string {
  const parts = sectionIds.map((id) => {
    const preset = ALL_SECTIONS.find((s) => s.id === id);
    if (preset) return isEn ? preset.promptEn : preset.promptKo;
    // User-typed custom section name
    return `## ${id}\n- Provide detailed analysis for this section (3-5 lines)\n`;
  });
  const totalItems = sectionIds.length <= 3 ? "8-12" : sectionIds.length <= 5 ? "20-30" : "25-35";
  const header = isEn
    ? `# Report Format\nTotal ${totalItems} bullet points. Each bullet: 1-3 sentences.\n\n`
    : `# Report Format\n전체 ${totalItems}개 항목. 각 항목: 1-3문장.\n\n`;
  return header + parts.join("\n");
}

const DATA_TYPE_LABELS: Record<string, string> = {
  seismic: "탄성파 (Seismic)",
  well_log: "검층 (Well Log)",
  gravity: "중력 (Gravity)",
  magnetic: "자력 (Magnetic)",
  gpr: "GPR",
  resistivity: "전기비저항 (Resistivity)",
  geological_map: "지질도 (Geological Map)",
  other: "기타",
};

export function buildReportPrompt(
  topic: string,
  captures?: CaptureInfo[],
  language: ReportLanguage = "ko",
  template: ReportTemplate = "detailed",
  customSections?: string[]
): string {
  const isEn = language === "en";

  let captureSection = "";
  let isMultiData = false;
  const dataTypes = new Set<string>();

  if (captures && captures.length > 0) {
    const captureList = captures
      .map((c, i) => {
        const typeLabel = DATA_TYPE_LABELS[c.dataType] || c.dataType;
        dataTypes.add(c.dataType);
        return `  - Capture ${i + 1} [${typeLabel}]: ${c.description}`;
      })
      .join("\n");

    isMultiData = dataTypes.size > 1;

    captureSection =
      "\n# User-Provided Data Descriptions (IMPORTANT)\n" +
      "The user described each capture below. Use these descriptions as the PRIMARY context for interpretation.\n" +
      captureList;
  }

  const crossSection = isMultiData
    ? "\n# Cross-Interpretation (REQUIRED for multi-data)\n" +
      "Multiple data types are provided. You MUST perform cross-interpretation:\n\n" +
      "Step 4. CROSS-COMPARE\n" +
      "- For each observed feature, check if it is supported or contradicted by other data types.\n" +
      "- Identify spatial/depth correlations between different data.\n" +
      "- Features confirmed by multiple data types get higher confidence.\n" +
      "- Features seen in only one data type should note this in confidence.\n"
    : "";

  const maxBullets = isMultiData ? "20" : "15";

  // === Language-specific sections ===

  const confidenceSection = isEn
    ? "\n# Confidence Level (REQUIRED — Be CONSERVATIVE)\n" +
      "Every bullet point MUST end with a confidence tag: [Confidence: High], [Confidence: Medium], or [Confidence: Low]\n" +
      "- High: ONLY for direct observations (e.g., 'a discontinuity is visible') or interpretations with unambiguous evidence" +
      (isMultiData ? " cross-confirmed by multiple datasets" : "") + "\n" +
      "- Medium: Most interpretations belong here — structural interpretations (e.g., rollover anticline vs velocity pull-up), inferred depositional environments, feature type identification where alternatives exist\n" +
      "- Low: Speculative interpretation, features at resolution limit, or where multiple equally valid explanations exist\n" +
      "- IMPORTANT: Err on the side of Medium/Low. A professional report with conservative confidence is more credible than one where everything is High.\n" +
      "- When assigning Medium or Low, briefly note why (e.g., 'could also be velocity artifact' or 'requires well calibration')\n" +
      '- Format: "- Observation/interpretation [Confidence: Medium]"\n\n'
    : "\n# 신뢰도 (REQUIRED — 보수적으로 평가)\n" +
      "모든 항목 끝에 반드시 신뢰도 태그 부착: [신뢰도: 높음], [신뢰도: 중간], [신뢰도: 낮음]\n" +
      "- 높음: 직접 관찰 사항(예: '불연속면이 관찰됨') 또는 증거가 명확한 해석만 해당" +
      (isMultiData ? ", 복수 자료에서 교차 확인된 경우" : "") + "\n" +
      "- 중간: 대부분의 해석이 여기에 해당 — 구조 해석(예: 롤오버 배사 vs 속도 풀업 효과), 추정 퇴적환경, 대안적 해석이 가능한 피처 식별 등\n" +
      "- 낮음: 추정적 해석, 해상도 한계의 피처, 복수의 동등한 해석이 가능한 경우\n" +
      "- 중요: 의심스러우면 중간/낮음으로 판정. 보수적 신뢰도를 가진 전문적 보고서가 모든 것이 '높음'인 보고서보다 신뢰할 수 있음.\n" +
      "- 중간/낮음 판정 시 간단한 이유 기재 (예: '속도 인공물 가능성 있음', '검층 보정 필요')\n" +
      '- 형식: "- 관찰/해석 내용 [신뢰도: 중간]"\n\n';

  const crossReportSection = isMultiData
    ? isEn
      ? "\n## Cross-Comparison Analysis\n" +
        "- Spatial/depth correlations between different data types (2-4 lines)\n" +
        "- Distinguish interpretations supported by multiple datasets from single-source interpretations\n"
      : "\n## 교차 대비 분석\n" +
        "- 서로 다른 자료 간 관찰의 공간적/심도적 대응 관계 (2-4줄)\n" +
        "- 복수 자료가 지지하는 해석과 단일 자료 기반 해석 구분\n"
    : "";

  // === Template-specific format ===
  let reportFormatSection = "";

  if (template === "custom" && customSections?.length) {
    reportFormatSection = buildCustomFormatSection(customSections, isEn);
  } else if (template === "qc") {
    reportFormatSection = isEn
      ? "# Report Format (Data Quality Control)\n" +
        "Total 20-30 items. Rate each item: GOOD / ACCEPTABLE / POOR.\n\n" +
        "## Data Information\n- Data type, format, acquisition parameters (2-3 lines)\n\n" +
        "## Noise Assessment\n- Noise level, types, S/N ratio by zone, frequency adequacy (3-5 lines)\n\n" +
        "## Reflector / Signal Quality\n- Continuity, multiples, amplitude consistency, phase, artifacts (3-5 lines)\n\n" +
        "## Artifacts & Anomalies\n- Missing traces, amplitude anomalies, processing artifacts, aliasing (3-5 lines)\n\n" +
        "## Well Log QC (if applicable)\n- Spikes, washout, sensor issues, depth correction, curve consistency (3-5 lines)\n\n" +
        "## QC Verdict\n- Overall rating: GOOD / ACCEPTABLE / POOR / REJECT (1-2 lines)\n- Usability: ready for interpretation / needs reprocessing / unusable\n- Problem zones with depth/time ranges\n\n" +
        "## Recommendations\n- Required preprocessing, reprocessing suggestions, additional data needs (2-4 lines)\n\n"
      : "# Report Format (데이터 품질 관리)\n" +
        "전체 20-30개 항목. 각 항목 평가: 양호 / 허용 / 불량.\n\n" +
        "## 자료 정보\n- 자료 종류, 포맷, 취득 파라미터 (2-3줄)\n\n" +
        "## 노이즈 평가\n- 노이즈 수준, 유형, 구간별 S/N비, 주파수 적정성 (3-5줄)\n\n" +
        "## 반사면 / 신호 품질\n- 연속성, 멀티플, 진폭 일관성, 위상, 인공물 (3-5줄)\n\n" +
        "## 인공물 및 이상\n- 결측 트레이스, 진폭 이상, 처리 인공물, 앨리어싱 (3-5줄)\n\n" +
        "## 검층 QC (해당 시)\n- 스파이크, 워시아웃, 센서 이상, 심도 보정, 커브 정합성 (3-5줄)\n\n" +
        "## QC 판정\n- 전체 등급: 양호 / 허용 / 불량 / 부적합 (1-2줄)\n- 활용성: 해석 가능 / 재처리 필요 / 사용 불가\n- 문제 구간 (심도/시간 범위)\n\n" +
        "## 권고사항\n- 필요 전처리, 재처리 권장사항, 추가 자료 필요성 (2-4줄)\n\n";
  } else if (template === "brief") {
    reportFormatSection = isEn
      ? "# Report Format (Brief Summary)\n" +
        "Total 8-12 bullet points. Concise, A4 half page.\n\n" +
        "## Data Overview\n- Data type and quality (1-2 lines)\n\n" +
        "## Key Findings\n- Most important observations and interpretations combined (4-6 lines)\n" +
        crossReportSection +
        "\n## Conclusion\n- Key takeaway in 1-2 lines\n\n"
      : "# Report Format (간이 보고서)\n" +
        "전체 8-12개 항목. 간결하게, A4 반 페이지.\n\n" +
        "## 자료 개요\n- 자료 종류, 품질 (1-2줄)\n\n" +
        "## 주요 발견\n- 핵심 관찰과 해석을 통합하여 기술 (4-6줄)\n" +
        crossReportSection +
        "\n## 결론\n- 핵심 결론 1-2줄\n\n";
  } else if (template === "academic") {
    reportFormatSection = isEn
      ? "# Report Format (Academic Paper Style)\n" +
        "Total 30-40 bullet points. Formal academic structure.\n\n" +
        "## Abstract\n- Objective, methods, key findings, significance (3-4 lines)\n\n" +
        "## Data and Methods\n- Data type, acquisition, processing, interpretation methodology (3-5 lines)\n\n" +
        "## Observations\n- Systematic description of all observed features with precise locations (5-8 lines)\n" +
        "- Use objective, descriptive language\n\n" +
        "## Interpretation and Discussion\n" +
        "- Structural interpretation with supporting evidence (3-5 lines)\n" +
        "- Stratigraphic interpretation and depositional model (3-5 lines)\n" +
        "- Comparison with published models and regional geology (2-3 lines)\n" +
        "- Limitations and alternative interpretations (2-3 lines)\n" +
        crossReportSection +
        "\n## Conclusions\n- Numbered key conclusions (3-5 lines)\n" +
        "- Implications for exploration/research (1-2 lines)\n" +
        "- Recommendations for future work (1-2 lines)\n\n"
      : "# Report Format (학술 보고서)\n" +
        "전체 30-40개 항목. 학술 논문 구조.\n\n" +
        "## 요약\n- 목적, 방법, 주요 발견, 의의 (3-4줄)\n\n" +
        "## 자료 및 방법\n- 자료 종류, 취득, 처리, 해석 방법론 (3-5줄)\n\n" +
        "## 관찰\n- 모든 관찰된 피처를 체계적으로 기술, 정확한 위치 포함 (5-8줄)\n" +
        "- 객관적이고 서술적인 표현 사용\n\n" +
        "## 해석 및 논의\n" +
        "- 구조 해석과 근거 (3-5줄)\n" +
        "- 층서 해석 및 퇴적 모델 (3-5줄)\n" +
        "- 기존 연구/지역 지질과의 비교 논의 (2-3줄)\n" +
        "- 한계점 및 대안적 해석 (2-3줄)\n" +
        crossReportSection +
        "\n## 결론\n- 번호 매긴 핵심 결론 (3-5줄)\n" +
        "- 탐사/연구에 대한 시사점 (1-2줄)\n" +
        "- 향후 연구 방향 제안 (1-2줄)\n\n";
  } else {
    // detailed (default) - existing format
    reportFormatSection = isEn
      ? "# Report Format (English, bullet points)\n" +
      "Total 25-35 bullet points. Each bullet: 1-3 sentences.\n\n" +
      "## Data Overview\n" +
      "- Data type, acquisition parameters, coverage area, and data quality assessment (2-3 lines)\n\n" +
      "## Key Observations\n" +
      "- Describe WHAT you see: reflector patterns, amplitude variations, curve shapes, anomaly distributions (4-6 lines)\n" +
      "- Be specific: reference locations (e.g., left/center/right of section, shallow/deep)\n\n" +
      "## Structural Interpretation\n" +
      "- Identify and describe structural features: faults (type, dip, displacement), folds (geometry, wavelength, vergence), fracture zones (3-5 lines)\n" +
      "- Describe the deformation history: timing relationships, overprinting, reactivation\n" +
      "- Relate structures to the regional tectonic framework\n\n" +
      "## Stratigraphic Interpretation\n" +
      "- Identify key stratigraphic surfaces: sequence boundaries, flooding surfaces, unconformities (3-5 lines)\n" +
      "- Describe depositional units: geometry (sheet, wedge, mound), stacking patterns (progradation, retrogradation, aggradation)\n" +
      "- Interpret depositional environments and facies distributions based on observed patterns\n\n" +
      "## Geological Process Analysis\n" +
      "- Discuss the geological processes that produced the observed features (2-4 lines)\n" +
      "- Temporal evolution: reconstruct the geological history in chronological order\n" +
      "- Identify any indicators of fluid migration, diagenesis, or post-depositional modification\n" +
      crossReportSection +
      "\n## Summary and Recommendations\n" +
      "- Key conclusions integrating structural and stratigraphic interpretations (2-3 lines)\n" +
      "- Geological significance and implications (1-2 lines)\n" +
      "- Suggested follow-up analyses or additional data needs (1-2 lines)\n\n"
    : "# Report Format (Korean, 개조식)\n" +
      "전체 25-35개 항목. 각 항목: 1-3문장.\n\n" +
      "## 자료 개요\n" +
      "- 자료 종류, 취득 파라미터, 범위, 품질 평가 (2-3줄)\n\n" +
      "## 주요 관찰\n" +
      "- 이미지에서 보이는 것을 구체적으로 기술: 반사면 패턴, 진폭 변화, 커브 형태, 이상대 분포 (4-6줄)\n" +
      "- 위치를 명시 (예: 단면 좌측/중앙/우측, 천부/심부)\n\n" +
      "## 구조 해석\n" +
      "- 구조 요소 식별 및 기술: 단층(유형, 경사, 변위량), 습곡(기하, 파장, 비대칭성), 파쇄대 (3-5줄)\n" +
      "- 변형사 기술: 시기적 선후관계, 중첩 변형, 재활성화 여부\n" +
      "- 지역 지구조 환경과의 연관성 논의\n\n" +
      "## 층서 해석\n" +
      "- 주요 층서면 식별: 시퀀스 경계, 범람면, 부정합 (3-5줄)\n" +
      "- 퇴적 단위 기술: 형태(sheet, wedge, mound), 적층 패턴(전진, 후퇴, 수직적층)\n" +
      "- 관찰된 패턴을 바탕으로 퇴적환경 및 상 분포 해석\n\n" +
      "## 지질학적 과정 분석\n" +
      "- 관찰된 특징을 형성한 지질학적 과정 논의 (2-4줄)\n" +
      "- 시간적 변화: 지질 역사를 시간 순서로 복원\n" +
      "- 유체 이동, 속성작용, 퇴적 후 변형의 지시자 식별\n" +
      crossReportSection +
      "\n## 종합 평가 및 제언\n" +
      "- 구조 및 층서 해석을 통합한 핵심 결론 (2-3줄)\n" +
      "- 지질학적 의의 및 시사점 (1-2줄)\n" +
      "- 추가 분석 방향 또는 필요 자료 제안 (1-2줄)\n\n";
  } // end template switch

  const rulesSection = isEn
    ? "# Rules\n" +
      "- English, bullet points only\n" +
      "- Be thorough and detailed in geological interpretation\n" +
      "- Describe only what is actually observable, but interpret deeply\n" +
      "- Structural interpretations must be consistent with the tectonic setting of the study area\n" +
      "- Do not assert uncertain interpretations — state them as possibilities with reasoning\n" +
      "- Confidence tags are mandatory for every item\n" +
      "- Total length: A4 1 page"
    : "# Rules\n" +
      "- Korean, 개조식 (bullet points only)\n" +
      "- 지질학적 해석은 충분히 상세하게 기술\n" +
      "- 관찰 가능한 것만 기술하되, 해석은 깊이 있게\n" +
      "- 구조 해석은 반드시 해당 지역의 지구조 환경과 일관되어야 함\n" +
      "- 불확실한 해석은 단정 짓지 말고 근거와 함께 가능성으로 기술\n" +
      "- 모든 항목에 신뢰도 태그 필수\n" +
      "- 전체 분량: A4 1페이지";

  const typoSection = isEn
    ? "\n# Terminology Correction\n" +
      "If the topic or descriptions contain apparent typos or misspellings of geological terms, basins, or formations, silently correct them in your report.\n" +
      "Common examples: 'Viking Garden' → 'Viking Graben', 'Brent Gorge' → 'Brent Group', 'Kimmerige' → 'Kimmeridge'.\n" +
      "Use the correct standard geological terminology throughout.\n\n"
    : "\n# 용어 자동 보정\n" +
      "토픽이나 설명에 지질 용어, 분지명, 지층명의 오타가 있으면 보고서에서 올바르게 수정하여 사용하세요.\n" +
      "예: 'Viking Garden' → 'Viking Graben', '동해 분지' → '울릉분지(동해)', 'Kimmerige' → 'Kimmeridge'.\n" +
      "표준 지질 용어를 일관되게 사용하세요.\n\n";

  const datasetSection = isEn
    ? "# Dataset Identification\n" +
      "In the Data Overview section, you MUST include:\n" +
      "- The specific dataset/line name if identifiable from the topic, description, or image (e.g., 'Mobil AVO Viking Graben Line 12')\n" +
      "- If the dataset name is visible in the image header/title bar, extract and use it\n" +
      "- If not identifiable, state 'Dataset name not specified' and describe what can be inferred about the data\n\n"
    : "# 데이터셋 식별\n" +
      "자료 개요 섹션에 반드시 포함:\n" +
      "- 토픽, 설명, 이미지에서 식별 가능한 구체적 데이터셋/라인명 (예: 'Mobil AVO Viking Graben Line 12')\n" +
      "- 이미지 상단/제목에 데이터셋명이 표시되어 있으면 추출하여 사용\n" +
      "- 식별 불가 시 '데이터셋명 미기재'로 표기하고, 자료에서 추론 가능한 정보 기술\n\n";

  const referenceSection = isEn
    ? "# Use of Reference Context\n" +
      "If reference material (manuals, papers) was provided via RAG context, actively cite relevant information:\n" +
      "- Reference specific findings, well results, or published interpretations when they support or contrast with your observations\n" +
      "- Format: mention the source naturally (e.g., 'consistent with the structural model described in the reference material')\n" +
      "- If DHI (Direct Hydrocarbon Indicator) or AVO anomalies are discussed in reference context, incorporate them into your interpretation\n\n"
    : "# 참고자료 활용\n" +
      "RAG 컨텍스트로 제공된 참고자료(매뉴얼, 논문)가 있을 경우 적극 인용:\n" +
      "- 관찰과 일치하거나 대비되는 기존 해석, 시추 결과, 출판 해석을 구체적으로 언급\n" +
      "- 형식: 자연스럽게 출처 언급 (예: '참고자료의 구조 모델과 일치함')\n" +
      "- 참고자료에 DHI(직접 탄화수소 지시자)나 AVO 이상에 대한 논의가 있으면 해석에 반영\n\n";

  const roleDescription = template === "qc"
    ? "You are a geoscience data quality control specialist. Analyze the provided data captures and produce a thorough QC assessment report. Focus on identifying data quality issues, artifacts, and fitness for interpretation — NOT on geological interpretation.\n\n"
    : "You are a geoscience interpretation expert with deep domain knowledge. Analyze the provided screen captures and write a detailed, professional interpretation report.\n\n";

  return (
    roleDescription +
    "# Topic\n" +
    topic +
    "\n" +
    captureSection +
    "\n\n" +
    typoSection +
    datasetSection +
    referenceSection +
    "# Interpretation Methodology (CRITICAL)\n" +
    "You must follow this sequence strictly:\n\n" +
    "Step 1. IDENTIFY CONTEXT\n" +
    "- From the topic, data descriptions, basin/region name, and your geological knowledge, determine the tectonic regime and geological setting of the study area.\n" +
    "- Correct any apparent typos in geographical/geological terms.\n\n" +
    "Step 2. OBSERVE\n" +
    "- Describe only what is visually present in the image: reflector geometry, amplitude patterns, discontinuities, log curve shapes, anomaly patterns, etc.\n" +
    "- Use neutral, descriptive language — do NOT jump to structural terms yet.\n" +
    "- Read any text visible in the image (titles, axis labels, legends) to identify the dataset.\n\n" +
    "Step 3. INTERPRET — CONSISTENT WITH CONTEXT\n" +
    "- Apply structural/stratigraphic terminology ONLY after confirming it is compatible with the tectonic regime identified in Step 1.\n" +
    "- Every structural term must be geologically valid for the identified setting.\n" +
    "- If the image alone is ambiguous, state the uncertainty rather than forcing an interpretation.\n" +
    "- For each interpretation, consider alternative explanations (e.g., structural vs. processing artifact) and note them.\n" +
    crossSection +
    confidenceSection +
    reportFormatSection +
    rulesSection
  );
}
