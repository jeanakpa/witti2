from extensions import db

class CustomerCustomerAccount1(db.Model):
    __tablename__ = 'customer_customeraccount_1'
    id = db.Column(db.BigInteger, primary_key=True)
    customer = db.Column(db.String(255))
    agence = db.Column(db.Text)
    account = db.Column(db.String(255))
    libelle = db.Column(db.Text)

    def __repr__(self):
        return f"<CustomerCustomerAccount1 {self.customer} - {self.account}>" 