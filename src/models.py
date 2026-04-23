from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, date
import json
import bcrypt

db = SQLAlchemy()


# ── USER ──────────────────────────────────────────────────────────────────────

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash   = db.Column(db.String(200), nullable=False)
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)

    # Rate limiting
    requests_today      = db.Column(db.Integer, default=0)
    last_request_date   = db.Column(db.Date, default=date.today)

    # Plan: 'free' | 'pro'
    plan = db.Column(db.String(20), default='free')

    sessions = db.relationship('InterviewSession', backref='user', lazy=True,
                                cascade='all, delete-orphan')

    FREE_DAILY_LIMIT = 10
    PRO_DAILY_LIMIT  = 100

    def set_password(self, raw_password: str):
        self.password_hash = bcrypt.hashpw(
            raw_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.checkpw(
            raw_password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def daily_limit(self) -> int:
        return self.PRO_DAILY_LIMIT if self.plan == 'pro' else self.FREE_DAILY_LIMIT

    def reset_if_new_day(self):
        today = date.today()
        if self.last_request_date != today:
            self.requests_today    = 0
            self.last_request_date = today

    def can_make_request(self) -> bool:
        self.reset_if_new_day()
        return self.requests_today < self.daily_limit()

    def consume_request(self):
        self.reset_if_new_day()
        self.requests_today += 1

    def requests_remaining(self) -> int:
        self.reset_if_new_day()
        return max(0, self.daily_limit() - self.requests_today)

    def __repr__(self):
        return f'<User {self.email}>'


# ── INTERVIEW SESSION ─────────────────────────────────────────────────────────

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'

    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    job_title           = db.Column(db.String(200), nullable=False, default='Unknown Role')
    resume_snippet      = db.Column(db.String(300), nullable=False, default='')
    created_at          = db.Column(db.DateTime, default=datetime.utcnow)
    total_questions     = db.Column(db.Integer, default=7)
    answered_questions  = db.Column(db.Integer, default=0)
    average_score       = db.Column(db.Float, default=0.0)
    _scores             = db.Column('scores', db.Text, default='[]')
    _questions          = db.Column('questions', db.Text, default='{}')

    evaluations = db.relationship('Evaluation', backref='session', lazy=True,
                                   cascade='all, delete-orphan')

    @property
    def scores(self):
        return json.loads(self._scores)

    @scores.setter
    def scores(self, value):
        self._scores = json.dumps(value)

    @property
    def questions(self):
        return json.loads(self._questions)

    @questions.setter
    def questions(self, value):
        self._questions = json.dumps(value)

    def update_stats(self):
        evals = Evaluation.query.filter_by(session_id=self.id).all()
        self.answered_questions = len(evals)
        if evals:
            self.average_score = round(sum(e.score for e in evals) / len(evals), 1)
            self.scores = [e.score for e in evals]
        db.session.commit()

    def to_dict(self):
        return {
            'id':                  self.id,
            'job_title':           self.job_title,
            'resume_snippet':      self.resume_snippet,
            'created_at':          self.created_at.strftime('%b %d, %Y %I:%M %p'),
            'total_questions':     self.total_questions,
            'answered_questions':  self.answered_questions,
            'average_score':       self.average_score,
            'scores':              self.scores,
        }


# ── EVALUATION ────────────────────────────────────────────────────────────────

class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id              = db.Column(db.Integer, primary_key=True)
    session_id      = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False, index=True)
    question        = db.Column(db.Text, nullable=False)
    answer          = db.Column(db.Text, nullable=False)
    score           = db.Column(db.Float, nullable=False)
    feedback        = db.Column(db.Text, nullable=False)
    question_type   = db.Column(db.String(20), default='technical')
    skill           = db.Column(db.String(100), default='')
    difficulty      = db.Column(db.String(20), default='medium')
    created_at      = db.Column(db.DateTime, default=datetime.utcnow)
    _full_result    = db.Column('full_result', db.Text, default='{}')

    @property
    def full_result(self):
        return json.loads(self._full_result)

    @full_result.setter
    def full_result(self, value):
        self._full_result = json.dumps(value)
