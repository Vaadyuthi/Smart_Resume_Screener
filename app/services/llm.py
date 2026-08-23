import json
import os

import httpx

from ..schemas import LLMResult


SYSTEM_PROMPT = """
You are an expert technical recruiter and resume evaluation assistant.

Your task is to compare a candidate resume with a job description.

IMPORTANT RULES:

1. Use ONLY information explicitly present in the resume.
2. Never invent skills, employers, degrees, projects or years of experience.
3. Evaluate technical skills, relevant experience, education and responsibilities.
4. Give an overall candidate fit score from 1 to 10.
5. Explain the reasoning clearly.
6. Identify both strengths and gaps.
7. Keep the recommendation professional.
8. Return ONLY valid JSON.

Required JSON format:

{
    "score": 8.5,
    "strengths": [
        "Python experience",
        "FastAPI experience"
    ],
    "gaps": [
        "Limited cloud experience"
    ],
    "recommendation": "Strong Match",
    "justification": "The candidate demonstrates strong alignment..."
}

Recommendation must be one of:

Strong Match
Match
Partial Match
Low Match
"""


async def llm_match(
    resume_text: str,
    job_description: str
):

    api_key = os.getenv(
        "LLM_API_KEY"
    )

    base_url = os.getenv(
        "LLM_BASE_URL",
        "https://api.groq.com/openai/v1"
    ).rstrip("/")


    model = os.getenv(
        "LLM_MODEL",
        "llama-3.1-8b-instant"
    )


    # No API key = fallback engine

    if not api_key:

        return None


    payload = {

        "model": model,

        "temperature": 0.1,

        "messages": [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content":
                f"""
JOB DESCRIPTION:

{job_description}


CANDIDATE RESUME:

{resume_text[:12000]}
"""
            }

        ],

        "response_format": {
            "type": "json_object"
        }

    }


    try:

        async with httpx.AsyncClient(
            timeout=45
        ) as client:

            response = await client.post(

                f"{base_url}/chat/completions",

                headers={
                    "Authorization":
                    f"Bearer {api_key}"
                },

                json=payload

            )


            response.raise_for_status()


            data = response.json()


            content = (
                data["choices"][0]
                ["message"]
                ["content"]
            )


            parsed = json.loads(
                content
            )


            return LLMResult.model_validate(
                parsed
            )


    except Exception:

        return None