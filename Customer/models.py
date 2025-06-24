from extensions import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customer_customers'
    id = db.Column(db.BigInteger, primary_key=True)
    customer_code = db.Column(db.String(30), nullable=False, unique=True)
    short_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(30), nullable=False)
    birth_date = db.Column(db.String(30), nullable=False)
    phone_number = db.Column(db.String(100))
    street = db.Column(db.String(100), nullable=False)
    users = db.Column(db.Integer)
    category = db.Column(db.String(30))
    total = db.Column(db.Integer)
    solde = db.Column(db.BigInteger)

    def __repr__(self):
        return f"<Customer {self.customer_code}>"

class Epargne(db.Model):
    __tablename__ = 'customer_epargne'
    solde = db.Column(db.BigInteger, nullable=False)
    client = db.Column(db.Text)
    numero = db.Column(db.String(255))
    libelle = db.Column(db.Text)

    def __repr__(self):
        return f"<Epargne {self.client} - {self.numero}>"

class Transaction(db.Model):
    __tablename__ = 'customer_deposit_withdrawal'
    libelle = db.Column(db.Text)
    code = db.Column(db.Text)
    sens = db.Column(db.Text)
    montant = db.Column(db.Numeric(38, 0))
    deposit_date = db.Column(db.Text)
    compte = db.Column(db.Text)
    client = db.Column(db.Text)

    def __repr__(self):
        return f"<Transaction {self.client} - {self.sens}>"

class SoldeDepotRecurrent(db.Model):
    __tablename__ = 'customer_solde_depotrecurrent'
    id = db.Column(db.BigInteger, primary_key=True)
    client = db.Column(db.String(30), nullable=False)
    numero = db.Column(db.String(30), nullable=False)
    libelle = db.Column(db.String(20), nullable=False)
    solde = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<SoldeDepotRecurrent {self.client} - {self.numero} - {self.solde}>"

class Rebours(db.Model):
    __tablename__ = 'customer_rebours'
    id = db.Column(db.BigInteger, primary_key=True)
    customer = db.Column(db.String(50), nullable=False, unique=True)
    jeton = db.Column(db.Integer, nullable=False)
    compte = db.Column(db.Integer, nullable=False)
    jour = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Rebours {self.customer} - {self.jeton}>"

class UnpaidAccount(db.Model):
    __tablename__ = 'customer_unpaid'
    terme = db.Column(db.Text)
    account = db.Column(db.String(255))
    product = db.Column(db.Text)
    code = db.Column(db.String(255))
    client = db.Column(db.Text)
    open_date = db.Column(db.String(10))
    maturity = db.Column(db.String(10))
    engagement = db.Column(db.Text)
    principal = db.Column(db.Text)
    due = db.Column(db.Text)
    overdue = db.Column(db.Integer)

    def __repr__(self):
        return f"<UnpaidAccount {self.client} - {self.account}>"

class CustomerDat(db.Model):
    __tablename__ = 'customer_dat'
    id = db.Column(db.BigInteger, primary_key=True)
    client = db.Column(db.String(30), nullable=False)
    compte = db.Column(db.String(30))
    montant = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<CustomerDat {self.client} - {self.montant}>"

class SoldeCourantEpargne(db.Model):
    __tablename__ = 'customer_solde_courantepargne'
    id = db.Column(db.BigInteger, primary_key=True)
    client = db.Column(db.String(30), nullable=False)
    numero = db.Column(db.String(30), nullable=False)
    libelle = db.Column(db.String(50), nullable=False)
    solde = db.Column(db.BigInteger, nullable=False)
    date = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f"<SoldeCourantEpargne {self.client} - {self.numero} - {self.solde}>"