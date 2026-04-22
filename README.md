# InterviewAI — Advanced Mock Interview Coach

A production-grade AI interview coaching platform that generates tailored interview questions from your resume and job description, then evaluates your answers in real time with professional feedback.

## Features

- **User Auth** — Secure registration & login (email + password, bcrypt hashed)
- **Per-User Sessions** — All interview data scoped to your account
- **Rate Limiting** — Free tier: 10 AI evaluations/day
- **Smart Question Generation** — 5 technical + 2 behavioural questions tailored to your resume and JD
- **PDF Resume Upload** — Upload your resume as a PDF or paste text directly
- **Voice Recording** — Answer questions using your microphone (Whisper transcription)
- **Per-Question Timer** — 3-minute countdown timer per question
- **AI Evaluation** — Score out of 10 with strengths, gaps, and actionable improvements
- **Score Analytics** — Live bar chart showing your performance across all answers
- **Session History** — All past interviews saved to SQLite with detailed breakdown
- **Professional UI** — Clean, modern design with score ring animations

## Project Structure

```
interview_ai/
├── src/
│   ├── app.py                  # Flask application, all routes (main blueprint)
│   ├── auth.py                 # Auth blueprint (register, login, logout)
│   ├── question_generator.py   # Generates 7 tailored questions via GPT-4o-mini
│   ├── evaluator.py            # Scores answers with detailed feedback
│   ├── prompts.py              # All prompt templates
│   ├── models.py               # SQLAlchemy models (User, InterviewSession, Evaluation)
│   └── pdf_parser.py           # PyMuPDF PDF text extraction
├── templates/
│   ├── auth/
│   │   ├── login.html          # Login page
│   │   └── register.html       # Registration page
│   ├── index.html              # Main interview UI
│   ├── history.html            # Past sessions list
│   └── session_detail.html     # Individual session breakdown
├── static/
│   └── uploads/                # Temp files (gitignored)
├── tests.py                    # Unit tests
├── requirements.txt
├── render.yaml                 # Render.com deployment config
├── .env.example                # Environment variable template
└── .gitignore
```

## Setup

### 1. Clone and install

```bash
git clone <your-repo-url>
cd interview_ai
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your OpenAI API key + a secret key
```

### 3. Run locally

```bash
flask --app src/app run
```

Visit `http://127.0.0.1:5000` — you'll be redirected to login/register.

## Running Tests

```bash
python tests.py
```

## Deployment on Render

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Add environment variable: `OPENAI_API_KEY = your_key`
5. Deploy

## Tech Stack

- **Backend**: Python 3.11, Flask 3.0, Flask-Login, SQLAlchemy, Gunicorn
- **Auth**: Flask-Login + bcrypt password hashing
- **AI**: OpenAI GPT-4o-mini (questions + evaluation), Whisper (voice transcription)
- **PDF**: PyMuPDF (fitz)
- **Database**: SQLite (local) via Flask-SQLAlchemy
- **Frontend**: Vanilla HTML/CSS/JS, Chart.js, Google Fonts (Syne + DM Sans)
- **Deploy**: Render.com

## Rate Limits

| Plan | AI Evals/day |
|------|-------------|
| Free | 10 |
| Pro  | 100 |
