# admin/resources/profile.py
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Account.models import Account
from Admin.views import api

admin_profile_model = api.model('AdminProfile', {
    'id': fields.Integer(description='Admin ID'),
    'first_name': fields.String(description='First Name'),
    'last_name': fields.String(description='Last Name'),
    'email': fields.String(description='Email'),
    'identifiant': fields.String(description='Identifiant'),
    'is_admin': fields.Boolean(description='Is Admin'),
    'is_superuser': fields.Boolean(description='Is Superuser'),
    'date_joined': fields.String(description='Date Joined'),
    'last_login': fields.String(description='Last Login')
})

class AdminProfile(Resource):
    @jwt_required()
    @api.marshal_with(admin_profile_model)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        return {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'identifiant': user.identifiant,
            'is_admin': user.is_admin,
            'is_superuser': user.is_superuser,
            'date_joined': str(user.date_joined),
            'last_login': str(user.last_login)
        }