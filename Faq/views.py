from flask import Blueprint
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Faq.models import FAQ

faq_bp = Blueprint('faq', __name__, url_prefix='/faq')
api = Api(faq_bp, version='1.0', title='FAQ API', description='API for FAQ operations')

# Define response model for FAQ
faq_model = api.model('FAQ', {
    'id': fields.Integer(description='FAQ ID'),
    'question': fields.String(description='FAQ question'),
    'answer': fields.String(description='FAQ answer')
})

faq_response_model = api.model('FAQResponse', {
    'msg': fields.String(description='Success message'),
    'faqs': fields.List(fields.Nested(faq_model), description='List of FAQs')
})

@api.route('')
class FAQList(Resource):
    @jwt_required()
    @api.marshal_with(faq_response_model)
    def get(self):
        faqs = FAQ.query.all()
        faqs_data = [{
            "id": faq.id,
            "question": faq.question,
            "answer": faq.answer
        } for faq in faqs]
        return {
            "msg": "FAQ récupérées avec succès",
            "faqs": faqs_data
        }, 200
    
