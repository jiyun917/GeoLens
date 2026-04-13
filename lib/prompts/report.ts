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
    promptEn: "## Data Information\n- Dataset name: Read any visible title, header, or label in the image. If the topic mentions a name (e.g., 'F3 Demo'), use it.\n- Data dimensionality: State if 2D or 3D. IMPORTANT: A single inline or crossline section displayed from a 3D volume is still 3D data — do NOT call it 2D just because you see one section.\n- Data type, format, acquisition parameters if identifiable (2-3 lines)\n- Coverage, line/trace count, sampling interval, record length\n",
    promptKo: "## 자료 정보\n- 데이터셋명: 이미지에 보이는 제목/헤더/라벨을 읽으세요. 토픽에 이름이 있으면 (예: 'F3 Demo') 사용하세요.\n- 자료 차원: 2D인지 3D인지 명시. 중요: 3D 볼륨에서 하나의 인라인/크로스라인 단면을 표시한 것은 여전히 3D 자료입니다. 단면 하나만 보인다고 2D로 판정하지 마세요.\n- 자료 종류, 포맷, 취득 파라미터 (2-3줄)\n- 범위, 라인/트레이스 수, 샘플링 간격, 기록 길이\n" },
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
    promptEn: "## QC Verdict\n- Overall data quality rating: GOOD / ACCEPTABLE / POOR / REJECT\n- Base the rating ONLY on technical quality metrics (noise, S/N, continuity, artifacts) — NOT on geological interpretation\n- Usability assessment: suitable for interpretation as-is, needs reprocessing, or unusable\n- Specific zones/intervals with quality concerns (list with depth/time ranges)\n\n## Recommendations\n- Required preprocessing steps before interpretation (technical only)\n- Suggested reprocessing parameters or techniques\n- Areas requiring additional data acquisition\n- Do NOT include geological interpretation recommendations (faults, horizons, etc.) — QC is about data quality only\n",
    promptKo: "## QC 판정\n- 전체 자료 품질 등급: 양호 / 허용 / 불량 / 부적합\n- 등급은 기술적 품질 지표(노이즈, S/N, 연속성, 인공물)만으로 판정 — 지질학적 해석을 근거로 사용하지 마세요\n- 활용 가능성: 현재 상태로 해석 가능 / 재처리 필요 / 사용 불가\n- 품질 우려 구간 (심도/시간 범위 명시)\n\n## 권고사항\n- 해석 전 필요한 전처리 단계 (기술적 사항만)\n- 권장 재처리 파라미터 또는 기법\n- 추가 자료 취득이 필요한 영역\n- 지질학적 해석 권고(단층, 호라이즌 등)는 포함하지 마세요 — QC는 자료 품질에 대한 것입니다\n" },
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
  const totalItems = sectionIds.length <= 3 ? "8-12" : sectionIds.length <= 5 ? "25-35" : "35-50";
  const header = isEn
    ? `# Report Format\nTotal ${totalItems} bullet points. Each bullet: 1-3 sentences.\nBe THOROUGH — cover every observable feature in detail.\n\n`
    : `# Report Format\n전체 ${totalItems}개 항목. 각 항목: 1-3문장.\n철저하게 — 관찰 가능한 모든 특징을 상세히 기술하세요.\n\n`;
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
    ? "\n# ██ Confidence Tags (MANDATORY — every bullet MUST have one) ██\n" +
      "EVERY bullet point in the report MUST end with exactly one of these tags:\n" +
      "  [Confidence: High]  [Confidence: Medium]  [Confidence: Low]\n\n" +
      "A bullet WITHOUT a tag is a VIOLATION. Check every bullet before finishing.\n\n" +
      "- High: Direct observation clearly visible in the image, or interpretation with unambiguous evidence" +
      (isMultiData ? " cross-confirmed by multiple datasets" : "") + "\n" +
      "- Medium: Most interpretations (default). Structural interpretations, inferred environments, where alternatives exist\n" +
      "- Low: Speculative, at resolution limit, or multiple equally valid explanations\n" +
      "- Err on Medium/Low. Conservative confidence = more credible.\n" +
      '- Exact format example:\n  "- The reflector shows 30ms offset, interpreted as a normal fault [Confidence: Medium]"\n\n'
    : "\n# ██ 신뢰도 태그 (필수 — 모든 항목에 반드시 부착) ██\n" +
      "리포트의 모든 불릿 항목 끝에 반드시 아래 태그 중 하나를 부착하세요:\n" +
      "  [신뢰도: 높음]  [신뢰도: 중간]  [신뢰도: 낮음]\n\n" +
      "태그가 없는 항목은 규칙 위반입니다. 작성 완료 후 모든 항목을 검토하세요.\n\n" +
      "- 높음: 이미지에서 명확히 보이는 직접 관찰, 또는 증거가 확실한 해석" +
      (isMultiData ? ", 복수 자료에서 교차 확인된 경우" : "") + "\n" +
      "- 중간: 대부분의 해석 (기본값). 구조 해석, 추정 환경, 대안 가능한 경우\n" +
      "- 낮음: 추정적 해석, 해상도 한계, 동등한 대안이 여러 개인 경우\n" +
      "- 의심스러우면 중간/낮음 판정. 보수적 = 더 신뢰할 수 있음.\n" +
      '- 정확한 형식 예시:\n  "- 반사면에서 약 30ms의 변위가 관찰되며 정단층으로 해석됨 [신뢰도: 중간]"\n\n';

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
        "## Data Information\n" +
        "- Dataset name: identify from image title/header or topic. If the topic says 'F3 Demo', the dataset is F3.\n" +
        "- Dimensionality: 2D or 3D. A single inline/crossline section from a 3D volume is STILL 3D data.\n" +
        "- Data type, format, acquisition parameters (2-3 lines)\n\n" +
        "## Noise Assessment\n- Noise level, types, S/N ratio by zone, frequency adequacy (3-5 lines)\n\n" +
        "## Reflector / Signal Quality\n- Continuity, multiples, amplitude consistency, phase, artifacts (3-5 lines)\n" +
        "- Describe ONLY what you observe technically. Do NOT add geological interpretation (no faults, no anticlines, no rift terminology).\n\n" +
        "## Artifacts & Anomalies\n- Missing traces, amplitude anomalies, processing artifacts, aliasing (3-5 lines)\n" +
        "- Describe amplitude anomalies as technical observations, NOT as geological features.\n\n" +
        "## Well Log QC (if applicable)\n- Spikes, washout, sensor issues, depth correction, curve consistency (3-5 lines)\n\n" +
        "## QC Verdict\n- Overall rating: GOOD / ACCEPTABLE / POOR / REJECT\n" +
        "- Base rating ONLY on technical metrics. Do NOT reference geological structures.\n" +
        "- Usability: ready for interpretation / needs reprocessing / unusable\n- Problem zones with depth/time ranges\n\n" +
        "## Recommendations\n- Technical preprocessing/reprocessing only. No geological interpretation recommendations. (2-4 lines)\n\n"
      : "# Report Format (데이터 품질 관리)\n" +
        "전체 20-30개 항목. 각 항목 평가: 양호 / 허용 / 불량.\n\n" +
        "## 자료 정보\n- 자료 종류, 포맷, 취득 파라미터 (2-3줄)\n\n" +
        "## 노이즈 평가\n- 노이즈 수준, 유형, 구간별 S/N비, 주파수 적정성 (3-5줄)\n\n" +
        "## 반사면 / 신호 품질\n- 연속성, 멀티플, 진폭 일관성, 위상, 인공물 (3-5줄)\n\n" +
        "## 인공물 및 이상\n- 결측 트레이스, 진폭 이상, 처리 인공물, 앨리어싱 (3-5줄)\n\n" +
        "## 검층 QC (해당 시)\n- 스파이크, 워시아웃, 센서 이상, 심도 보정, 커브 정합성 (3-5줄)\n\n" +
        "## 자료 정보\n" +
        "- 데이터셋명: 이미지 제목/헤더 또는 토픽에서 식별. 토픽에 'F3 Demo'가 있으면 해당 데이터셋입니다.\n" +
        "- 차원: 2D 또는 3D. 3D 볼륨의 인라인/크로스라인 단면 하나는 여전히 3D 자료입니다.\n" +
        "- 자료 종류, 포맷, 취득 파라미터 (2-3줄)\n\n" +
        "## 노이즈 평가\n- 노이즈 수준, 유형, 구간별 S/N비, 주파수 적정성 (3-5줄)\n\n" +
        "## 반사면 / 신호 품질\n- 연속성, 멀티플, 진폭 일관성, 위상, 인공물 (3-5줄)\n" +
        "- 기술적 관찰만 기술. 지질학적 해석(단층, 배사, 리프트 등)을 추가하지 마세요.\n\n" +
        "## 인공물 및 이상\n- 결측 트레이스, 진폭 이상, 처리 인공물, 앨리어싱 (3-5줄)\n" +
        "- 진폭 이상은 기술적 관찰로 기술. 지질학적 특징으로 해석하지 마세요.\n\n" +
        "## 검층 QC (해당 시)\n- 스파이크, 워시아웃, 센서 이상, 심도 보정, 커브 정합성 (3-5줄)\n\n" +
        "## QC 판정\n- 전체 등급: 양호 / 허용 / 불량 / 부적합\n" +
        "- 기술적 지표만으로 판정. 지질 구조를 근거로 사용하지 마세요.\n" +
        "- 활용성: 해석 가능 / 재처리 필요 / 사용 불가\n- 문제 구간 (심도/시간 범위)\n\n" +
        "## 권고사항\n- 기술적 전처리/재처리만. 지질학적 해석 권고 없음. (2-4줄)\n\n";
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
    // detailed (default) - comprehensive format
    reportFormatSection = isEn
      ? "# Report Format (Detailed Exploration Report)\n" +
      "Total 35-50 bullet points. Each bullet: 1-3 sentences. Be EXHAUSTIVE.\n\n" +
      "## Data Overview\n" +
      "- Dataset name/identification (3-4 lines)\n" +
      "- Data type, acquisition parameters, coverage, vertical/horizontal axis units\n" +
      "- Data quality assessment: signal-to-noise, frequency content, resolution\n\n" +
      "## Key Observations (describe EVERYTHING visible — 8-12 lines)\n" +
      "- Identify and describe ALL visible reflectors/features with their locations\n" +
      "- Amplitude patterns: high/low/variable, spatial distribution\n" +
      "- Continuity: which reflectors are continuous, which are disrupted?\n" +
      "- Key horizons: describe the boundary reflectors between units (amplitude, continuity, shape)\n" +
      "- Relative spatial descriptions: 'left vs right', 'shallow vs deep', asymmetry\n" +
      "- Any anomalous zones: blanking, chaotic, transparent areas\n\n" +
      "## Structural Interpretation (6-10 lines)\n" +
      "- Identify EACH structural feature with visual evidence and location\n" +
      "- Fault checklist: offset visible? terminations? dip direction? → type determination\n" +
      "- For each structure: observation → evidence → interpretation\n" +
      "- Tectonic consistency: verify all structures match the regional setting\n" +
      "- Deformation history: timing, sequence, reactivation\n" +
      "- Salt/diapir features: draping vs onlap patterns, rim syncline symmetry\n\n" +
      "## Stratigraphic Interpretation (6-10 lines)\n" +
      "- Identify ALL key stratigraphic surfaces with visual criteria\n" +
      "- Clinoform analysis: direction, geometry (sigmoidal/oblique), stacking\n" +
      "- Sequence stratigraphy: systems tracts, key surfaces\n" +
      "- Depositional environments and facies interpretation\n" +
      "- Thickness variations and their significance\n\n" +
      "## Geological Process Analysis (4-8 lines)\n" +
      "- Geological processes with chronological order\n" +
      "- Temporal evolution: step-by-step geological history\n" +
      "- Fluid migration, diagenesis, post-depositional modifications\n" +
      "- Alternative process interpretations\n" +
      crossReportSection +
      "\n## Summary and Recommendations (4-6 lines)\n" +
      "- Key conclusions integrating ALL interpretations\n" +
      "- Geological significance, implications for exploration\n" +
      "- Confidence summary: what is well-constrained vs uncertain\n" +
      "- Suggested follow-up: additional data, processing, analyses\n\n"
    : "# Report Format (상세 해석 보고서)\n" +
      "전체 35-50개 항목. 각 항목: 1-3문장. 철저하고 빠짐없이 기술하세요.\n\n" +
      "## 자료 개요\n" +
      "- 데이터셋 식별/명칭 (3-4줄)\n" +
      "- 자료 종류, 취득 파라미터, 범위, 수직/수평축 단위\n" +
      "- 자료 품질: 신호대잡음비, 주파수 대역, 해상도\n\n" +
      "## 주요 관찰 (보이는 모든 것을 기술 — 8-12줄)\n" +
      "- 식별 가능한 모든 반사면/피처를 위치와 함께 기술\n" +
      "- 진폭 패턴: 고/저/가변, 공간적 분포\n" +
      "- 연속성: 연속적 vs 단속적 반사면 구분\n" +
      "- 핵심 반사면(Key Horizon): 층서단위 경계 반사면의 진폭, 연속성, 형태를 명시\n" +
      "- 상대적 공간 기술: '좌측 vs 우측', '천부 vs 심부', 대칭/비대칭\n" +
      "- 이상 구간: 블랭킹, 혼탁, 투명 영역\n\n" +
      "## 구조 해석 (6-10줄)\n" +
      "- 각 구조 요소를 시각적 근거 + 위치와 함께 기술\n" +
      "- 단층 체크리스트: 변위(offset) 확인? 종단(termination)? 경사 방향? → 단층 유형 결정\n" +
      "- 각 구조: 관찰 → 근거 → 해석 패턴으로 기술\n" +
      "- 지구조 일관성: 모든 구조가 지역 환경과 일치하는지 검증\n" +
      "- 변형사: 시기, 순서, 재활성화\n" +
      "- 암염/다이어피르: draping vs onlap 패턴, 림싱크라인 대칭성\n\n" +
      "## 층서 해석 (6-10줄)\n" +
      "- 모든 주요 층서면을 시각적 기준과 함께 식별\n" +
      "- 클리노폼 분석: 방향, 형태(시그모이달/오블리크), 적층 패턴\n" +
      "- 시퀀스 층서: 체계역, 핵심 층서면\n" +
      "- 퇴적환경 및 상 해석\n" +
      "- 두께 변화와 그 의미\n\n" +
      "## 지질학적 과정 분석 (4-8줄)\n" +
      "- 지질학적 과정을 시간 순서로 기술\n" +
      "- 시간적 변화: 단계별 지질 역사 복원\n" +
      "- 유체 이동, 속성작용, 퇴적 후 변형\n" +
      "- 대안적 과정 해석\n" +
      crossReportSection +
      "\n## 종합 평가 및 제언 (4-6줄)\n" +
      "- 모든 해석을 통합한 핵심 결론\n" +
      "- 지질학적 의의, 탐사 시사점\n" +
      "- 신뢰도 요약: 확실한 것 vs 불확실한 것\n" +
      "- 추가 자료, 처리, 분석 방향 제안\n\n";
  } // end template switch

  const rulesSection = isEn
    ? "# Writing Style & Formatting Rules\n" +
      "- Write in English. Use a professional, polished report style.\n" +
      "- Mix **narrative paragraphs** and bullet points — do NOT write everything as bullets.\n" +
      "  - Section intros: 1-2 sentence paragraph summarizing the section, then bullets for details.\n" +
      "  - Key findings: use bold (**bold**) for important terms, structure names, and conclusions.\n" +
      "- Use **horizontal rules** (---) between major sections for visual separation.\n" +
      "- Be thorough and detailed in geological interpretation\n" +
      "- Describe only what is actually observable, but interpret deeply\n" +
      "- Structural interpretations must be consistent with the tectonic setting of the study area\n" +
      "- Name specific formations, groups, and geological units when the region is identifiable\n" +
      "- Include fault/structure generation history when multiple phases are evident\n" +
      "- Do not assert uncertain interpretations — state them as possibilities with reasoning\n" +
      "- Confidence tags are mandatory for every item\n" +
      "- Total length: A4 1-2 pages\n" +
      "- Make the report visually organized and easy to read\n" +
      "- Do NOT include author names, reviewer names, roles (e.g., 'Senior Researcher'), or any personnel information in the report body"
    : "# 작성 스타일 및 서식 규칙\n" +
      "- 한국어로 작성. 전문적이고 정돈된 보고서 스타일.\n" +
      "- **서술형 문단**과 개조식(bullet)을 혼합 — 모든 것을 개조식으로만 쓰지 마세요.\n" +
      "  - 각 섹션 시작: 1-2문장의 요약 문단을 쓰고, 세부 사항은 개조식으로.\n" +
      "  - 핵심 용어, 구조명, 결론은 **굵게(bold)** 처리.\n" +
      "- 주요 섹션 사이에 **수평선**(---)을 넣어 시각적으로 구분.\n" +
      "- 지질학적 해석은 충분히 상세하게 기술\n" +
      "- 관찰 가능한 것만 기술하되, 해석은 깊이 있게\n" +
      "- 구조 해석은 반드시 해당 지역의 지구조 환경과 일관되어야 함\n" +
      "- 지역이 식별되면 구체적 지층명/그룹명을 사용 (예: '암염' 대신 'Zechstein 암염')\n" +
      "- 다수의 구조 운동이 관찰되면 단층/구조 세대 구분과 운동사를 포함\n" +
      "- 불확실한 해석은 단정 짓지 말고 근거와 함께 가능성으로 기술\n" +
      "- 모든 항목에 신뢰도 태그 필수\n" +
      "- 전체 분량: A4 1-2페이지\n" +
      "- 보고서 본문에 작성자, 검토자, 직책(예: '선임 연구원') 등 인적 정보를 포함하지 마세요\n" +
      "- 보고서가 시각적으로 정돈되고 읽기 쉽도록 작성";

  const structuresSection = isEn
    ? '\n\n# Structure Labels (MANDATORY — DO NOT SKIP)\n' +
      'You MUST end your report with a ```structures code block containing a JSON array.\n' +
      'This identifies key geological structures and their location in the image (3x3 grid).\n' +
      'Example (you MUST output something like this):\n' +
      '```structures\n' +
      '[{"type":"anticline","label":"Anticline","position":"mid-center"},{"type":"normal_fault","label":"Normal Fault","position":"mid-left"}]\n' +
      '```\n' +
      'Valid types: salt_diapir, normal_fault, reverse_fault, unconformity, anticline, syncline, growth_strata, horizon, amplitude_anomaly, channel, delta, reef\n' +
      'Valid positions: top-left, top-center, top-right, mid-left, mid-center, mid-right, bottom-left, bottom-center, bottom-right\n' +
      'Rules: max 8, determine position from the ACTUAL IMAGE, skip basement/post_kinematic\n'
    : '\n\n# 구조 라벨 (반드시 출력 — 생략 금지)\n' +
      '리포트 맨 마지막에 반드시 ```structures 코드블록으로 JSON 배열을 출력하세요.\n' +
      '이미지에서 식별한 주요 지질 구조와 위치(3x3 그리드)를 표시합니다.\n' +
      '예시 (반드시 이런 형태로 출력):\n' +
      '```structures\n' +
      '[{"type":"anticline","label":"배사 구조","position":"mid-center"},{"type":"normal_fault","label":"정단층","position":"mid-left"}]\n' +
      '```\n' +
      'type: salt_diapir, normal_fault, reverse_fault, unconformity, anticline, syncline, growth_strata, horizon, amplitude_anomaly, channel, delta, reef\n' +
      'position: top-left, top-center, top-right, mid-left, mid-center, mid-right, bottom-left, bottom-center, bottom-right\n' +
      '규칙: 최대 8개, 실제 이미지를 보고 위치 판단, basement/post_kinematic 제외\n';

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
      "- The specific dataset/line name if identifiable from the topic, description, or image (e.g., 'Mobil AVO Viking Graben Line 12', 'F3 Demo 2023')\n" +
      "- If the dataset name is visible in the image header/title bar, extract and use it\n" +
      "- If not identifiable, state 'Dataset name not specified' and describe what can be inferred about the data\n" +
      "- 2D vs 3D: A single inline/crossline section displayed from a 3D volume is STILL 3D data. Only call it 2D if it is a standalone 2D line.\n" +
      "- IMPORTANT: Do NOT apply geological context from one dataset to another. Each dataset has its own geological setting. F3 (Netherlands) ≠ Viking Graben (Norway).\n\n"
    : "# 데이터셋 식별\n" +
      "자료 개요 섹션에 반드시 포함:\n" +
      "- 토픽, 설명, 이미지에서 식별 가능한 구체적 데이터셋/라인명 (예: 'Mobil AVO Viking Graben Line 12', 'F3 Demo 2023')\n" +
      "- 이미지 상단/제목에 데이터셋명이 표시되어 있으면 추출하여 사용\n" +
      "- 식별 불가 시 '데이터셋명 미기재'로 표기하고, 자료에서 추론 가능한 정보 기술\n" +
      "- 2D vs 3D: 3D 볼륨에서 인라인/크로스라인 단면 하나를 표시한 것은 여전히 3D 자료입니다. 독립 2D 라인인 경우에만 2D로 기재.\n" +
      "- 중요: 하나의 데이터셋의 지질 맥락을 다른 데이터셋에 적용하지 마세요. F3(네덜란드) ≠ Viking Graben(노르웨이).\n\n";

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
    ? "You are a geoscience data quality control specialist. Analyze the provided data captures and produce a thorough QC assessment report.\n\n" +
      "# QC RULES (CRITICAL)\n" +
      "1. QC is about TECHNICAL DATA QUALITY only — noise, S/N ratio, continuity, artifacts, frequency content, multiple removal, trace quality.\n" +
      "2. The MAJORITY of the report (>70%) must be technical quality metrics. Geological interpretation should be minimal or absent.\n" +
      "3. Do NOT structure the report as an interpretation report. Structure it as: Data Info → Noise → Signal Quality → Artifacts → Verdict → Recommendations.\n" +
      "4. Dataset identification: If the topic contains a name (e.g., 'F3', 'Viking Graben'), that IS the dataset name — state it definitively, not as 'possibly' or 'presumed'.\n" +
      "5. 2D vs 3D: A single inline or crossline section displayed from a 3D survey is STILL 3D data. Only classify as 2D if you have explicit evidence.\n" +
      "6. Amplitude anomalies should be described as technical observations (e.g., 'amplitude brightening at 1200ms'), NOT as geological features.\n" +
      "7. For well-known datasets (F3, Penobscot, Poseidon, etc.), mention known properties: included wells, survey size, sampling interval if you know them.\n" +
      "8. Do NOT apply geological context from one dataset to another.\n\n"
    : "You are a senior geoscience interpretation expert with 20+ years of experience in seismic interpretation, well log analysis, and geological modeling. " +
      "You have published extensively and reviewed hundreds of interpretation reports. " +
      "Analyze the provided screen captures with extreme rigor and write a detailed, professional interpretation report.\n\n" +
      "# ACCURACY RULES (CRITICAL — READ FIRST)\n" +
      "1. ONLY describe features you can CLEARLY SEE in the image. If something is ambiguous, say '불명확' or 'ambiguous'.\n" +
      "2. Distinguish between OBSERVATION (what you see) and INTERPRETATION (what it means). Never mix them.\n" +
      "3. For every interpretation, provide the VISUAL EVIDENCE from the image that supports it.\n" +
      "   - WRONG: '단층이 존재한다' (no evidence)\n" +
      "   - RIGHT: '단면 중앙부(약 X 위치)에서 반사면의 불연속과 약 Yms의 수직 변위가 관찰되며, 이는 정단층으로 해석된다' (location + evidence + interpretation)\n" +
      "4. If you cannot determine something from the image alone, explicitly state the limitation.\n" +
      "5. Do NOT hallucinate features. If the image resolution is poor or the feature is unclear, say '해상도 한계' or 'resolution limit'.\n" +
      "6. Reference SPECIFIC locations in the image: read axis labels carefully. Use inline/crossline numbers, time(ms)/depth(m) values, or relative positions.\n" +
      "7. When describing spatial relationships, use directional terms tied to the image: left/right, shallow/deep, with approximate positions.\n" +
      "8. READ THE IMAGE CAREFULLY before writing. Spend time analyzing:\n" +
      "   - What are the axis labels? (time vs depth, inline vs crossline, distance)\n" +
      "   - What is the color scale? (amplitude, velocity, impedance)\n" +
      "   - What is the vertical/horizontal scale?\n" +
      "   - What text/annotations are already on the image?\n" +
      "9. Cross-check your interpretations: if you say 'fault', verify there is actual displacement. If you say 'unconformity', verify truncation/onlap.\n" +
      "10. Do NOT use generic descriptions. Be SPECIFIC with relative descriptions from the image.\n" +
      "11. Use RELATIVE descriptions when absolute values are unavailable:\n" +
      "   - Position: '단면 중앙부에서 약간 우측', '상부 1/3 지점'\n" +
      "   - Comparison: '좌측 림싱크라인이 우측보다 깊다', '돔 정상부에서 측면부로 갈수록 지층이 얇아진다'\n" +
      "   - Direction: '클리노폼이 좌→우 방향으로 전진', '단층면이 좌측으로 경사'\n" +
      "   These relative observations are VALUABLE evidence even without absolute measurements.\n\n" +
      "# FAULT IDENTIFICATION CHECKLIST (use when assessing faults)\n" +
      "Before claiming a fault exists, check these visual criteria:\n" +
      "- Is there vertical OFFSET (displacement) of reflectors across the suspected fault?\n" +
      "- Do reflectors TERMINATE against the suspected fault plane?\n" +
      "- Can you identify the FAULT PLANE dip direction? → normal vs reverse\n" +
      "- What is the spatial relationship with nearby structures (salt domes → radial faults, grabens → conjugate faults)?\n" +
      "- If none of these are clearly visible, state 'possible fault' with Low confidence, not 'fault exists'.\n\n" +
      "# KEY HORIZON DESCRIPTION (for stratigraphic division)\n" +
      "When dividing the section into upper/middle/lower units, describe the BOUNDARY reflectors:\n" +
      "- Amplitude: high/moderate/low (brightness in image)\n" +
      "- Continuity: continuous across section / intermittent / disrupted\n" +
      "- Shape: flat / gently dipping / curved / irregular\n" +
      "- Example: '중부와 하부를 구분하는 경계면은 고진폭·고연속성 반사면으로, 단면 전체에 걸쳐 추적 가능하다'\n\n" +
      "# DRAPING vs ONLAP DISTINCTION (critical for salt/structural interpretation)\n" +
      "- **Draping**: reflectors CONFORM to the structure shape, maintaining thickness → post-tectonic passive burial\n" +
      "- **Onlap**: reflectors ABUT against the structure sideways, thinning toward it → syn-tectonic sedimentation\n" +
      "- This distinction reveals TIMING: draping = structure formed first, onlap = structure growing during deposition\n" +
      "- Always specify which pattern you observe near structural features.\n\n" +
      "# COMMON MISINTERPRETATION WARNINGS\n" +
      "- **Do NOT confuse visually similar but geologically different features.** Check internal characteristics.\n" +
      "- **Artifacts ≠ Real features**: Distinguish real signals from processing effects.\n" +
      "- **Use standard terminology**: 림싱크라인(rim syncline), NOT 퀼싱크라인. Check spelling of all technical terms.\n" +
      "- **Alternative explanations**: For each major interpretation, consider at least one alternative.\n\n";

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
    "Step 0. IDENTIFY DATASET (MANDATORY — do this FIRST)\n" +
    "- Read the TOPIC text carefully. If it contains ANY recognizable name (e.g., 'F3', 'F3 Demo', 'Viking Graben', 'Poseidon', 'Penobscot'), that IS the dataset name. State it definitively: 'F3 Demo 3D Survey' — NOT 'possibly F3' or 'dataset not specified'.\n" +
    "- Read any visible text in the image (window title, axis labels, header). Extract the dataset/survey name.\n" +
    "- Determine 2D vs 3D: If the image shows a single inline or crossline section from a named survey or software like OpendTect, it is almost certainly a 3D volume. Only classify as 2D if you have explicit evidence it is a standalone 2D seismic line.\n" +
    "- For well-known datasets, include known metadata: F3 → Netherlands North Sea, 651 inlines, 951 crosslines, 4ms sampling, wells F02-1/F03-2/F03-4/F06-1. Viking Graben → Norwegian North Sea, Mobil AVO dataset. Penobscot → Nova Scotia, Canada.\n" +
    "- NEVER write 'Dataset name not specified' or 'presumably' if the topic contains a recognizable name.\n\n" +
    "Step 1. IDENTIFY GEOLOGICAL CONTEXT (CRITICAL — this determines ALL subsequent interpretations)\n" +
    "- From the dataset name and region, determine the TECTONIC SETTING first:\n" +
    "  - Is it EXTENSIONAL (rift, passive margin)? → expect normal faults, salt diapirs, half-grabens\n" +
    "  - Is it COMPRESSIONAL (fold-thrust belt, foreland)? → expect reverse faults, anticlines, thrust sheets\n" +
    "  - Is it STRIKE-SLIP? → expect flower structures, pull-apart basins\n" +
    "- Name specific geological formations, groups, and stratigraphic units:\n" +
    "  F3 → Netherlands North Sea, EXTENSIONAL + salt tectonics. Dominant features: Pliocene clinoforms (progradation), Zechstein salt, Chalk Group. Curved reflectors are usually clinoforms NOT anticlines. Do NOT interpret compressional folding.\n" +
    "  Viking Graben → Norwegian North Sea, EXTENSIONAL (Jurassic rift). Brent Group, Kimmeridge Clay, Draupne Formation.\n" +
    "  Penobscot → Nova Scotia, Canada, passive margin.\n" +
    "- ██ TECTONIC CONSISTENCY CHECK: Your structural interpretations MUST match the tectonic setting. ██\n" +
    "  - In extensional settings: do NOT interpret compressional folds, thrust faults, or nappe structures\n" +
    "  - Curved reflectors in extensional/deltaic settings are more likely clinoforms or differential compaction than anticlines\n" +
    "  - Salt-related structures (diapirs, pillows, walls) are common in North Sea — consider salt influence first\n" +
    "- Correct any apparent typos in geographical/geological terms.\n\n" +
    "Step 2. OBSERVE — DESCRIBE EXACTLY WHAT YOU SEE\n" +
    "- Examine the image thoroughly. Describe ALL visible features relevant to the data type:\n" +
    "  - Patterns, shapes, trends, anomalies, discontinuities, gradients\n" +
    "  - Spatial distribution: where features appear (position, depth/time/distance)\n" +
    "  - Intensity/amplitude/value variations across the image\n" +
    "- Read ALL visible text: axis labels, colorbars, scale bars, titles, legends, units\n" +
    "- Reference EXACT positions using visible coordinates or relative terms ('left third', 'center at ~Xm depth')\n" +
    "- Use ONLY neutral, descriptive language — NO interpretation terms yet\n\n" +
    "Step 3. INTERPRET — WITH EVIDENCE\n" +
    "- For EACH interpretation, cite the specific observation that supports it:\n" +
    "  - Pattern: 'Observation → therefore → Interpretation'\n" +
    "  - Example: '해당 위치에서 [구체적 관찰 내용] → [해석]으로 판단된다'\n" +
    "- ██ BEFORE writing any structural interpretation, re-check Step 1: is this term valid for this tectonic setting? ██\n" +
    "  - 'Anticline' in an extensional basin? → More likely clinoform, differential compaction, or drape over salt\n" +
    "  - 'Thrust fault' in a rift? → Very unlikely. Re-examine.\n" +
    "  - 'Growth fold' in extensional setting? → Consider growth fault + rollover instead\n" +
    "- Apply geological terminology ONLY after confirming compatibility with the tectonic setting.\n" +
    "- Name specific formations, units, or features when identifiable from context.\n" +
    "- Include geological history/sequence when relevant.\n" +
    "- For key interpretations, provide at least one ALTERNATIVE explanation:\n" +
    "  - Curved reflectors: anticline vs clinoform vs differential compaction vs velocity artifact?\n" +
    "  - Reflector discontinuity: fault vs channel edge vs processing artifact?\n" +
    "  - High amplitude: fluid effect vs lithology change vs tuning?\n" +
    "- If the image alone is ambiguous, state the uncertainty rather than forcing an interpretation.\n" +
    "- For each interpretation, consider alternative explanations (e.g., structural vs. processing artifact) and note them.\n" +
    crossSection +
    confidenceSection +
    reportFormatSection +
    rulesSection +
    "\n# ██ SELF-VERIFICATION (DO THIS BEFORE FINISHING) ██\n" +
    "Before outputting your report, verify:\n" +
    "1. TECTONIC CONSISTENCY: Do ALL structural interpretations match the tectonic setting (Step 1)? If not, FIX them.\n" +
    "2. EVIDENCE CHECK: Does each interpretation have specific visual evidence with location?\n" +
    "3. ARTIFACT CHECK: Did you confuse artifacts with real features?\n" +
    "4. CLINOFORM vs ANTICLINE: In extensional/deltaic settings, are curved reflectors interpreted as clinoforms (not anticlines)?\n" +
    "5. CONFIDENCE: Is every bullet tagged with [신뢰도: X] or [Confidence: X]? Most should be 중간/Medium.\n" +
    "If any check fails, correct it before outputting.\n\n" +
    structuresSection
  );
}
