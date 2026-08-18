"""Probabilistic QA gate — LLM-as-judge evaluation of the worksheet HTML.

Uses response_format=json_object and validates the verdict through a Pydantic
model before any action is taken (per global JSON/Pydantic enforcement rules).
"""

import os
import sys
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field

EVALUATION_PROMPT = """You are a Cambridge PET materials reviewer. Assess the worksheet HTML for:

1. Content quality: Are instructions clear and unambiguous? Is the exercise logic sound?
2. CEFR appropriateness: Does vocabulary, grammar, and task complexity match {target_level}?
3. Educational soundness: Is the task design effective for the stated learning goal?
4. Visual layout: Are margins, spacing, font sizes, and alignment appropriate for A4 classroom use?
5. Error types targeted: Are the errors pedagogically relevant for {learner_profile}?

Rate each dimension 1-5 and provide a pass/fail verdict (pass requires all dimensions >= 3).
If fail, list specific repair actions with file paths.

Respond with EXACTLY this JSON shape (no other fields):
{{"content_quality": 1-5, "cefr_appropriateness": 1-5, "educational_soundness": 1-5, "visual_layout": 1-5, "error_targeting": 1-5, "pass_fail": "pass" or "fail", "repair_actions": ["..."]}}

WORKSHEET HTML:
{html}"""


class WorksheetEvaluation(BaseModel):
    content_quality: int = Field(ge=1, le=5)
    cefr_appropriateness: int = Field(ge=1, le=5)
    educational_soundness: int = Field(ge=1, le=5)
    visual_layout: int = Field(ge=1, le=5)
    error_targeting: int = Field(ge=1, le=5)
    pass_fail: str
    repair_actions: list[str] = Field(default_factory=list)


def call_judge(client: OpenAI, html: str) -> dict:
    response = client.chat.completions.create(
        model="deepseek/deepseek-v4-flash",
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a Cambridge PET materials reviewer. Always respond with valid JSON."},
            {"role": "user", "content": EVALUATION_PROMPT.format(
                target_level="B1",
                learner_profile="Thai middle school students (L1 Thai: unreleased final stops; dropped or underarticulated final /t/, /d/, and -ed endings)",
                html=html[:18000],
            )},
        ],
    )
    import json

    data = json.loads(response.choices[0].message.content)
    normalized = {}
    for key, value in data.items():
        clean = key.lstrip("._")
        normalized["pass_fail" if clean == "verdict" else clean] = value
    return normalized


def main() -> None:
    html = Path("PROJECTS/PRONUNCIATION NOTICING/worksheet.html").read_text(encoding="utf-8")
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    validated = None
    for attempt in range(3):
        try:
            validated = WorksheetEvaluation.model_validate(call_judge(client, html))
            break
        except Exception as exc:
            print(f"Judge validation failed (attempt {attempt + 1}): {exc}", file=sys.stderr)
    if validated is None:
        sys.exit(1)
    print(validated.model_dump_json(indent=2))
    sys.exit(0 if validated.pass_fail == "pass" else 1)


if __name__ == "__main__":
    main()
