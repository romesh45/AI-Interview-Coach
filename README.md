# InterviewAI — Advanced Mock Interview Coach

A production-grade AI interview coaching platform that generates tailored interview questions from your resume and job description, then evaluates your answers in real time with professional feedback.

## Features

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
ai_interview_coach/
├── src/
│   ├── app.py                  # Flask application, all routes
│   ├── question_generator.py   # Generates 7 tailored questions via GPT-4o-mini
│   ├── evaluator.py            # Scores answers with detailed feedback
│   ├── prompts.py              # All prompt templates
│   ├── models.py               # SQLAlchemy models (InterviewSession, Evaluation)
│   └── pdf_parser.py           # PyMuPDF PDF text extraction
├── templates/
│   ├── index.html              # Main interview UI
│   ├── history.html            # Past sessions list
│   └── session_detail.html     # Individual session breakdown
├── static/
│   └── uploads/                # Temp files (gitignored)
├── tests.py                    # Unit tests
├── requirements.txt
├── render.yaml                 # Render.com deployment config
├── .env                        # API keys (do not commit)
└── .gitignore
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Edit `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
SECRET_KEY=your-strong-random-secret-key
```

### 3. Run locally

```bash
flask --app src/app run
```

Visit `http://127.0.0.1:5000`

## Running Tests

```bash
python tests.py
```

## Deployment on Render (Free)

1. Push this repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Add environment variable: `OPENAI_API_KEY = your_key`
6. Deploy — your app will be live at `https://interview-ai.onrender.com`

## Tech Stack

- **Backend**: Python 3.11, Flask 3.0, SQLAlchemy, Gunicorn
- **AI**: OpenAI GPT-4o-mini (questions + evaluation), Whisper (voice transcription)
- **PDF**: PyMuPDF (fitz)
- **Database**: SQLite (local) via Flask-SQLAlchemy
- **Frontend**: Vanilla HTML/CSS/JS, Chart.js, Google Fonts (Syne + DM Sans)
- **Deploy**: Render.com (free tier)
