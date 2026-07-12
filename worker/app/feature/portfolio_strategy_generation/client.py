from google import genai
from google.genai import types
from app.feature.portfolio_strategy_generation.schema import (
    GeneratedPortfolioStrategyPayload,
    ExperienceInput,
    PostAnalysisInput,
)

class GeminiPortfolioStrategyGenerator:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        experiences: list[ExperienceInput],
        position_type: str,
        industry_type: str,
        post_analysis: PostAnalysisInput
    ) -> GeneratedPortfolioStrategyPayload:
        print("log : Starting portfolio strategy generation using PortfolioStrategyGenerator")

        prompt = self._create_prompt(experiences, position_type, industry_type, post_analysis)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeneratedPortfolioStrategyPayload,
                temperature=0,
            ),
        )

        if response.parsed is not None:
            return response.parsed.model_dump()

        return GeneratedPortfolioStrategyPayload.model_validate_json(response.text).model_dump()

    def _create_prompt(
        self,
        experiences: list[ExperienceInput],
        position_type: str | None,
        industry_type: str | None,
        post_analysis: PostAnalysisInput
    ) -> str:
        # 직무/산업 미지정(None)이면 프롬프트에 "None" 문자열이 새지 않도록 대체 문구를 사용한다.
        position_label = position_type or "미지정"
        industry_label = industry_type or "미지정"

        experience_str = "\n\n".join(
            [
                (
                    f"Title: {exp.title} [{exp.experienceType}] "
                    f"({exp.startDate} - {exp.endDate})\n"
                    f"- ImpactTier: {exp.impactTier}\n"
                    f"- TeamSize: {exp.teamSize}\n"
                    f"- Role: {exp.roleType}\n"
                    f"- Experience Content:\n{exp.experienceContent}"
                )
                for exp in experiences
            ]
        )

        prompt = f"""
            You generate portfolio strategy data tailored to a specific job posting.

            You are given:
            1. The analysis of the target job posting (what the company wants).
            2. The user's experience data.

            Build a portfolio strategy that maximizes the fit between the user's
            experiences and the target job posting. Every recommendation (positioning,
            ordering, keywords, strengths, improvement guides) must be grounded in BOTH
            the job posting analysis and the user's experiences.

            Return JSON that MUST match the provided schema exactly.

            Rules:
            - Output must contain only one top-level key: "portfolioStrategy"
            - All string values must be written in Korean
            - Do not include markdown, code fences, or explanations
            - experienceType must be one of: PROJECT, CAREER, EDUCATION, COMPETITION, OTHER
            - experienceOrdering means the priority order in which the user's experiences should appear in the portfolio, prioritizing experiences most relevant to the target job posting
            - experienceOrdering.order must start from 1 and increase sequentially without gaps
            - experienceStrategyPoints must reference only experiences that exist in the input data
            - experienceOrdering.title must exactly match an input experience title
            - mainPositioningMessage must position the user against the job posting analysis
            - keywords, strengths, and kpiCheckList should be concise and practical
            - improvementGuides should contain actionable advice to close gaps against the job posting

            Target:
            - positionType: {position_label}
            - industryType: {industry_label}

            Job Posting Analysis:
            - Title: {post_analysis.title}
            - Summary: {post_analysis.summary}

            Experience Data:
            {experience_str}
        """
        return prompt
