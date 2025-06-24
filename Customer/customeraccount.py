from extensions import db

class CustomerCustomerAccount(db.Model):
    __tablename__ = 'customer_customeraccount'
    id = db.Column(db.BigInteger, primary_key=True)
    customer = db.Column(db.String(255))
    agence = db.Column(db.Text)
    account = db.Column(db.String(255))
    libelle = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f"<CustomerCustomerAccount {self.customer} - {self.account}>" 