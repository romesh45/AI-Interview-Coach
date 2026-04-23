from collections import defaultdict

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

from models import InterviewSession, Evaluation

main = Blueprint('main', __name__)


@main.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main.route('/dashboard')
@login_required
def dashboard():
    sessions = (InterviewSession.query
                .filter_by(user_id=current_user.id)
                .order_by(InterviewSession.created_at.asc())
                .all())

    all_evals = (Evaluation.query
                 .join(InterviewSession)
                 .filter(InterviewSession.user_id == current_user.id)
                 .all())

    total_sessions = len(sessions)
    total_answers  = len(all_evals)
    all_scores     = [e.score for e in all_evals]
    avg_score_all  = round(sum(all_scores) / len(all_scores), 1) if all_scores else 0
    best_score     = max(all_scores) if all_scores else 0

    trend_labels, trend_scores = [], []
    for s in sessions:
        if s.answered_questions > 0:
            trend_labels.append(s.created_at.strftime('%b %d'))
            trend_scores.append(s.average_score)

    skill_totals = defaultdict(list)
    for e in all_evals:
        skill = e.skill.strip() if e.skill and e.skill.strip() else 'General'
        skill_totals[skill].append(e.score)

    skill_labels, skill_avgs = [], []
    for skill, scores in sorted(skill_totals.items(), key=lambda x: sum(x[1]) / len(x[1])):
        skill_labels.append(skill)
        skill_avgs.append(round(sum(scores) / len(scores), 1))

    recent_sessions = list(reversed(sessions[-8:]))

    return render_template(
        'dashboard.html',
        total_sessions     = total_sessions,
        total_answers      = total_answers,
        avg_score_all      = avg_score_all,
        best_score         = best_score,
        trend_labels       = trend_labels,
        trend_scores       = trend_scores,
        skill_labels       = skill_labels,
        skill_avgs         = skill_avgs,
        recent_sessions    = recent_sessions,
        requests_remaining = current_user.requests_remaining(),
    )
