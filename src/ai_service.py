"""
AI service layer — single entry point for all AI operations.

Demo mode is automatically enabled when:
    1. DEMO_MODE=true is set explicitly, OR
    2. neither OPENAI_API_KEY, GEMINI_API_KEY, nor GROQ_API_KEY is set

When demo mode is active, all functions return realistic mock data so
the app is fully explorable without an API key.
"""

import os


def _resolve_demo_mode() -> bool:
    if os.environ.get('DEMO_MODE', '').strip().lower() == 'true':
        return True
    has_openai = bool(os.environ.get('OPENAI_API_KEY', '').strip())
    has_gemini = bool(os.environ.get('GEMINI_API_KEY', '').strip())
    has_groq = bool(os.environ.get('GROQ_API_KEY', '').strip())
    return not (has_openai or has_gemini or has_groq)


DEMO_MODE: bool = _resolve_demo_mode()


def _is_quota_or_rate_limited(error_message: str) -> bool:
    msg = (error_message or '').lower()
    signals = [
        '429',
        'quota',
        'resource exhausted',
        'rate limit',
        'too many requests',
        'insufficient_quota',
    ]
    return any(signal in msg for signal in signals)


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def generate_questions(resume: str, job_description: str) -> dict:
    """Return {'technical': [...], 'behavioral': [...]} or {'error': '...'}."""
    if not resume.strip() or not job_description.strip():
        return {"error": "Resume and Job Description cannot be empty."}

    if DEMO_MODE:
        from demo_data import get_demo_questions
        return get_demo_questions()

    result = _live_generate_questions(resume, job_description)
    if isinstance(result, dict) and _is_quota_or_rate_limited(result.get('error', '')):
        from demo_data import get_demo_questions
        return get_demo_questions()
    return result


def evaluate_answer(question: str, answer: str) -> dict:
    """Return scored evaluation dict or {'error': '...'}."""
    if not question.strip() or not answer.strip():
        return {"error": "Question and Answer cannot be empty."}

    if DEMO_MODE:
        from demo_data import get_demo_evaluation
        return get_demo_evaluation()

    result = _live_evaluate_answer(question, answer)
    if isinstance(result, dict) and _is_quota_or_rate_limited(result.get('error', '')):
        from demo_data import get_demo_evaluation
        return get_demo_evaluation()
    return result


def transcribe_audio(audio_path: str) -> dict:
    """Transcribe an audio file. Returns {'text': '...'} or {'error': '...'}."""
    if DEMO_MODE:
        from demo_data import DEMO_TRANSCRIPTION
        return {"text": DEMO_TRANSCRIPTION}

    try:
        from openai import OpenAI
        client = OpenAI()
        with open(audio_path, 'rb') as f:
            text = client.audio.transcriptions.create(
                model='whisper-1', file=f, response_format='text'
            )
        return {"text": text}
    except Exception:
        return {"error": "Audio transcription failed. Please type your answer instead."}


# ── LIVE IMPLEMENTATIONS ──────────────────────────────────────────────────────

def _live_generate_questions(resume: str, job_description: str) -> dict:
    from question_generator import generate_questions as _gen
    return _gen(resume, job_description)


def _live_evaluate_answer(question: str, answer: str) -> dict:
    from evaluator import evaluate_answer as _eval
    return _eval(question, answer)
