from extensions import db

class CategClient(db.Model):
    __tablename__ = 'categ_client'
    id = db.Column(db.BigInteger, primary_key=True)
    customer_code = db.Column(db.String(50))
    category = db.Column(db.String(100))

    def __repr__(self):
        return f"<CategClient {self.customer_code} - {self.category}>" 