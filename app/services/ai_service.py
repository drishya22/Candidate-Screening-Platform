import json

from google import genai
from google.genai import types

from app.core.config import settings


client = genai.Client(api_key=settings.gemini_api_key)


EVALUATION_SCHEMA = {
    "type": "object",
    "properties": {
        "skills_score": {
            "type": "number",
            "description": "Score from 0 to 100 for required technical skills."
        },
        "experience_score": {
            "type": "number",
            "description": "Score from 0 to 100 for relevant experience."
        },
        "project_score": {
            "type": "number",
            "description": "Score from 0 to 100 for relevance and quality of projects."
        },
        "education_score": {
            "type": "number",
            "description": "Score from 0 to 100 for educational background."
        },
        "strengths": {
            "type": "array",
            "maxItems": 5,
            "items": {"type": "string"}
        },
        "gaps": {
            "type": "array",
            "maxItems": 5,
            "items": {"type": "string"}
        },
        "evidence": {
            "type": "array",
            "minItems": 5,
            "maxItems": 8,
            "items": {
                "type": "object",
                "properties": {
                    "requirement": {"type": "string"},
                    "matched": {"type": "boolean"},
                    "evidence": {
                        "type": "string",
                        "description": "Maximum 20 words."
                    }
                },
                "required": [
                    "requirement",
                    "matched",
                    "evidence"
                ]
            }
        },
        "recommendation": {
            "type": "string",
            "enum": [
                "strong_shortlist",
                "shortlist",
                "borderline",
                "reject"
            ]
        }
    },
    "required": [
        "skills_score",
        "experience_score",
        "project_score",
        "education_score",
        "strengths",
        "gaps",
        "evidence",
        "recommendation"
    ]
}


def evaluate_candidate(job_description: str,resume_text: str) -> dict:

    prompt = f"""You are a technical recruiter. Score this candidate for the job below using ONLY evidence explicitly present in the resume.

JOB DESCRIPTION:
{job_description}

RESUME:
{resume_text}

Rules:
- A skill/requirement mentioned in the JD but not evidenced in the resume gets NO credit.
- Do not infer, assume, or invent skills, experience, projects, or education.
- Ignore name, email, contact details, and any other identity info.
- Base scores (0-100) on concrete, resume-stated evidence only — prefer projects/experience over keyword mentions.

Output constraints (keep responses concise to save tokens):
- "strengths": max 5 items, one short phrase each.
- "gaps": max 5 items, one short phrase each.
- "evidence": cover only the 5-8 most important requirements from the JD. Each "evidence" field must be ≤20 words.
- No extra commentary outside the schema fields.
"""

    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(          
            response_mime_type="application/json",
            response_schema=EVALUATION_SCHEMA,
        ),
    )

    return json.loads(response.text)