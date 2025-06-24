from extensions import db

class AuthGroupPermissions(db.Model):
    __tablename__ = 'auth_group_permissions'
    id = db.Column(db.BigInteger, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('auth_group.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('auth_permission.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('group_id', 'permission_id', name='auth_group_permissions_group_id_permission_id_0cd325b0_uniq'),
    )

    def __repr__(self):
        return f"<AuthGroupPermissions group_id={self.group_id} permission_id={self.permission_id}>" 