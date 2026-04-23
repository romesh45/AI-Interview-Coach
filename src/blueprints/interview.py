import os
import re
import uuid

from flask import (Blueprint, render_template, request,
                   session as flask_session, redirect, url_for, current_app)
from flask_login import login_required, current_user

from models import db, InterviewSession, Evaluation
from ai_service import generate_questions, evaluate_answer
from pdf_parser import extract_text_from_pdf

interview = Blueprint('interview', __name__)

_RESUME_FILE_PATTERN = re.compile(r'resume_user_\d+_[a-f0-9]{32}\.pdf')


# ── MAIN INTERVIEW ROUTE ──────────────────────────────────────────────────────

@interview.route('/app', methods=['GET', 'POST'])
@login_required
def index():
    error          = None
    active_session = _get_active_session()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'generate':
            error, active_session = _handle_generate(active_session)

        elif action == 'evaluate':
            error = _handle_evaluate(active_session)

        elif action == 'reset':
            flask_session.pop('active_session_id', None)
            return redirect(url_for('interview.index'))

    evaluations = _get_evaluations(active_session)

    return render_template(
        'index.html',
        active_session     = active_session,
        questions          = active_session.questions if active_session else None,
        evaluations        = evaluations,
        error              = error,
        requests_remaining = current_user.requests_remaining(),
    )


# ── HANDLERS ─────────────────────────────────────────────────────────────────

def _handle_generate(active_session):
    error = None
    if not current_user.can_make_request():
        error = (f"Daily limit reached ({current_user.daily_limit()} "
                 f"interviews/day). Reset tomorrow or set DEMO_MODE=true.")
        return error, active_session

    resume_text     = ''
    job_description = request.form.get('job_description', '').strip()
    uploaded_name   = flask_session.get('uploaded_resume_filename')

    if uploaded_name:
        saved_path = _resume_file_path(uploaded_name)
        if os.path.exists(saved_path):
            resume_text, parse_error = _extract_resume_text(saved_path)
            if parse_error:
                error = parse_error
        else:
            flask_session.pop('uploaded_resume_filename', None)

    pdf_file = request.files.get('resume_pdf')
    if not resume_text and not error and pdf_file and pdf_file.filename.lower().endswith('.pdf'):
        tmp_name = f'resume_{uuid.uuid4().hex}.pdf'
        tmp_path = os.path.join(current_app.config['UPLOAD_FOLDER'], tmp_name)
        pdf_file.save(tmp_path)
        result = extract_text_from_pdf(tmp_path)
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        if 'error' in result:
            error = result['error']
        else:
            resume_text = result['text']

    if not resume_text and not error:
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
                sess            = InterviewSession(
                    user_id        = current_user.id,
                    job_title      = _extract_job_title(job_description),
                    resume_snippet = resume_text[:200],
                    total_questions= 7,
                )
                sess.questions = result
                db.session.add(sess)
                db.session.commit()
                flask_session['active_session_id'] = sess.id
                active_session = sess

    return error, active_session


def _handle_evaluate(active_session):
    if not active_session:
        return "No active interview session. Please generate questions first."

    question     = request.form.get('question', '')
    answer       = request.form.get('answer', '').strip()
    q_skill      = request.form.get('skill', '')
    q_difficulty = request.form.get('difficulty', '')
    q_type       = request.form.get('q_type', 'technical')

    if not answer:
        return "Please write an answer before submitting."

    result = evaluate_answer(question, answer)
    if 'error' in result:
        return result['error']

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
    return None


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _get_active_session():
    sid = flask_session.get('active_session_id')
    if not sid:
        return None
    return InterviewSession.query.filter_by(id=sid, user_id=current_user.id).first()


def _get_evaluations(active_session):
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
    return os.path.join(current_app.config['RESUME_FOLDER'], os.path.basename(filename))


def _extract_resume_text(file_path: str):
    parsed = extract_text_from_pdf(file_path)
    if 'error' in parsed:
        current_app.logger.warning('Resume parse failed: %s — %s', file_path, parsed['error'])
        return '', True
    return parsed.get('text', ''), False
