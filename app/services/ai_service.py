import json
import logging

import httpx
from google import genai
from google.genai import types

from app.core.config import settings

logger = logging.getLogger(__name__)

client = genai.Client(api_key=settings.gemini_api_key)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


# Gemini uses Google's own structured-output schema format.
# Keep this schema Gemini-compatible.
GEMINI_EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "skills_score": {
            "type": "number",
            "description": "Score from 0 to 100 for required technical skills.",
        },
        "experience_score": {
            "type": "number",
            "description": "Score from 0 to 100 for relevant experience.",
        },
        "project_score": {
            "type": "number",
            "description": "Score from 0 to 100 for relevance and quality of projects.",
        },
        "education_score": {
            "type": "number",
            "description": "Score from 0 to 100 for educational background.",
        },
        "strengths": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "string",
            },
        },
        "gaps": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "string",
            },
        },
        "evidence": {
            "type": "array",
            "minItems": 5,
            "maxItems": 8,
            "items": {
                "type": "object",
                "properties": {
                    "requirement": {
                        "type": "string",
                    },
                    "matched": {
                        "type": "boolean",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Maximum 20 words.",
                    },
                },
                "required": [
                    "requirement",
                    "matched",
                    "evidence",
                ],
            },
        },
        "recommendation": {
            "type": "string",
            "enum": [
                "strong_shortlist",
                "shortlist",
                "borderline",
                "reject",
            ],
        },
    },
    "required": [
        "skills_score",
        "experience_score",
        "project_score",
        "education_score",
        "strengths",
        "gaps",
        "evidence",
        "recommendation",
    ],
}


# OpenRouter uses standard JSON Schema for strict structured output.
# Keep additionalProperties=False here so the schema remains strict.
OPENROUTER_EVALUATION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "skills_score": {
            "type": "number",
            "description": "Score from 0 to 100 for required technical skills.",
        },
        "experience_score": {
            "type": "number",
            "description": "Score from 0 to 100 for relevant experience.",
        },
        "project_score": {
            "type": "number",
            "description": "Score from 0 to 100 for relevance and quality of projects.",
        },
        "education_score": {
            "type": "number",
            "description": "Score from 0 to 100 for educational background.",
        },
        "strengths": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "string",
            },
        },
        "gaps": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "string",
            },
        },
        "evidence": {
            "type": "array",
            "minItems": 5,
            "maxItems": 8,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "requirement": {
                        "type": "string",
                    },
                    "matched": {
                        "type": "boolean",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "Maximum 20 words.",
                    },
                },
                "required": [
                    "requirement",
                    "matched",
                    "evidence",
                ],
            },
        },
        "recommendation": {
            "type": "string",
            "enum": [
                "strong_shortlist",
                "shortlist",
                "borderline",
                "reject",
            ],
        },
    },
    "required": [
        "skills_score",
        "experience_score",
        "project_score",
        "education_score",
        "strengths",
        "gaps",
        "evidence",
        "recommendation",
    ],
}


def _build_prompt(job_description: str, resume_text: str) -> str:
    return f"""Role: technical recruiter scoring a candidate against a job, using ONLY the resume as evidence.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Scoring rules:
- No resume evidence for a JD requirement = no credit. Do not infer, assume, or invent skills, experience, projects, or education.
- Ignore name, email, contact info, and other identity details.
- Prefer concrete project/experience evidence over keyword mentions.
- "evidence" entries: cover only the most important JD requirements, most critical first.
- Keep evidence concise and grounded in specific resume evidence.

Follow the response schema exactly. No text outside the JSON."""


def _evaluate_with_gemini(prompt: str) -> dict:
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GEMINI_EVALUATION_SCHEMA,
        ),
    )

    return json.loads(response.text)


def _evaluate_with_openrouter(prompt: str) -> dict:
    if not settings.openrouter_api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not configured.")

    payload = {
        "model": settings.openrouter_model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "candidate_evaluation",
                "strict": True,
                "schema": OPENROUTER_EVALUATION_SCHEMA,
            },
        },
        "provider": {
            "require_parameters": True,
        },
    }

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "Content-Type": "application/json",
    }

    response = httpx.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60.0,
    )

    response.raise_for_status()

    data = response.json()
    content = data["choices"][0]["message"]["content"]

    return json.loads(content)


def evaluate_candidate(job_description: str, resume_text: str) -> dict:
    prompt = _build_prompt(job_description, resume_text)

    gemini_error = None

    # Primary provider: Gemini
    try:
        result = _evaluate_with_gemini(prompt)

        logger.info("AI evaluation completed using Gemini.")

        return result

    except Exception as exc:
        gemini_error = exc

        logger.warning(
            "Gemini evaluation failed. Falling back to OpenRouter: %s",
            exc,
        )

    # Fallback provider: OpenRouter
    try:
        result = _evaluate_with_openrouter(prompt)

        logger.info("AI evaluation completed using OpenRouter fallback.")

        return result

    except Exception as openrouter_error:
        logger.error(
            "Both Gemini and OpenRouter evaluation failed. "
            "Gemini error: %s | OpenRouter error: %s",
            gemini_error,
            openrouter_error,
        )

        raise RuntimeError(
            "AI evaluation failed with both primary and fallback providers."
        ) from openrouter_error