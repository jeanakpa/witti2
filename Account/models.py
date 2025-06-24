from extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Account(db.Model):
    __tablename__ = 'accounts_account'
    id = db.Column(db.BigInteger, primary_key=True)
    password = db.Column(db.String(128), nullable=False)  # Correspond à la colonne password NOT NULL
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False)  # UNIQUE retiré pour correspondre à la base
    identifiant = db.Column(db.String(100), nullable=False, unique=True)
    date_joined = db.Column(db.DateTime(timezone=True), nullable=False)
    last_login = db.Column(db.DateTime(timezone=True), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False)
    is_staff = db.Column(db.Boolean, nullable=False)
    is_superuser = db.Column(db.Boolean, nullable=False)

    def set_password(self, password):
        """Hache le mot de passe et le stocke dans password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie si le mot de passe correspond au hash."""
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<Account {self.username}>"