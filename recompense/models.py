from extensions import db
from Account.models import Account
from Customer.models import Customer
from datetime import datetime

class Recompense(db.Model):
    __tablename__ = 'recompense_recompense'
    id = db.Column(db.BigInteger, primary_key=True)
    libelle = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    recompense_image = db.Column(db.String(100), nullable=False)
    jeton = db.Column(db.BigInteger, nullable=False)

    def __repr__(self):
        return f"<Recompense id={self.id} libelle={self.libelle}>"

class LotClient(db.Model):
    __tablename__ = 'recompense_lotclient'
    id = db.Column(db.BigInteger, primary_key=True)
    client = db.Column(db.String(100), nullable=False)
    jeton = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    recompense_id = db.Column(db.BigInteger, db.ForeignKey('recompense_recompense.id'), nullable=False)

    def __repr__(self):
        return f"<LotClient {self.client} - {self.jeton} - {self.date}>"