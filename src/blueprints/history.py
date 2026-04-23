from flask import Blueprint, render_template, redirect, url_for, session as flask_session
from flask_login import login_required, current_user

from models import db, InterviewSession, Evaluation

history = Blueprint('history', __name__)


@history.route('/history')
@history.route('/history/')
@login_required
def history_list():
    sessions = (InterviewSession.query
                .filter_by(user_id=current_user.id)
                .order_by(InterviewSession.created_at.desc())
                .limit(20).all())
    return render_template('history.html', sessions=sessions)


@history.route('/history/<int:session_id>')
@login_required
def session_detail(session_id):
    interview   = InterviewSession.query.filter_by(
        id=session_id, user_id=current_user.id).first_or_404()
    evaluations = Evaluation.query.filter_by(session_id=session_id).all()
    return render_template('session_detail.html',
                           interview=interview, evaluations=evaluations)


@history.route('/history/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_session(session_id):
    interview = InterviewSession.query.filter_by(
        id=session_id, user_id=current_user.id).first_or_404()
    db.session.delete(interview)
    db.session.commit()
    if flask_session.get('active_session_id') == session_id:
        flask_session.pop('active_session_id', None)
    return redirect(url_for('history.history_list'))
