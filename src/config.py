import os


class Config:
    """Production config. Reads from environment variables."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

    def __init__(self):
        secret = os.environ.get('SECRET_KEY', '').strip()
        if not secret:
            raise RuntimeError(
                "SECRET_KEY is not set.\n"
                "Add it to your .env file:\n"
                "  SECRET_KEY=<random-string>\n"
                "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        self.SECRET_KEY = secret

        db_url = os.environ.get('DATABASE_URL', '').strip()
        # Render.com provides postgres:// but SQLAlchemy requires postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)

        basedir = os.path.abspath(os.path.dirname(__file__))
        self.SQLALCHEMY_DATABASE_URI = db_url or (
            'sqlite:///' + os.path.join(basedir, '..', 'interviews.db')
        )

        self.UPLOAD_FOLDER = os.path.join(basedir, '..', 'static', 'uploads')
        self.RESUME_FOLDER = os.path.join(basedir, '..', 'static', 'resumes')


class TestConfig:
    """In-memory config for pytest. No real DB or secret required."""

    TESTING = True
    SECRET_KEY = 'test-secret-key-not-for-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    WTF_CSRF_ENABLED = False

    import tempfile, os
    _tmp = tempfile.mkdtemp()
    UPLOAD_FOLDER = os.path.join(_tmp, 'uploads')
    RESUME_FOLDER = os.path.join(_tmp, 'resumes')
