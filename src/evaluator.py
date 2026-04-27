import json
import os
from prompts import ANSWER_EVALUATION_PROMPT

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


def evaluate_answer(question: str, answer: str) -> dict:
    if not question.strip() or not answer.strip():
        return {"error": "Question and Answer cannot be empty."}

    prompt = ANSWER_EVALUATION_PROMPT.format(question=question, answer=answer)

    try:
        provider = _resolve_provider()
        model = _resolve_model(provider)
        response = _get_client().chat.completions.create(
            model=model,
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}]
        )

        parsed_json = json.loads(response.choices[0].message.content)

        if not isinstance(parsed_json, dict):
            raise ValueError("Invalid JSON structure: Output must be an object.")

        evaluation = {
            "score":    parsed_json.get("score", "N/A"),
            "feedback": parsed_json.get("feedback", "No feedback provided."),
            "strengths": (parsed_json.get("strengths")
                          if isinstance(parsed_json.get("strengths"), list) else []),
            "gaps": (parsed_json.get("gaps")
                     if isinstance(parsed_json.get("gaps"), list) else []),
            "improvement_suggestions": (
                parsed_json.get("improvement_suggestions")
                if isinstance(parsed_json.get("improvement_suggestions"), list) else []
            ),
        }
        return evaluation

    except json.JSONDecodeError:
        return {"error": "Failed to parse API response as JSON."}
    except Exception as e:
        return {"error": f"Failed to evaluate answer: {str(e)}"}
