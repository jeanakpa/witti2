# Account/views.py
from datetime import datetime
from flask import Blueprint, request, current_app
from flask_restx import Api, Resource, fields
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash
from Account.models import Account
from Models.referral import Referral
from Customer.models import Customer
from extensions import db

# Définir le blueprint une seule fois
accounts_bp = Blueprint('accounts', __name__)
api = Api(accounts_bp, doc='/doc/', version='1.0', title='Accounts API', description='API for account operations')

# Modèle pour la connexion
login_model = api.model('Login', {
    'identifiant': fields.String(required=True, description='User identifier'),
    'password': fields.String(required=True, description='User password')
})

# Modèle pour la connexion admin
admin_login_model = api.model('AdminLogin', {
    'email': fields.String(required=True, description='Admin email'),
    'password': fields.String(required=True, description='Admin password')
})

# Modèle pour l'inscription via parrainage
signup_model = api.model('Signup', {
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'identifiant': fields.String(required=True),
    'password': fields.String(required=True)
})

# Modèles de réponse
login_response_model = api.model('LoginResponse', {
    'access_token': fields.String(description='JWT access token')
})

admin_login_response_model = api.model('AdminLoginResponse', {
    'access_token': fields.String(description='JWT access token'),
    'role': fields.String(description='Admin role'),
    'name': fields.String(description='Admin name'),
    'email': fields.String(description='Admin email')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.marshal_with(login_response_model)
    def post(self):
        data = api.payload
        identifiant = data.get('identifiant')
        password = data.get('password')

        try:
            user = db.session.query(Account).filter_by(identifiant=identifiant).first()
            if not user:
                current_app.logger.warning(f"Login failed: User with identifiant {identifiant} not found")
                return {"message": "Invalid identifiant or password"}, 401

            if not user.check_password(password):
                current_app.logger.warning(f"Login failed: Incorrect password for identifiant {identifiant}")
                return {"message": "Invalid identifiant or password"}, 401

            access_token = create_access_token(identity=identifiant)
            current_app.logger.info(f"User {identifiant} logged in successfully")
            return {"access_token": access_token}, 200

        except Exception as e:
            current_app.logger.error(f"Error during login: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/admin/login')
class AdminLogin(Resource):
    @api.expect(admin_login_model)
    @api.marshal_with(admin_login_response_model)
    def post(self):
        data = api.payload
        email = data.get('email')
        password = data.get('password')

        try:
            admin = db.session.query(Account).filter_by(email=email).first()
            if not admin:
                current_app.logger.warning(f"Admin login failed: User with email {email} not found")
                return {"message": "Invalid email or password"}, 401

            if not admin.check_password(password):
                current_app.logger.warning(f"Admin login failed: Incorrect password for email {email}")
                return {"message": "Invalid email or password"}, 401

            # Vérifier si l'utilisateur est un admin ou super admin
            if not (admin.is_admin or admin.is_superuser):
                current_app.logger.warning(f"Admin login failed: User {email} is not an admin")
                return {"message": "User is not an admin"}, 403

            access_token = create_access_token(identity=admin.identifiant)
            current_app.logger.info(f"Admin {email} logged in successfully")
            return {
                "access_token": access_token,
                "role": "super_admin" if admin.is_superuser else "admin",
                "name": f"{admin.first_name} {admin.last_name}",
                "email": admin.email
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error during admin login: {str(e)}")
            return {"error": str(e)}, 500



