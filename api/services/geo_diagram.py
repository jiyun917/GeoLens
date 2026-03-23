"""
GeoBanana: Geological schematic diagram generator.
Uses PaperBanana's VLM → matplotlib code → subprocess execution pattern.
Includes reference image matching and STRUCTURES_JSON output for image labels.
"""

import asyncio
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from google import genai

# ── Paths ──
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_REF_DIR = _PROJECT_ROOT / "data" / "reference_sets"
_REF_INDEX = _REF_DIR / "index.json"

# ── Geological matplotlib prompt ──

GEO_PROMPT = """\
Generate ONLY a ```python code block. No text before or after.
The code creates a geological schematic diagram using matplotlib.

Rules:
- OUTPUT_PATH is pre-defined. End with: plt.savefig(OUTPUT_PATH, dpi=200, bbox_inches='tight', facecolor='white'); plt.close()
- Use ONLY matplotlib and numpy. NO font_manager. NO system font search.
- plt.rcParams['font.family'] = 'Malgun Gothic'; plt.rcParams['axes.unicode_minus'] = False
- fig, ax = plt.subplots(figsize=(10, 6))
- Conceptual textbook-style diagram. Labels in LANG.
- Layers as fill_between with SMOOTH sine-curved boundaries.
- Blue gradient top to bottom: #DBEAFE, #93C5FD, #60A5FA, #3B82F6. Basement: #9CA3AF.
- Faults: red (#DC2626), linewidth=2.5. Unconformity: dashed orange (#D97706).
- Growth strata: #FCD34D wedge shape. Salt/intrusion: mint (#5DCAA5).
- Add legend, title, depth labels.

After the code block, output structure information:

STRUCTURES_JSON:
[{"type": "structure_type", "label": "Korean label", "position": "grid-position"}]

Valid types: salt_diapir, normal_fault, reverse_fault, unconformity, anticline, syncline, growth_strata, post_kinematic, pre_kinematic, basement, horizon, amplitude_anomaly, channel, delta, reef
Valid positions: top-left, top-center, top-right, mid-left, mid-center, mid-right, bottom-left, bottom-center, bottom-right
Max 8 structures. Skip post_kinematic and basement.
"""

_SEISMIC_HINT = "\nSeismic cross-section: X=distance, Y=depth. Smooth curved layers, faults, salt domes. Max 8 elements."
_WELLLOG_HINT = "\nWell log: 3-panel (GR left, wellbore center, Resistivity right). plt.subplots(1,3, figsize=(8,10)). Y=Depth inverted."
_GRAVITY_HINT = "\nGravity/Magnetic: 2-row (anomaly profile top, subsurface model bottom). plt.subplots(2,1, figsize=(10,6))."
_GPR_HINT = "\nGPR: X=distance(m), Y=depth(m, 0-5m). Brown/tan soil layers, gray bedrock, red circles for buried objects."
_RESISTIVITY_HINT = "\nResistivity: X=distance, Y=depth(inverted). Color-coded zones, dashed boundaries."

_HINTS = {
    "seismic": _SEISMIC_HINT,
    "well_log": _WELLLOG_HINT,
    "gravity": _GRAVITY_HINT,
    "magnetic": _GRAVITY_HINT,
    "resistivity": _RESISTIVITY_HINT,
    "gpr": _GPR_HINT,
}


def _load_reference_images(report_text: str) -> list[dict]:
    """Load matching reference images based on report content."""
    if not _REF_INDEX.exists():
        return []
    try:
        index = json.loads(_REF_INDEX.read_text(encoding="utf-8"))
        examples = index.get("examples", [])
    except Exception:
        return []

    # Simple keyword matching to select relevant references
    text_lower = report_text.lower()
    scored = []
    for ex in examples:
        score = 0
        for hint in ex.get("structure_hints", []):
            if hint.replace("_", " ") in text_lower or hint in text_lower:
                score += 2
        ctx = ex.get("source_context", "").lower()
        for word in ctx.split():
            if len(word) > 4 and word in text_lower:
                score += 1
        img_path = _REF_DIR / ex.get("image_path", "")
        if img_path.exists():
            scored.append((score, ex, img_path))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:2]  # Top 2 references


def _build_prompt(report_text: str, data_type: str, language: str) -> str:
    lang = "Korean" if language == "ko" else "English"
    hint = _HINTS.get(data_type, _SEISMIC_HINT)
    return (
        GEO_PROMPT.replace("LANG", lang)
        + "\nData type: " + data_type + hint
        + "\n\nReport:\n" + report_text[:3500]
    )


