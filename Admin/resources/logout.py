# admin/resources/logout.py
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Account.models import Account
from Models.token_blacklist import TokenBlacklist
from extensions import db
from flask import current_app
from Admin.views import api  # Importer l'instance 'api' depuis views.py

logout_response_model = api.model('LogoutResponse', {
    'msg': fields.String(description='Logout message')
})

class AdminLogout(Resource):
    @jwt_required()
    @api.marshal_with(logout_response_model)
    def post(self):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            return {"msg": "Utilisateur non autorisé"}, 403
        try:
            jti = get_jwt()['jti']
            blacklisted_token = TokenBlacklist(jti=jti)
            db.session.add(blacklisted_token)
            db.session.commit()
            current_app.logger.info(f"Admin {admin_identifiant} logged out successfully, token JTI {jti} blacklisted")
            return {"msg": "Déconnexion réussie"}, 200
        except Exception as e:
            current_app.logger.error(f"Error during admin logout: {str(e)}")
            return {"error": str(e)}, 500