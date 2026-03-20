export function buildCheckPrompt(instruction: string): string {
  return `You are a task completion judge. Compare two screenshots to determine if an action was performed.

Action to verify:
${instruction}

Process:
1. Look at the "before" screenshot (first image) — the state before the action.
2. Look at the "after" screenshot (second image) — the current state.
3. Determine if the action was performed based on visible changes.

Rules:
- Return "Yes" if the screen changed in a way consistent with the action being performed (e.g., a menu opened, a dialog appeared, a button state changed, content updated, a new view loaded).
- Return "Yes" even if the result is slightly different from expected, as long as the user clearly attempted and executed the action.
- Return "No" only if the screen is essentially unchanged, or the change is unrelated to the action (e.g., just a hover effect or cursor movement).

Format: very concise reasoning (under 10 words), then "Yes" or "No" on the last line.`;
}