def _extract_code(response: str) -> str:
    if "```python" in response:
        start = response.index("```python") + len("```python")
        end = response.find("```", start)
        return (response[start:end] if end != -1 else response[start:]).strip()
    if "```" in response:
        start = response.index("```") + 3
        nl = response.find("\n", start)
        if nl != -1 and nl - start < 20:
            start = nl + 1
        end = response.find("```", start)
        return (response[start:end] if end != -1 else response[start:]).strip()
    return response.strip()


def _extract_structures(response: str) -> list[dict]:
    """Parse STRUCTURES_JSON from VLM response."""
    VALID_TYPES = {
        "salt_diapir", "normal_fault", "reverse_fault", "strike_slip_fault",
        "unconformity", "anticline", "syncline", "growth_strata",
        "post_kinematic", "pre_kinematic", "basement", "horizon",
        "amplitude_anomaly", "channel", "delta", "reef",
    }
    VALID_POSITIONS = {
        "top-left", "top-center", "top-right",
        "mid-left", "mid-center", "mid-right",
        "bottom-left", "bottom-center", "bottom-right",
    }
    match = re.search(r'STRUCTURES_JSON:\s*\n?\s*(\[[\s\S]*?\])', response)
    if not match:
        return []
    try:
        raw = json.loads(match.group(1))
        return [
            s for s in raw
            if s.get("type") in VALID_TYPES
            and s.get("position") in VALID_POSITIONS
            and s.get("label")
            and s["type"] not in ("post_kinematic", "basement")
        ][:8]
    except (json.JSONDecodeError, TypeError):
        return []


def _execute_code(code: str, output_path: str) -> bool:
    code = re.sub(r'^OUTPUT_PATH\s*=\s*["\'].*["\']\s*$', "", code, flags=re.MULTILINE)
    full_code = f'OUTPUT_PATH = r"{output_path}"\n{code}'

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    try:
        compile(full_code, "<diagram>", "exec")
    except SyntaxError:
        lines = [l for l in full_code.split("\n")
                 if not any(k in l for k in ["FontProperties", "font_manager", "findSystemFonts"])]
        full_code = "\n".join(lines)
        try:
            compile(full_code, "<diagram>", "exec")
        except SyntaxError:
            return False

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(full_code)
        temp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, temp_path],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"[GeoBanana] Exec error: {result.stderr[:300]}")
            return False
        return Path(output_path).exists()
    except subprocess.TimeoutExpired:
        return False
    finally:
        Path(temp_path).unlink(missing_ok=True)


async def generate_geo_diagram(
    report_text: str,
    data_type: str = "seismic",
    language: str = "ko",
    capture_image: str | None = None,
) -> dict | None:
    """
    Generate geological schematic diagram.
    Returns {"image": base64_png, "structures": [...]} or None.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    client = genai.Client(api_key=api_key)
    prompt_text = _build_prompt(report_text, data_type, language)

    # Build multimodal content
    contents = []

    # Add reference images (best matching)
    refs = _load_reference_images(report_text)
    for _, ex, img_path in refs:
        try:
            img_bytes = img_path.read_bytes()
            mime = "image/png" if img_path.suffix == ".png" else "image/jpeg"
            contents.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(img_bytes).decode()}})
            contents.append(f"Reference diagram: {ex.get('caption', '')}. Match this visual STYLE but create content based on the report below.")
        except Exception:
            pass

    # Add capture image if provided
    if capture_image:
        img_data = capture_image
        mime = "image/jpeg"
        if img_data.startswith("data:"):
            header, img_data = img_data.split(",", 1)
            if "png" in header:
                mime = "image/png"
        contents.append({"inline_data": {"mime_type": mime, "data": img_data}})
        contents.append("Above is the actual data image. Match the structural layout.\n\n")

    contents.append(prompt_text)

    # Try multiple models
    models = ["gemini-2.5-flash-lite", "gemini-2.0-flash-lite", "gemini-2.5-flash"]
    full_response = None

    for model in models:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(
                    model=model, contents=contents,
                    config={"temperature": 0.3, "max_output_tokens": 16384},
                )
                full_response = resp.text
                print(f"[GeoBanana] OK: {model}")
                break
            except Exception as e:
                print(f"[GeoBanana] {model} attempt {attempt+1}: {e}")
                if attempt == 0:
                    await asyncio.sleep(2)
        if full_response:
            break

    if not full_response:
        return None

    code = _extract_code(full_response)
    structures = _extract_structures(full_response)
    if not code:
        return None

    print(f"[GeoBanana] {len(code)} chars code, {len(structures)} structures")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        out = tmp.name

    try:
        if _execute_code(code, out):
            with open(out, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            return {"image": img_b64, "structures": structures}
        return None
    finally:
        Path(out).unlink(missing_ok=True)
