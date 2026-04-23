from flask import Blueprint, render_template, session as flask_session, current_app
from flask_login import login_required, current_user

from models import InterviewSession

profile = Blueprint('profile', __name__)


@profile.route('/profile')
@login_required
def profile_view():
    total_sessions = InterviewSession.query.filter_by(user_id=current_user.id).count()

    resume_filename = flask_session.get('uploaded_resume_filename')
    import os
    has_resume = bool(
        resume_filename and
        os.path.exists(os.path.join(current_app.config['RESUME_FOLDER'], resume_filename))
    )

    return render_template(
        'profile.html',
        total_sessions     = total_sessions,
        has_resume         = has_resume,
        requests_remaining = current_user.requests_remaining(),
    )
