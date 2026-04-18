import os
import sys
import json

# Ensure src/ is in path when running from project root
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from dotenv import load_dotenv

load_dotenv()

from question_generator import generate_questions
from evaluator import evaluate_answer
from pdf_parser import extract_text_from_pdf
from models import db, InterviewSession, Evaluation

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

# Database config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '..', 'interviews.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

db.init_app(app)

with app.app_context():
    db.create_all()

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
def index():
    error = None

    if 'questions' not in session:
        session['questions'] = None
    if 'evaluations' not in session:
        session['evaluations'] = {}
    if 'session_id' not in session:
        session['session_id'] = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'generate':
            resume_text = ''
            job_description = request.form.get('job_description', '').strip()

            # Handle PDF upload
            pdf_file = request.files.get('resume_pdf')
            if pdf_file and pdf_file.filename.endswith('.pdf'):
                save_path = os.path.join(UPLOAD_FOLDER, 'resume_temp.pdf')
                pdf_file.save(save_path)
                result = extract_text_from_pdf(save_path)
                if 'error' in result:
                    error = result['error']
                else:
                    resume_text = result['text']
                try:
                    os.remove(save_path)
                except Exception:
                    pass
            else:
                resume_text = request.form.get('resume', '').strip()

            if not error:
                if not resume_text or not job_description:
                    error = "Please provide both resume content and job description."
                else:
                    result = generate_questions(resume_text, job_description)
                    if 'error' in result:
                        error = result['error']
                    else:
                        session['questions'] = result
                        session['evaluations'] = {}

                        # Create DB session record
                        job_title = _extract_job_title(job_description)
                        resume_snippet = resume_text[:200]
                        interview = InterviewSession(
                            job_title=job_title,
                            resume_snippet=resume_snippet,
                            total_questions=7
                        )
                        db.session.add(interview)
                        db.session.commit()
                        session['session_id'] = interview.id
                        session.modified = True

        elif action == 'evaluate':
            question = request.form.get('question', '')
            answer = request.form.get('answer', '')
            q_skill = request.form.get('skill', '')
            q_difficulty = request.form.get('difficulty', '')
            q_type = request.form.get('q_type', 'technical')

            result = evaluate_answer(question, answer)
            if 'error' in result:
                error = result['error']
            else:
                evals = session.get('evaluations', {})
                evals[question] = {'answer': answer, 'evaluation': result}
                session['evaluations'] = evals
                session.modified = True

                # Persist to DB
                sid = session.get('session_id')
                if sid:
                    # Upsert evaluation
                    existing = Evaluation.query.filter_by(session_id=sid, question=question).first()
                    if existing:
                        existing.answer = answer
                        existing.score = float(result['score'])
                        existing.feedback = result['feedback']
                    else:
                        ev = Evaluation(
                            session_id=sid,
                            question=question,
                            answer=answer,
                            score=float(result['score']),
                            feedback=result['feedback'],
                            question_type=q_type,
                            skill=q_skill,
                            difficulty=q_difficulty
                        )
                        db.session.add(ev)
                    db.session.commit()

                    interview = InterviewSession.query.get(sid)
                    if interview:
                        interview.update_stats()

        elif action == 'reset':
            session.clear()
            return redirect(url_for('index'))

    return render_template(
        'index.html',
        questions=session.get('questions'),
        evaluations=session.get('evaluations'),
        error=error
    )


@app.route('/history')
def history():
    sessions = InterviewSession.query.order_by(InterviewSession.created_at.desc()).limit(20).all()
    return render_template('history.html', sessions=sessions)


@app.route('/history/<int:session_id>')
def session_detail(session_id):
    interview = InterviewSession.query.get_or_404(session_id)
    evaluations = Evaluation.query.filter_by(session_id=session_id).all()
    return render_template('session_detail.html', interview=interview, evaluations=evaluations)


@app.route('/history/<int:session_id>/delete', methods=['POST'])
def delete_session(session_id):
    interview = InterviewSession.query.get_or_404(session_id)
    db.session.delete(interview)
    db.session.commit()
    return redirect(url_for('history'))


@app.route('/api/transcribe', methods=['POST'])
def transcribe_audio():
    """Transcribe audio using OpenAI Whisper."""
    try:
        from openai import OpenAI
        client = OpenAI()
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400

        save_path = os.path.join(UPLOAD_FOLDER, 'voice_temp.webm')
        audio_file.save(save_path)

        with open(save_path, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                response_format="text"
            )
        try:
            os.remove(save_path)
        except Exception:
            pass

        return jsonify({'text': transcript})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/scores')
def api_scores():
    sid = session.get('session_id')
    if not sid:
        return jsonify({'scores': [], 'labels': [], 'average': 0})
    evals = Evaluation.query.filter_by(session_id=sid).all()
    scores = [e.score for e in evals]
    labels = [e.skill or f'Q{i+1}' for i, e in enumerate(evals)]
    avg = round(sum(scores) / len(scores), 1) if scores else 0
    return jsonify({'scores': scores, 'labels': labels, 'average': avg})


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_job_title(jd: str) -> str:
    """Best-effort extract job title from first line of job description."""
    lines = [l.strip() for l in jd.splitlines() if l.strip()]
    if lines:
        first = lines[0]
        return first[:80] if len(first) <= 80 else first[:77] + '...'
    return 'Software Engineer'


if __name__ == '__main__':
    app.run(debug=True, port=5001)
