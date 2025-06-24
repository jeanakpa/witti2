from flask import Blueprint, current_app, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Account.models import Account
from Support.models import SupportRequest
from datetime import datetime
import os

support_bp = Blueprint('support', __name__, url_prefix='/support')
api = Api(support_bp, version='1.0', title='Support API', description='API for support operations')

SUPPORT_PHONE = os.getenv('SUPPORT_PHONE', '+2250710922213')
SUPPORT_WHATSAPP = os.getenv('SUPPORT_WHATSAPP', '+2250710922213')
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'misterjohn0798@gmail.com')
WHATSAPP_DEFAULT_MESSAGE = os.getenv('WHATSAPP_DEFAULT_MESSAGE', 'Bonjour, j''ai besoin d''aide avec l''application.')

# Define response model for support contact information
support_contact_model = api.model('SupportContact', {
    'phone': fields.String(description='Support phone number'),
    'whatsapp': fields.String(description='WhatsApp contact link'),
    'email': fields.String(description='Support email address')
})

# Define request model for submitting a support request
support_request_model = api.model('SupportRequest', {
    'subject': fields.String(required=True, description='Subject of the request'),
    'description': fields.String(required=True, description='Description of the issue'),
    'request_type': fields.String(required=True, description='Type of request', enum=['Reclamation', 'Assistance', 'Autre'])
})

# Define response model for support request submission
support_request_response_model = api.model('SupportRequestResponse', {
    'msg': fields.String(description='Success message'),
    'request_id': fields.Integer(description='ID of the submitted request')
})

@api.route('/contact')
class SupportContact(Resource):
    @jwt_required()
    @api.marshal_with(support_contact_model)
    def get(self):
        try:
            identifiant = get_jwt_identity()
            user = db.session.query(Account).filter_by(identifiant=identifiant).first()
            if not user:
                current_app.logger.warning(f"Support contact failed: User with identifiant {identifiant} not found")
                return {"message": "User not found"}, 404

            # Générer le lien WhatsApp
            whatsapp_link = f"https://wa.me/{SUPPORT_WHATSAPP}?text={WHATSAPP_DEFAULT_MESSAGE.replace(' ', '%20')}"

            # Retourner les informations de contact
            contact_info = {
                "phone": SUPPORT_PHONE,
                "whatsapp": whatsapp_link,
                "email": SUPPORT_EMAIL
            }

            current_app.logger.info(f"Support contact information retrieved for user {identifiant}")
            return contact_info, 200

        except Exception as e:
            current_app.logger.error(f"Error retrieving support contact: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/request')
class SupportRequestResource(Resource):
    @jwt_required()
    @api.expect(support_request_model)
    @api.marshal_with(support_request_response_model)
    def post(self):
        try:
            identifiant = get_jwt_identity()
            user = db.session.query(Account).filter_by(identifiant=identifiant).first()
            if not user:
                current_app.logger.warning(f"Support request failed: User with identifiant {identifiant} not found")
                return {"message": "User not found"}, 404

            data = api.payload
            subject = data.get('subject')
            description = data.get('description')
            request_type = data.get('request_type')

            # Valider les champs
            if not subject or not description or not request_type:
                current_app.logger.warning(f"Support request failed: Missing required fields")
                return {"message": "Subject, description, and request type are required"}, 400

            if request_type not in ['Reclamation', 'Assistance', 'Autre']:
                current_app.logger.warning(f"Support request failed: Invalid request type {request_type}")
                return {"message": "Request type must be 'Reclamation', 'Assistance', or 'Autre'"}, 400

            # Créer une nouvelle demande de support
            support_request = SupportRequest(
                user_id=user.id,
                subject=subject,
                description=description,
                request_type=request_type
            )
            db.session.add(support_request)
            db.session.commit()

            current_app.logger.info(f"Support request {support_request.id} submitted by user {identifiant}")
            return {
                "msg": "Demande de support soumise avec succès",
                "request_id": support_request.id
            }, 201

        except Exception as e:
            current_app.logger.error(f"Error submitting support request: {str(e)}")
            return {"error": str(e)}, 500