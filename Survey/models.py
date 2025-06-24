from extensions import db
from datetime import datetime

class Survey(db.Model):
    __tablename__ = 'surveys'
    id = db.Column(db.BigInteger, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Survey {self.id} - {self.title}>"

class SurveyOption(db.Model):
    __tablename__ = 'survey_options'
    id = db.Column(db.BigInteger, primary_key=True)
    survey_id = db.Column(db.BigInteger, db.ForeignKey('surveys.id'), nullable=False)
    option_text = db.Column(db.String(50), nullable=False)  # "Très mal", "Mal", etc.
    option_value = db.Column(db.Integer, nullable=False)  # 1, 2, ..., 5
    survey = db.relationship('Survey', backref='options')

    def __repr__(self):
        return f"<SurveyOption {self.option_value} - {self.option_text}>"

class SurveyResponse(db.Model):
    __tablename__ = 'survey_responses'
    id = db.Column(db.BigInteger, primary_key=True)
    survey_id = db.Column(db.BigInteger, db.ForeignKey('surveys.id'), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('accounts_account.id'), nullable=False)
    customer_id = db.Column(db.BigInteger, db.ForeignKey('customer_customers.id'), nullable=False)
    option_id = db.Column(db.BigInteger, db.ForeignKey('survey_options.id'), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    survey = db.relationship('Survey', backref='responses')
    option = db.relationship('SurveyOption', backref='responses')
    customer = db.relationship('Customer', backref='survey_responses')

    def __repr__(self):
        return f"<SurveyResponse {self.id} - Survey {self.survey_id}>"