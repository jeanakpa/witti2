# Admin/resources/referral.py
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Account.models import Account
from Models.referral import Referral
from Support.models import SupportRequest
from extensions import db

# Définir les modèles sans dépendre de l'api
ns = None  # L'espace de noms sera défini dans views.py

referral_model = {
    'id': fields.Integer(description='ID du parrainage'),
    'referrer_id': fields.Integer(description='ID de l\'utilisateur parrain'),
    'referrer_email': fields.String(description='Email de l\'utilisateur parrain'),
    'referred_email': fields.String(description='Email de l\'ami invité'),
    'referral_link': fields.String(description='Lien de parrainage'),
    'status': fields.String(description='Statut du parrainage'),
    'created_at': fields.DateTime(description='Date de création')
}

update_status_model = {
    'status': fields.String(required=True, description='Nouveau statut (pending, accepted, rewarded)')
}

class ReferralManagementResource(Resource):
    @jwt_required()
    def get(self):
        # Récupérer l'utilisateur connecté
        identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=identifiant).first()
        if not admin:
            return {'message': 'Utilisateur non trouvé'}, 404

        # Vérifier si l'utilisateur est un admin ou super admin
        if not (admin.is_admin or admin.is_superuser):
            return {'message': 'Accès réservé aux administrateurs'}, 403

        # Récupérer tous les parrainages
        referrals = Referral.query.all()
        referral_data = [{
            'id': referral.id,
            'referrer_id': referral.referrer_id,
            'referrer_email': referral.referrer.email if referral.referrer else 'N/A',
            'referred_email': referral.referred_email,
            'referral_link': f"http://127.0.0.1:5000/accounts/refer/{referral.referral_code}",
            'status': referral.status,
            'created_at': referral.created_at.isoformat()
        } for referral in referrals]

        return {
            'referrals': referral_data
        }, 200

    @jwt_required()
    def put(self, referral_id):
        # Récupérer l'utilisateur connecté
        identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=identifiant).first()
        if not admin:
            return {'message': 'Utilisateur non trouvé'}, 404

        # Vérifier si l'utilisateur est un admin ou super admin
        if not (admin.is_admin or admin.is_superuser):
            return {'message': 'Accès réservé aux administrateurs'}, 403

        # Récupérer le parrainage
        referral = Referral.query.get(referral_id)
        if not referral:
            return {'message': 'Parrainage non trouvé'}, 404

        # Mettre à jour le statut
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ['pending', 'accepted', 'rewarded']:
            return {'message': 'Statut invalide'}, 400

        referral.status = new_status
        db.session.commit()

        return {'message': 'Statut mis à jour avec succès'}, 200

    @jwt_required()
    def delete(self, referral_id):
        # Récupérer l'utilisateur connecté
        identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=identifiant).first()
        if not admin:
            return {'message': 'Utilisateur non trouvé'}, 404

        # Vérifier si l'utilisateur est un admin ou super admin
        if not (admin.is_admin or admin.is_superuser):
            return {'message': 'Accès réservé aux administrateurs'}, 403

        # Récupérer le parrainage
        referral = Referral.query.get(referral_id)
        if not referral:
            return {'message': 'Parrainage non trouvé'}, 404

        # Supprimer le parrainage
        db.session.delete(referral)
        db.session.commit()

        return {'message': 'Parrainage supprimé avec succès'}, 200