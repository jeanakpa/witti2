# models/page_visit.py
from extensions import db
from datetime import datetime

class PageVisit(db.Model):
    __tablename__ = 'page_visits'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    path = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('accounts_account.id'), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('Account', backref='page_visits')

    def __repr__(self):
        return f"<PageVisit path={self.path} timestamp={self.timestamp}>"