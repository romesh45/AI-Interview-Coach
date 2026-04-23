import os
import re
import uuid

from flask import (Blueprint, request, jsonify,
                   session as flask_session, current_app)
from flask_login import login_required, current_user
from extensions import csrf

from models import db
from ai_service import transcribe_audio
from pdf_parser import extract_text_from_pdf

api = Blueprint('api', __name__, url_prefix='/api')

_RESUME_FILE_PATTERN = re.compile(r'resume_user_\d+_[a-f0-9]{32}\.pdf')


# ── TRANSCRIPTION ─────────────────────────────────────────────────────────────

@api.route('/transcribe', methods=['POST'])
@csrf.exempt
@login_required
def transcribe():
    audio_file = request.files.get('audio')
    if not audio_file:
        return jsonify({'error': 'No audio file provided'}), 400

    safe_name = f'voice_{uuid.uuid4().hex}.webm'
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], safe_name)
    audio_file.save(save_path)

    result = transcribe_audio(save_path)

    try:
        os.remove(save_path)
    except OSError:
        pass

    if 'error' in result:
        return jsonify(result), 500
    return jsonify(result)


# ── RESUME UPLOAD / DELETE ────────────────────────────────────────────────────

@api.route('/upload-resume', methods=['POST'])
@csrf.exempt
@login_required
def upload_resume():
    resume_pdf = request.files.get('resume_pdf') or request.files.get('resume')
    if not resume_pdf or not resume_pdf.filename:
        return jsonify({'error': 'No resume file provided'}), 400
    if not resume_pdf.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDF files are supported'}), 400

    previous = flask_session.get('uploaded_resume_filename')
    if previous:
        prev_path = _resume_path(previous)
        if os.path.exists(prev_path):
            try:
                os.remove(prev_path)
            except OSError:
                current_app.logger.warning('Could not delete old resume: %s', prev_path)

    filename  = f'resume_user_{current_user.id}_{uuid.uuid4().hex}.pdf'
    save_path = _resume_path(filename)
    resume_pdf.save(save_path)

    parsed = extract_text_from_pdf(save_path)
    if 'error' in parsed:
        try:
            os.remove(save_path)
        except OSError:
            pass
        return jsonify({'error': 'Unable to parse resume PDF. Is it a text-based PDF?'}), 400

    flask_session['uploaded_resume_filename'] = filename
    return jsonify({
        'message':     'Resume uploaded successfully',
        'filename':    filename,
        'text_length': len(parsed['text']),
    })


@api.route('/upload-resume', methods=['DELETE'])
@csrf.exempt
@login_required
def delete_resume():
    filename = flask_session.get('uploaded_resume_filename')
    if not filename:
        return jsonify({'error': 'No resume on file'}), 404
    if not _is_valid_filename(filename) or not _is_owner(filename):
        current_app.logger.warning(
            'Resume delete validation failed — user %s, file %s', current_user.id, filename
        )
        flask_session.pop('uploaded_resume_filename', None)
        return jsonify({'error': 'Resume not found'}), 404

    flask_session.pop('uploaded_resume_filename', None)
    path = _resume_path(filename)
    if not os.path.exists(path):
        return jsonify({'error': 'Resume file not found on disk'}), 404

    try:
        os.remove(path)
    except OSError:
        return jsonify({'error': 'Unable to delete resume file'}), 500

    return jsonify({'message': 'Resume deleted successfully'})


# ── SCORES ────────────────────────────────────────────────────────────────────

@api.route('/scores')
@login_required
def scores():
    from models import InterviewSession, Evaluation
    from flask_login import current_user
    from flask import session as flask_session

    sid = flask_session.get('active_session_id')
    if not sid:
        return jsonify({'scores': [], 'labels': [], 'average': 0})

    active = InterviewSession.query.filter_by(id=sid, user_id=current_user.id).first()
    if not active:
        return jsonify({'scores': [], 'labels': [], 'average': 0})

    evals  = Evaluation.query.filter_by(session_id=active.id).all()
    s_list = [e.score for e in evals]
    labels = [e.skill or f'Q{i+1}' for i, e in enumerate(evals)]
    avg    = round(sum(s_list) / len(s_list), 1) if s_list else 0
    return jsonify({'scores': s_list, 'labels': labels, 'average': avg})


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _resume_path(filename: str) -> str:
    return os.path.join(current_app.config['RESUME_FOLDER'], os.path.basename(filename))


def _is_valid_filename(filename: str) -> bool:
    return bool(_RESUME_FILE_PATTERN.fullmatch(filename))


def _is_owner(filename: str) -> bool:
    return filename.startswith(f'resume_user_{current_user.id}_')
