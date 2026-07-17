import json
import logging
from typing import Any

from google import genai
from google.genai import types
from pydantic import ValidationError

from app.feature.post_analysis.schema import PostAnalysisPayload


logger = logging.getLogger(__name__)


class GeminiPostAnalyzer:
    MAX_VALIDATION_RETRIES = 2

    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def analyze(self, post_content: str) -> dict[str, Any]:
        print("log : Starting post analysis using GeminiPostAnalyzer")

        prompt = self._create_prompt(post_content)

        total_attempts = self.MAX_VALIDATION_RETRIES + 1
        for attempt in range(1, total_attempts + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=PostAnalysisPayload,
                        temperature=0,
                    ),
                )

                if response.parsed is not None:
                    return response.parsed.model_dump()
                return PostAnalysisPayload.model_validate_json(response.text).model_dump()
            except ValidationError as exc:
                if attempt < total_attempts:
                    retry_count = attempt
                    logger.warning(
                        "Gemini structured output validation failed "
                        "(attempt=%d/%d, retry=%d/%d, reason=%s). Retrying.",
                        attempt,
                        total_attempts,
                        retry_count,
                        self.MAX_VALIDATION_RETRIES,
                        exc,
                    )
                    continue

                retry_count = self.MAX_VALIDATION_RETRIES
                logger.error(
                    "Gemini structured output validation failed after all retries "
                    "(attempt=%d/%d, retry=%d/%d, reason=%s).",
                    attempt,
                    total_attempts,
                    retry_count,
                    self.MAX_VALIDATION_RETRIES,
                    exc,
                )
                raise

    def _create_prompt(self, post_content: str) -> str:

        schema_text = json.dumps(
            PostAnalysisPayload.model_json_schema(),
            ensure_ascii=False,
            indent=2
        )
        prompt = f"""
            You analyze the job posting content and extract key information.

            Return JSON that MUST match the provided schema exactly.

            Job Posting Content:
            {post_content}

            Schema:
            {schema_text}

            Rules:
            - Output MUST be valid JSON
            - Output must contain ONLY the keys defined in the schema
            - All string values must be written in Korean
            - Do not include markdown, explanations, or extra keys
            - Every array field MUST contain at least 1 item. NEVER return an empty array ([])
            - If explicit information is limited, infer a reasonable item from the job posting context
            - Every inferred item must still be grounded in the posting; never invent unsupported information

            Field rules:
            title
            - Job posting title: company name + role name (e.g. "OO회사 백엔드 개발자 채용")
            - Maximum 30 Korean characters
            - If longer, rewrite to fit the limit

            summary
            - Job title + experience requirement + company name
            - Maximum 20 Korean characters
            - If longer, rewrite to fit the limit

            company_intro
            - Company mission or domain inferred from the posting content
            - Maximum 30 Korean characters

            rnr
            - Extract responsibilities directly from the job posting
            - If responsibilities are not explicit, infer them only from the described role and work context
            - Must contain at least 1 item; never return []
            - Maximum 5 items
            - Each item should be a short phrase

            required_skills
            - Extract required or preferred skills
            - If skills are not explicit, infer them only when supported by the role and responsibilities
            - Must contain at least 1 item; never return []
            - Maximum 5 items

            differentiators
            - Preferred qualifications or hidden priorities inferred from the posting
            - Must contain at least 1 item; never return []
            - Maximum 3 items
            - Do not invent information not implied in the text

            hidden_keywords
            - Domain, job, or skill focused hashtags
            - Must contain at least 1 item; never return []
            - Maximum 5 items
            - Each item must start with "#"

            action_items
            - Immediate preparation steps before applying
            - Must contain at least 1 item; never return []
            - Maximum 3 items

        """

        return prompt
