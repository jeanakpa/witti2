from extensions import db

class CustomerAccount(db.Model):
    __tablename__ = 'customer_customer_account'
    id = db.Column(db.BigInteger, primary_key=True)
    account_number = db.Column(db.String(30), nullable=False)
    customer_code = db.Column(db.String(20), nullable=False)
    working_balance = db.Column(db.BigInteger)

    def __repr__(self):
        return f"<CustomerAccount {self.account_number} - {self.customer_code}>" 