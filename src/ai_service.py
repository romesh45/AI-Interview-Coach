"""
AI service layer — single entry point for all AI operations.

Demo mode is automatically enabled when:
    1. DEMO_MODE=true is set explicitly, OR
    2. neither OPENAI_API_KEY nor GEMINI_API_KEY is set

When demo mode is active, all functions return realistic mock data so
the app is fully explorable without an API key.
"""

import os


def _resolve_demo_mode() -> bool:
    if os.environ.get('DEMO_MODE', '').strip().lower() == 'true':
        return True
    has_openai = bool(os.environ.get('OPENAI_API_KEY', '').strip())
    has_gemini = bool(os.environ.get('GEMINI_API_KEY', '').strip())
    return not (has_openai or has_gemini)


DEMO_MODE: bool = _resolve_demo_mode()


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def generate_questions(resume: str, job_description: str) -> dict:
    """Return {'technical': [...], 'behavioral': [...]} or {'error': '...'}."""
    if not resume.strip() or not job_description.strip():
        return {"error": "Resume and Job Description cannot be empty."}

    if DEMO_MODE:
        from demo_data import get_demo_questions
        return get_demo_questions()

    return _live_generate_questions(resume, job_description)


def evaluate_answer(question: str, answer: str) -> dict:
    """Return scored evaluation dict or {'error': '...'}."""
    if not question.strip() or not answer.strip():
        return {"error": "Question and Answer cannot be empty."}

    if DEMO_MODE:
        from demo_data import get_demo_evaluation
        return get_demo_evaluation()

    return _live_evaluate_answer(question, answer)


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
