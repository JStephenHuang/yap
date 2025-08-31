import ollama
import praw.models

from creepypastas.metadata import Metadata
from .common import Scraper, triage_prompt, TriageResponse


class Llama3_1_8b(Scraper):
    def __init__(self):
        self.ollama = ollama.Client()

    def scrape_story(self, thread: praw.models.Submission) -> Metadata | None:
        original_story = thread.selftext
        response = self.ollama.chat.completions.create(
            model="llama3.1:8b",
            messages=[
                {"role": "user", "content": triage_prompt.format(story=original_story)}
            ],
            format="json",
        )

        validated_response = TriageResponse.model_validate_json(response)
        approved = validated_response.approved

        if not approved:
            return None

        return Metadata(
            url=f"https://www.reddit.com{thread.permalink}",
            title=thread.title,
            author=str(thread.author),
            state=Metadata.State.TRIAGED,
        )


#   model=self.settings.TRIAGE_LLM_MODEL,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": self.settings.TRIAGE_LLM_PROMPT.format(
#                         text=raw_text,
#                         title=title,
#                     ),
#                 }
#             ],
#             format="json",
