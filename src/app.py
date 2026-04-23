import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_login import LoginManager

from models import db, User
from extensions import csrf


def create_app(config_object=None):
    """Application factory. Pass a config object for testing."""
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    if config_object is None:
        from config import Config
        config_object = Config()

    app.config.from_object(config_object)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view             = 'auth.login'
    login_manager.login_message          = 'Please log in to access InterviewAI.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ── File storage dirs ──────────────────────────────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESUME_FOLDER'], exist_ok=True)

    # ── Blueprints ─────────────────────────────────────────────────────────────
    from auth import auth as auth_blueprint
    from blueprints.main import main as main_blueprint
    from blueprints.interview import interview as interview_blueprint
    from blueprints.history import history as history_blueprint
    from blueprints.api import api as api_blueprint
    from blueprints.profile import profile as profile_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(main_blueprint)
    app.register_blueprint(interview_blueprint)
    app.register_blueprint(history_blueprint)
    app.register_blueprint(api_blueprint)
    app.register_blueprint(profile_blueprint)

    # ── Template globals ───────────────────────────────────────────────────────
    from ai_service import DEMO_MODE

    @app.context_processor
    def inject_globals():
        return {'demo_mode': DEMO_MODE}

    # ── DB bootstrap ───────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
