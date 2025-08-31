SANITIZER_LLM_MODEL: str = "llama3.1:8b"
SANITIZER_LLM_TEMPERATURE: float = 0.3

# Sanitizer Prompt
SANITIZER_PROMPT: str = """You are an editor preparing a creepypasta for audio narration. Your task is to polish the provided story to ensure it flows perfectly when read aloud, while preserving its original horror.
Story:
---
{story}
---

Editing Guidelines:
1.  **Preserve the Core:** Maintain the original tone, writing style, and plot. Do not add or remove story elements.
2.  **Enhance Flow:** Correct grammar, punctuation, and awkward phrasing to ensure a smooth, natural narration.
3.  **Clean Content:** Replace vulgarity with thematically creepy alternatives and remove all meta-commentary (e.g., author's notes, Reddit references).
4.  **Format for TTS:** The final text must be clean of any formatting artifacts that would disrupt a Text-to-Speech engine. Specifically, ensure there are no single punctuation marks (like periods, hyphens, or asterisks) left on their own lines.

Respond ONLY with a JSON object in the following format, with no other text before or after it:
{
"sanitized_text": "The fully edited and cleaned story text goes here."
}
"""
