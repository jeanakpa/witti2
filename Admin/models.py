from extensions import db
from datetime import datetime

class AdminHoneypotLoginAttempt(db.Model):
    __tablename__ = 'admin_honeypot_loginattempt'
    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(255))
    ip_address = db.Column(db.String(50))  # Type inet en SQL, string ici
    session_key = db.Column(db.String(50))
    user_agent = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    path = db.Column(db.Text)

    def __repr__(self):
        return f"<AdminHoneypotLoginAttempt {self.username} @ {self.ip_address}>" 