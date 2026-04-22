import os
import re
import sys
import uuid

sys.path.insert(0, os.path.dirname(__file__))

from flask import (Flask, render_template, request, session,
                   redirect, url_for, jsonify, Blueprint)
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

load_dotenv()

from auth import auth as auth_blueprint
from question_generator import generate_questions
from evaluator import evaluate_answer
from pdf_parser import extract_text_from_pdf
from models import db, User, InterviewSession, Evaluation

# ── APP SETUP ─────────────────────────────────────────────────────────────────

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'sqlite:///' + os.path.join(basedir, '..', 'interviews.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB

db.init_app(app)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view         = 'auth.login'
login_manager.login_message      = 'Please log in to access InterviewAI.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(auth_blueprint)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
RESUME_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'resumes')
RESUME_FILE_PATTERN = re.compile(r'resume_user_\d+_[a-f0-9]{32}\.pdf')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESUME_FOLDER, exist_ok=True)

with app.app_context():
    db.create_all()


# ── MAIN BLUEPRINT ────────────────────────────────────────────────────────────

main = Blueprint('main', __name__)


@main.route('/')
def landing():
    """Public landing page. Logged-in users go straight to dashboard."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main.route('/app', methods=['GET', 'POST'])
@login_required
def index():
    error          = None
    active_session = _get_active_session()

    if request.method == 'POST':
        action = request.form.get('action')

        # ── GENERATE ──────────────────────────────────────────────────────────
        if action == 'generate':
            if not current_user.can_make_request():
                error = (f"Daily limit reached ({current_user.daily_limit()} "
                         f"interviews/day). Upgrade to Pro for more.")
            else:
                resume_text     = ''
                job_description = request.form.get('job_description', '').strip()
                uploaded_resume = session.get('uploaded_resume_filename')

                if uploaded_resume:
                    saved_resume_path = _resume_file_path(uploaded_resume)
                    if os.path.exists(saved_resume_path):
                        resume_text, parse_error = _extract_resume_text(saved_resume_path)
                        if parse_error:
                            error = parse_error
                    else:
                        session.pop('uploaded_resume_filename', None)

                pdf_file = request.files.get('resume_pdf')
                if not resume_text and pdf_file and pdf_file.filename.lower().endswith('.pdf'):
                    safe_name = f'resume_{uuid.uuid4().hex}.pdf'
                    save_path = os.path.join(UPLOAD_FOLDER, safe_name)
                    pdf_file.save(save_path)
                    result = extract_text_from_pdf(save_path)
                    try:
                        os.remove(save_path)
                    except Exception:
                        pass
                    if 'error' in result:
                        error = result['error']
                    else:
                        resume_text = result['text']
                elif not resume_text:
                    resume_text = request.form.get('resume', '').strip()

                if not error:
                    if not resume_text or not job_description:
                        error = "Please provide both resume content and job description."
                    else:
                        result = generate_questions(resume_text, job_description)
                        if 'error' in result:
                            error = result['error']
                        else:
                            current_user.consume_request()
                            interview          = InterviewSession(
                                user_id        = current_user.id,
                                job_title      = _extract_job_title(job_description),
                                resume_snippet = resume_text[:200],
                                total_questions= 7,
                            )
                            interview.questions = result
                            db.session.add(interview)
                            db.session.commit()
                            session['active_session_id'] = interview.id
                            active_session = interview

        # ── EVALUATE ──────────────────────────────────────────────────────────
        elif action == 'evaluate':
            if not active_session:
                error = "No active interview session. Please generate questions first."
            else:
                question     = request.form.get('question', '')
                answer       = request.form.get('answer', '').strip()
                q_skill      = request.form.get('skill', '')
                q_difficulty = request.form.get('difficulty', '')
                q_type       = request.form.get('q_type', 'technical')

                if not answer:
                    error = "Please write an answer before submitting."
                else:
                    result = evaluate_answer(question, answer)
                    if 'error' in result:
                        error = result['error']
                    else:
                        existing = Evaluation.query.filter_by(
                            session_id=active_session.id, question=question
                        ).first()
                        if existing:
                            existing.answer      = answer
                            existing.score       = float(result['score'])
                            existing.feedback    = result['feedback']
                            existing.full_result = result
                        else:
                            ev = Evaluation(
                                session_id    = active_session.id,
                                question      = question,
                                answer        = answer,
                                score         = float(result['score']),
                                feedback      = result['feedback'],
                                question_type = q_type,
                                skill         = q_skill,
                                difficulty    = q_difficulty,
                            )
                            ev.full_result = result
                            db.session.add(ev)
                        db.session.commit()
                        active_session.update_stats()

        # ── RESET ─────────────────────────────────────────────────────────────
        elif action == 'reset':
            session.pop('active_session_id', None)
            return redirect(url_for('main.index'))   # /app

    evaluations = _get_evaluations(active_session)

    return render_template(
        'index.html',
        active_session     = active_session,
        questions          = active_session.questions if active_session else None,
        evaluations        = evaluations,
        error              = error,
        requests_remaining = current_user.requests_remaining(),
    )


@main.route('/dashboard')
@login_required
def dashboard():
    from collections import defaultdict

    sessions = (InterviewSession.query
                .filter_by(user_id=current_user.id)
                .order_by(InterviewSession.created_at.asc())
                .all())

    all_evals = (Evaluation.query
                 .join(InterviewSession)
                 .filter(InterviewSession.user_id == current_user.id)
                 .all())

    # ── Stat cards ────────────────────────────────────────────────────────────
    total_sessions  = len(sessions)
    total_answers   = len(all_evals)
    all_scores      = [e.score for e in all_evals]
    avg_score_all   = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    best_score      = max(all_scores) if all_scores else 0

    # ── Score trend (one point per session, only sessions with answers) ───────
    trend_labels = []
    trend_scores = []
    for s in sessions:
        if s.answered_questions > 0:
            trend_labels.append(s.created_at.strftime('%b %d'))
            trend_scores.append(s.average_score)

    # ── Skill breakdown (avg score per skill tag) ─────────────────────────────
    skill_totals  = defaultdict(list)
    for e in all_evals:
        skill = e.skill.strip() if e.skill and e.skill.strip() else 'General'
        skill_totals[skill].append(e.score)

    skill_labels = []
    skill_avgs   = []
    for skill, scores in sorted(skill_totals.items(), key=lambda x: sum(x[1])/len(x[1])):
        skill_labels.append(skill)
        skill_avgs.append(round(sum(scores) / len(scores), 1))

    # ── Recent sessions (last 8) ──────────────────────────────────────────────
    recent_sessions = list(reversed(sessions[-8:]))

    return render_template(
        'dashboard.html',
        total_sessions  = total_sessions,
        total_answers   = total_answers,
        avg_score_all   = avg_score_all,
        best_score      = best_score,
        trend_labels    = trend_labels,
        trend_scores    = trend_scores,
        skill_labels    = skill_labels,
        skill_avgs      = skill_avgs,
        recent_sessions = recent_sessions,
        requests_remaining = current_user.requests_remaining(),
    )


@main.route('/history')
@main.route('/history/')
@login_required
def history():
    sessions = (InterviewSession.query
                .filter_by(user_id=current_user.id)
                .order_by(InterviewSession.created_at.desc())
                .limit(20).all())
    return render_template('history.html', sessions=sessions)


@main.route('/history/<int:session_id>')
@login_required
def session_detail(session_id):
    interview   = InterviewSession.query.filter_by(
        id=session_id, user_id=current_user.id).first_or_404()
    evaluations = Evaluation.query.filter_by(session_id=session_id).all()
    return render_template('session_detail.html',
                           interview=interview, evaluations=evaluations)


@main.route('/history/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    interview = InterviewSession.query.filter_by(
        id=session_id, user_id=current_user.id).first_or_404()
    db.session.delete(interview)
    db.session.commit()
    if session.get('active_session_id') == session_id:
        session.pop('active_session_id', None)
    return redirect(url_for('main.history'))


@main.route('/api/transcribe', methods=['POST'])
@login_required
def transcribe_audio():
    try:
        from openai import OpenAI
        client     = OpenAI()
        audio_file = request.files.get('audio')
        if not audio_file:
            return jsonify({'error': 'No audio file provided'}), 400

        safe_name = f'voice_{uuid.uuid4().hex}.webm'
        save_path = os.path.join(UPLOAD_FOLDER, safe_name)
        audio_file.save(save_path)

        with open(save_path, 'rb') as f:
            transcript = client.audio.transcriptions.create(
                model='whisper-1', file=f, response_format='text')
        try:
            os.remove(save_path)
        except Exception:
            pass
        return jsonify({'text': transcript})
    except Exception as e:
        app.logger.exception('Audio transcription failed')
        return jsonify({'error': 'Audio transcription failed'}), 500


@main.route('/api/upload-resume', methods=['POST'])
@login_required
def upload_resume():
    resume_pdf = request.files.get('resume_pdf') or request.files.get('resume')
    if not resume_pdf or not resume_pdf.filename:
        return jsonify({'error': 'No resume file provided'}), 400
    if not resume_pdf.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    previous_resume = session.get('uploaded_resume_filename')
    if previous_resume:
        previous_path = _resume_file_path(previous_resume)
        if os.path.exists(previous_path):
            try:
                os.remove(previous_path)
            except OSError:
                app.logger.warning('Failed to delete old resume file: %s', previous_path)

    filename = f'resume_user_{current_user.id}_{uuid.uuid4().hex}.pdf'
    save_path = _resume_file_path(filename)
    resume_pdf.save(save_path)
    resume_text, has_parse_error = _extract_resume_text(save_path)
    if has_parse_error:
        try:
            os.remove(save_path)
        except OSError:
            app.logger.warning('Failed to delete invalid resume file: %s', save_path)
        return jsonify({'error': 'Unable to parse resume PDF'}), 400

    session['uploaded_resume_filename'] = filename
    return jsonify({
        'message': 'Resume uploaded successfully',
        'filename': filename,
        'text_length': len(resume_text),
    })


@main.route('/api/upload-resume', methods=['DELETE'])
@login_required
def delete_uploaded_resume():
    filename = session.get('uploaded_resume_filename')
    if not filename:
        return jsonify({'error': 'No resume selected'}), 404
    if not _is_valid_resume_filename(filename) or not _is_current_user_resume(filename):
        app.logger.warning('Resume delete validation failed for user %s: %s', current_user.id, filename)
        session.pop('uploaded_resume_filename', None)
        return jsonify({'error': 'Resume not found'}), 404

    session.pop('uploaded_resume_filename', None)

    resume_path = _resume_file_path(filename)
    if os.path.exists(resume_path):
        try:
            os.remove(resume_path)
        except OSError:
            return jsonify({'error': 'Unable to delete resume file'}), 500
        return jsonify({'message': 'Resume deleted successfully'})
    return jsonify({'error': 'Resume file not found'}), 404


@main.route('/api/scores')
@login_required
def api_scores():
    active_session = _get_active_session()
    if not active_session:
        return jsonify({'scores': [], 'labels': [], 'average': 0})
    evals  = Evaluation.query.filter_by(session_id=active_session.id).all()
    scores = [e.score for e in evals]
    labels = [e.skill or f'Q{i+1}' for i, e in enumerate(evals)]
    avg    = round(sum(scores) / len(scores), 1) if scores else 0
    return jsonify({'scores': scores, 'labels': labels, 'average': avg})


app.register_blueprint(main)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _get_active_session() -> InterviewSession | None:
    sid = session.get('active_session_id')
    if not sid:
        return None
    return InterviewSession.query.filter_by(
        id=sid, user_id=current_user.id).first()


def _get_evaluations(active_session: InterviewSession | None) -> dict:
    if not active_session:
        return {}
    evals  = Evaluation.query.filter_by(session_id=active_session.id).all()
    result = {}
    for ev in evals:
        full = ev.full_result
        result[ev.question] = {
            'answer': ev.answer,
            'evaluation': {
                'score':                   ev.score,
                'feedback':                ev.feedback,
                'strengths':               full.get('strengths', []),
                'gaps':                    full.get('gaps', []),
                'improvement_suggestions': full.get('improvement_suggestions', []),
            }
        }
    return result


def _extract_job_title(jd: str) -> str:
    lines = [l.strip() for l in jd.splitlines() if l.strip()]
    if lines:
        first = lines[0]
        return first[:80] if len(first) <= 80 else first[:77] + '...'
    return 'Software Engineer'


def _resume_file_path(filename: str) -> str:
    safe_name = os.path.basename(filename)
    return os.path.join(RESUME_FOLDER, safe_name)


def _extract_resume_text(file_path: str) -> tuple[str, bool]:
    parsed = extract_text_from_pdf(file_path)
    if 'error' in parsed:
        app.logger.warning('Resume parsing failed for %s: %s', file_path, parsed.get('error'))
        return '', True
    return parsed.get('text', ''), False


def _is_valid_resume_filename(filename: str) -> bool:
    return bool(RESUME_FILE_PATTERN.fullmatch(filename))


def _is_current_user_resume(filename: str) -> bool:
    return filename.startswith(f'resume_user_{current_user.id}_')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
