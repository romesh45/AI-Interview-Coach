# InterviewAI — AI-Powered Mock Interview Coach

> A full-stack Flask application that generates tailored interview questions from your resume and job description, evaluates your answers in real time, and tracks your progress over time.
>
> **Built as a portfolio project** showcasing Flask backend architecture, secure AI API integration (Gemini/OpenAI), and real-world SaaS patterns.

---

## Demo Mode

**No API key required to explore.** When `GROQ_API_KEY`, `GEMINI_API_KEY`, and `OPENAI_API_KEY` are all missing, the app automatically switches to Demo Mode — all AI responses (questions, evaluations, scores, feedback) are replaced with realistic simulated data so you can explore every feature without any setup.

```
# Run with zero config:
cp .env.example .env        # only SECRET_KEY needed
flask --app src/app run
```

---

## Features

| Feature | Details |
|---------|---------|
| **Resume-Tailored Questions** | 5 technical + 2 behavioural questions generated from your actual resume and the job description via Gemini or GPT |
| **AI Answer Evaluation** | 0–10 scoring with strengths, gaps, and exactly 3 actionable improvement suggestions via Gemini or GPT |
| **Voice Answers** | Record via microphone — Whisper transcribes it instantly |
| **Per-Question Timer** | 3-minute countdown that turns red under pressure |
| **PDF Resume Upload** | Upload a PDF or paste text — per-user persistent storage |
| **Progress Dashboard** | Score trend chart, skill breakdown, session history |
| **Demo Mode** | Realistic mock AI responses when API key is absent — zero-friction for reviewers |
| **CSRF Protection** | All state-changing forms and API endpoints protected via Flask-WTF |
| **Secure Auth** | Email + bcrypt-hashed passwords, Flask-Login sessions, rate limiting |
| **Profile Page** | Account info, resume status, daily usage quota visualisation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                              │
│  HTML/CSS/JS · Chart.js · Fetch API (voice, resume upload)  │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP
┌──────────────────────────▼──────────────────────────────────┐
│                    Flask Application                        │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  auth/   │  │ main/    │  │interview/│  │ api/     │   │
│  │ blueprint│  │dashboard │  │/app route│  │transcribe│   │
│  └──────────┘  └──────────┘  └──────────┘  │upload    │   │
│                                             │scores    │   │
│  ┌──────────┐  ┌──────────┐                └──────────┘   │
│  │ history/ │  │ profile/ │                               │
│  │ blueprint│  │ blueprint│                               │
│  └──────────┘  └──────────┘                               │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              ai_service.py  (AI layer)              │   │
│  │                                                     │   │
│  │  DEMO_MODE? ──yes──▶ demo_data.py (mock responses) │   │
│  │       │                                             │   │
│  │       no                                            │   │
│  │       ▼                                             │   │
│  │  question_generator.py ──▶ OpenAI GPT-4o-mini      │   │
│  │  evaluator.py          ──▶ OpenAI GPT-4o-mini      │   │
│  │  transcribe_audio()    ──▶ OpenAI Whisper          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │        SQLAlchemy ORM  ──▶  SQLite / PostgreSQL     │   │
│  │  User · InterviewSession · Evaluation               │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
interview-ai/
├── src/
│   ├── app.py                  # App factory (create_app)
│   ├── config.py               # Config classes (prod + test)
│   ├── models.py               # SQLAlchemy models + indexes
│   ├── auth.py                 # Auth blueprint
│   ├── ai_service.py           # AI layer with demo mode detection
│   ├── demo_data.py            # Realistic mock questions & evaluations
│   ├── question_generator.py   # GPT-4o-mini question generation
│   ├── evaluator.py            # GPT-4o-mini answer evaluation
│   ├── pdf_parser.py           # PyMuPDF text extraction
│   ├── prompts.py              # Prompt templates
│   └── blueprints/
│       ├── main.py             # / and /dashboard
│       ├── interview.py        # /app (interview flow)
│       ├── history.py          # /history/*
│       ├── api.py              # /api/transcribe, /api/upload-resume, /api/scores
│       └── profile.py          # /profile
├── templates/
│   ├── landing.html
│   ├── index.html              # Interview UI
│   ├── dashboard.html
│   ├── history.html
│   ├── session_detail.html
│   ├── profile.html
│   └── auth/
│       ├── login.html
│       └── register.html
├── static/
│   ├── uploads/                # Temp audio files (gitignored)
│   └── resumes/                # Per-user resume PDFs (gitignored)
├── tests/
│   ├── conftest.py             # pytest fixtures (demo mode, test DB)
│   ├── test_auth.py            # Register, login, logout, duplicate email
│   ├── test_interview.py       # Full interview flow in demo mode
│   └── test_resume.py          # Resume upload/delete, API endpoints
├── tests.py                    # Legacy unit tests (question_generator, evaluator)
├── requirements.txt
├── render.yaml                 # Render.com deployment
└── .env.example
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, Flask 3.0, Gunicorn |
| **Auth** | Flask-Login, bcrypt |
| **Security** | Flask-WTF CSRF protection |
| **Database** | SQLite (dev) / PostgreSQL (prod) via Flask-SQLAlchemy |
| **AI — Questions** | Gemini (default) or OpenAI (configurable) |
| **AI — Evaluation** | Gemini (default) or OpenAI (configurable) |
| **AI — Voice** | OpenAI Whisper |
| **PDF** | PyMuPDF (fitz) |
| **Frontend** | Vanilla HTML/CSS/JS, Chart.js, Google Fonts |
| **Deploy** | Render.com |
| **Tests** | pytest + pytest-flask |

