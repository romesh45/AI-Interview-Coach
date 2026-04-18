from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class InterviewSession(db.Model):
    __tablename__ = 'interview_sessions'

    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(200), nullable=False, default='Unknown Role')
    resume_snippet = db.Column(db.String(300), nullable=False, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    total_questions = db.Column(db.Integer, default=7)
    answered_questions = db.Column(db.Integer, default=0)
    average_score = db.Column(db.Float, default=0.0)
    _scores = db.Column('scores', db.Text, default='[]')

    evaluations = db.relationship('Evaluation', backref='session', lazy=True, cascade='all, delete-orphan')

    @property
    def scores(self):
        return json.loads(self._scores)

    @scores.setter
    def scores(self, value):
        self._scores = json.dumps(value)

    def update_stats(self):
        evals = Evaluation.query.filter_by(session_id=self.id).all()
        self.answered_questions = len(evals)
        if evals:
            self.average_score = round(sum(e.score for e in evals) / len(evals), 1)
            self.scores = [e.score for e in evals]
        db.session.commit()

    def to_dict(self):
        return {
            'id': self.id,
            'job_title': self.job_title,
            'resume_snippet': self.resume_snippet,
            'created_at': self.created_at.strftime('%b %d, %Y %I:%M %p'),
            'total_questions': self.total_questions,
            'answered_questions': self.answered_questions,
            'average_score': self.average_score,
            'scores': self.scores
        }


class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('interview_sessions.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float, nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='technical')
    skill = db.Column(db.String(100), default='')
    difficulty = db.Column(db.String(20), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
