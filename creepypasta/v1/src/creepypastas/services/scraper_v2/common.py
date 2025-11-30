import praw
import praw.models

import pydantic
import typing

from creepypastas.metadata import Metadata


class Scraper(typing.Protocol):
    def scrape_story(self, thread: praw.models.Submission) -> Metadata: ...


class TriageResponse(pydantic.BaseModel):
    approved: bool
    reasoning: str


triage_prompt = """
You are an expert horror editor specializing in creepypasta storytelling. 
Your task is to evaluate whether the following unedited raw Reddit post 
has strong potential to be adapted into an engaging, scary, and 
fear-inducing creepypasta video for YouTube.

### Evaluation Criteria
- **Engagement**: The text should be capable of capturing and holding attention.
- **Horror Quality**: The text should contain elements of fear, dread, suspense, or unease.
- **Creepypasta Fit**: The story should align with typical creepypasta themes 
  (e.g., urban legends, supernatural events, psychological horror).
- **Potential**: Even if unpolished, the text should demonstrate 
  potential to be refined into an effective horror story.

### Instructions
- Be concise and objective in your evaluation.
- Do **not** rewrite or improve the story. Only judge its potential.
- Always return a valid JSON object in the exact schema below.

### Schema
{{
  "approved": true | false,
  "reasoning": "A short explanation of why it was approved or rejected."
}}

### Story to Evaluate
{story}
"""
