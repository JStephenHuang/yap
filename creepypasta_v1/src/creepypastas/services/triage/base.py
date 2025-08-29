MIN_WORDS: int = 500
MAX_WORDS: int = 1500

TRIAGE_LLM_MODEL: str = "llama3.1:8b"
TRIAGE_LLM_PROMPT: str = """
You are an expert evaluator of creepypasta stories and experiences. Your task is to determine if the following raw text strictly adheres to the creepypasta theme, meaning it presents a genuinely scary story or a frightening personal experience.

Consider the following criteria:
- **Scary Theme:** The core of the text should revolve around creating fear, suspense, unease, or horror.
- **Narrative or Experiential:** It should be presented as either a fictional story or a recounting of a personal (though potentially fictionalized) scary experience.
- **Exclusion of Other Themes:** The text should *not* primarily focus on other genres or topics such as:
    - General fiction without a significant horror element.
    - Non-fiction accounts that are not inherently scary.
    - Discussions, analyses, or explanations of creepypasta or horror in general (meta-commentary).
    - Requests for information or help.
    - Advertisements or promotional material.
    - Content that is primarily humorous, satirical, or romantic.
    - Content that is excessively graphic or disturbing without a clear scary narrative purpose.

Evaluate the following title and raw text:
---
{title}
{text}
---

Based solely on the criteria above, determine if this text qualifies as a creepypasta (scary story or experience) and explain why the story eithers qualifies or does not.

Respond with a JSON object in the following format:
{{
    "approved": true/false,
    "reasoning": "explanation of why it was approved or rejected",
}}
"""
TRIAGE_LLM_TEMPERATURE: float = 0.0  # Make responses deterministic
