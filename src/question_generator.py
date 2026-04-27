import json
import os
from prompts import QUESTION_GENERATION_PROMPT

_client = None


def _resolve_provider() -> str:
    provider = os.environ.get('AI_PROVIDER', 'auto').strip().lower()
    if provider in {'openai', 'gemini', 'groq'}:
        return provider
    if os.environ.get('GROQ_API_KEY', '').strip():
        return 'groq'
    if os.environ.get('GEMINI_API_KEY', '').strip():
        return 'gemini'
    return 'openai'


def _resolve_model(provider: str) -> str:
    if provider == 'groq':
        return os.environ.get('GROQ_MODEL', 'llama-3.3-70b-versatile').strip() or 'llama-3.3-70b-versatile'
    if provider == 'gemini':
        return os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash').strip() or 'gemini-2.0-flash'
    return os.environ.get('OPENAI_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'


def _get_client():
    global _client
    if _client is None:
        from openai import OpenAI
        provider = _resolve_provider()
        if provider == 'groq':
            _client = OpenAI(
                api_key=os.environ.get('GROQ_API_KEY', '').strip(),
                base_url='https://api.groq.com/openai/v1'
            )
        elif provider == 'gemini':
            _client = OpenAI(
                api_key=os.environ.get('GEMINI_API_KEY', '').strip(),
                base_url='https://generativelanguage.googleapis.com/v1beta/openai/'
            )
        else:
            _client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', '').strip() or None)
    return _client


def generate_questions(resume: str, job_description: str) -> dict:
    if not resume.strip() or not job_description.strip():
        return {"error": "Resume and Job Description cannot be empty."}

    prompt = QUESTION_GENERATION_PROMPT.format(
        resume_text=resume,
        job_description=job_description
    )

    try:
        provider = _resolve_provider()
        model = _resolve_model(provider)
        response = _get_client().chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )

        raw_output     = json.loads(response.choices[0].message.content)
        questions_list = raw_output.get("questions", [])

        if not isinstance(questions_list, list):
            raise ValueError("Invalid JSON structure: 'questions' must be a list.")

        formatted_questions = {"technical": [], "behavioral": []}

        for item in questions_list:
            if not isinstance(item, dict):
                continue
            mapped_item = {
                "question":   item.get("question", ""),
                "skill":      item.get("skill", ""),
                "difficulty": item.get("difficulty", "medium"),
            }
            if item.get("type") == "technical":
                formatted_questions["technical"].append(mapped_item)
            elif item.get("type") == "behavioral":
                formatted_questions["behavioral"].append(mapped_item)

        # Soft floor — tolerate minor model variance (e.g. 4+3 instead of 5+2)
        if len(formatted_questions["technical"]) < 3:
            return {"error": "Could not generate enough technical questions. Please try again."}
        if len(formatted_questions["behavioral"]) < 1:
            return {"error": "Could not generate behavioral questions. Please try again."}

        # Trim to expected counts
        formatted_questions["technical"]  = formatted_questions["technical"][:5]
        formatted_questions["behavioral"] = formatted_questions["behavioral"][:2]

        return formatted_questions

    except json.JSONDecodeError:
        return {"error": "Failed to parse API response as JSON."}
    except Exception as e:
        return {"error": f"Failed to generate questions: {str(e)}"}