---

## Local Setup

### 1. Clone and install

```bash
git clone https://github.com/your-username/interview-ai.git
cd interview-ai
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Required — generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=your-random-secret-key

# AI provider: auto | groq | gemini | openai
AI_PROVIDER=auto

# Recommended: Groq key (backend only, never exposed to frontend)
GROQ_API_KEY=your-groq-api-key

# Optional: override Groq model
# GROQ_MODEL=llama-3.3-70b-versatile

# Optional: Gemini fallback
# GEMINI_API_KEY=your-gemini-api-key
# GEMINI_MODEL=gemini-2.0-flash

# Optional: OpenAI fallback (if you want it)
# OPENAI_API_KEY=sk-...
```

### 3. Run

```bash
flask --app src/app run --port 5001
```

Visit `http://127.0.0.1:5001` — register an account and start your first mock interview.

---

## Demo Mode

Demo Mode activates automatically when:
- `GROQ_API_KEY`, `GEMINI_API_KEY`, and `OPENAI_API_KEY` are missing or empty
- `DEMO_MODE=true` is set (overrides even if a key exists)

In demo mode:
- Question generation returns a realistic set of 5 technical + 2 behavioural questions
- Answer evaluation returns realistic scores (5–9), structured feedback, strengths, gaps, and 3 improvement suggestions
- Voice transcription returns a placeholder message
- A yellow banner is shown on all pages indicating demo mode

This design allows recruiters and reviewers to explore every feature of the app without needing an API key or account on OpenAI.

Keys are used only on the backend via environment variables. The frontend never receives or stores provider API keys.

---

## Running Tests

```bash
# New pytest suite (runs entirely in demo mode — no API key needed)
pytest tests/ -v

# Legacy unit tests (mocks OpenAI client)
python tests.py
```

---

## Deployment (Render.com)

1. Push to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your repo — Render detects `render.yaml` automatically
4. Set environment variables:
    - `AI_PROVIDER=auto` (or `groq`)
    - `GROQ_API_KEY=<your key>`
    - optional: `GROQ_MODEL=llama-3.3-70b-versatile`
5. Deploy — `SECRET_KEY` is auto-generated by Render

The app will be live at `https://your-service.onrender.com`.

To switch to PostgreSQL on Render: add a **PostgreSQL** database resource — Render sets `DATABASE_URL` automatically and the app picks it up with no code changes.

---

## Key Design Decisions

**App factory pattern** — `create_app()` in `src/app.py` enables clean testing with an in-memory SQLite database and disabled CSRF, without touching production config.

**AI service layer** — `ai_service.py` is the single entry point for all AI calls. Demo mode detection happens once at import time (`DEMO_MODE: bool = _resolve_demo_mode()`), keeping the rest of the app unaware of whether it's talking to real AI or mock data.

**Lazy OpenAI client** — `question_generator.py` and `evaluator.py` initialise the OpenAI client on first call (not at import), so the modules can be imported safely in demo mode or tests without a valid API key.

**PostgreSQL-ready** — The config layer normalises `postgres://` → `postgresql://` (Render.com quirk) and the ORM schema is identical between SQLite and PostgreSQL.
