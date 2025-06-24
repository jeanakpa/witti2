# models/referral.py
from extensions import db
from datetime import datetime

class Referral(db.Model):
    __tablename__ = 'referrals'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    referrer_id = db.Column(db.BigInteger, db.ForeignKey('accounts_account.id'), nullable=False)
    referred_email = db.Column(db.String(255), nullable=False)  # Email de l'ami invité
    referral_code = db.Column(db.String(50), nullable=False, unique=True)  # Code unique de parrainage
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, accepted, rewarded
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    referrer = db.relationship('Account', backref='referrals')

    def to_dict(self):
        return {
            "id": self.id,
            "referrer_id": self.referrer_id,  # Corrigé de referer_id et self.referred_email
            "referred_email": self.referred_email,
            "referral_code": self.referral_code,
            "status": self.status,
            "created_at": self.created_at.isoformat(),  # Format compatible JSON
            "referrer": {
                "id": self.referrer.id,
                "identifiant": self.referrer.identifiant,
                "email": self.referrer.email
            } if self.referrer else None
        }

    def __repr__(self):
        return f"<Referral referrer_id={self.referrer_id} referred_email={self.referred_email} status={self.status}>"