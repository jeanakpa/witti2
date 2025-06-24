# admin/resources/admin.py (corrigé)
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Account.models import Account
from Admin.views import api  # Correction de "Admin" à "admin"

admin_model = api.model('Admin', {
    'id': fields.Integer(description='Admin ID'),
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'email': fields.String(description='Email'),
    'identifiant': fields.String(description='Identifiant'),
    'is_admin': fields.Boolean(description='Is Admin'),
    'is_superuser': fields.Boolean(description='Is Superuser')
})

class AdminList(Resource):
    @jwt_required()
    @api.marshal_with(admin_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        admins = Account.query.filter((Account.is_admin == True) | (Account.is_superuser == True)).all()
        return [{
            'id': admin.id,
            'first_name': admin.first_name,
            'last_name': admin.last_name,
            'email': admin.email,
            'identifiant': admin.identifiant,
            'is_admin': admin.is_admin,
            'is_superuser': admin.is_superuser
        } for admin in admins]