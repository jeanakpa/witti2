from extensions import db

class AuthGroup(db.Model):
    __tablename__ = 'auth_group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)

    def __repr__(self):
        return f"<AuthGroup {self.name}>" 