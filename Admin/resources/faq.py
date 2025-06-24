# admin/resources/faq.py (adapté)
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Faq.models import FAQ
from Account.models import Account
from extensions import db
from Admin.views import api  # Correction de "Admin" à "admin"
from flask import request

faq_model = api.model('FAQ', {
    'id': fields.Integer(description='FAQ ID'),
    'question': fields.String(description='Question'),
    'answer': fields.String(description='Answer')
})

faq_input_model = api.model('FAQInput', {
    'question': fields.String(required=True, description='Question'),
    'answer': fields.String(required=True, description='Answer')
})

class FAQList(Resource):
    @jwt_required()
    @api.marshal_with(faq_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        faqs = FAQ.query.all()
        return [faq.to_dict() for faq in faqs]

    @jwt_required()
    @api.expect(faq_input_model)
    @api.marshal_with(faq_model, code=201)
    def post(self):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not user.is_superuser:
            api.abort(403, "Seuls les super admins peuvent créer des FAQs")
        data = request.get_json()
        faq = FAQ(question=data['question'], answer=data['answer'])
        db.session.add(faq)
        db.session.commit()
        return faq.to_dict()

class FAQDetail(Resource):
    @jwt_required()
    @api.marshal_with(faq_model)
    def get(self, faq_id):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        faq = FAQ.query.get_or_404(faq_id)
        return faq.to_dict()

    @jwt_required()
    @api.expect(faq_input_model)
    @api.marshal_with(faq_model)
    def put(self, faq_id):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not user.is_superuser:
            api.abort(403, "Seuls les super admins peuvent modifier des FAQs")
        faq = FAQ.query.get_or_404(faq_id)
        data = request.get_json()
        faq.question = data['question']
        faq.answer = data['answer']
        db.session.commit()
        return faq.to_dict()

    @jwt_required()
    def delete(self, faq_id):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not user.is_superuser:
            api.abort(403, "Seuls les super admins peuvent supprimer des FAQs")
        faq = FAQ.query.get_or_404(faq_id)
        db.session.delete(faq)
        db.session.commit()
        return {"message": "FAQ supprimée avec succès"}, 200