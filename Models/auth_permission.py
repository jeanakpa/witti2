from extensions import db

class AuthPermission(db.Model):
    __tablename__ = 'auth_permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    content_type_id = db.Column(db.Integer, db.ForeignKey('django_content_type.id'), nullable=False)
    codename = db.Column(db.String(100), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('content_type_id', 'codename', name='auth_permission_content_type_id_codename_01ab375a_uniq'),
    )

    def __repr__(self):
        return f"<AuthPermission {self.name} ({self.codename})>" 