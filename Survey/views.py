from flask import Blueprint, current_app, jsonify, request
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from Survey.models import Survey, SurveyOption, SurveyResponse
from Account.models import Account
from Customer.models import Customer

survey_bp = Blueprint('survey', __name__, url_prefix='/survey')
api = Api(survey_bp, version='1.0', title='Survey API', description='API for survey operations')

survey_model = api.model('Survey', {
    'id': fields.Integer(description='Survey ID'),
    'title': fields.String(description='Survey title'),
    'description': fields.String(description='Survey description'),
    'created_at': fields.String(description='Creation date'),
    'options': fields.List(fields.Nested(api.model('SurveyOption', {
        'id': fields.Integer(description='Option ID'),
        'option_text': fields.String(description='Option text (e.g., Très mal)'),
        'option_value': fields.Integer(description='Option value (1-5)')
    })))
})

survey_response_input_model = api.model('SurveyResponseInput', {
    'option_value': fields.Integer(required=True, description='Value of the selected option (1-5)')
})

survey_response_model = api.model('SurveyResponse', {
    'msg': fields.String(description='Success message'),
    'survey_id': fields.Integer(description='Survey ID'),
    'option_value': fields.Integer(description='Selected option value')
})

@api.route('/surveys')
class ListSurveys(Resource):
    @jwt_required()
    @api.marshal_with(survey_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        surveys = Survey.query.filter_by(is_active=True).all()
        surveys_data = []
        for survey in surveys:
            options = SurveyOption.query.filter_by(survey_id=survey.id).all()
            surveys_data.append({
                'id': survey.id,
                'title': survey.title,
                'description': survey.description,
                'created_at': str(survey.created_at),
                'options': [{'id': opt.id, 'option_text': opt.option_text, 'option_value': opt.option_value} for opt in options]
            })
        return surveys_data

@api.route('/surveys/<int:survey_id>/respond', methods=['POST'])
class RespondToSurvey(Resource):
    @jwt_required()
    @api.expect(survey_response_input_model)
    @api.marshal_with(survey_response_model, code=201)
    def post(self, survey_id):
        user_identifiant = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_identifiant).first()
        if not user:
            current_app.logger.error(f"Utilisateur non trouvé pour identifiant {user_identifiant}")
            api.abort(404, "Utilisateur non trouvé")

        customer = Customer.query.filter_by(customer_code=user_identifiant).first()
        if not customer:
            current_app.logger.error(f"Client non trouvé pour identifiant {user_identifiant}")
            api.abort(404, "Client non trouvé")

        survey = Survey.query.get(survey_id)
        if not survey:
            current_app.logger.error(f"Sondage {survey_id} n'existe pas")
            api.abort(400, "Sondage invalide ou non actif")
        if not survey.is_active:
            current_app.logger.error(f"Sondage {survey_id} est inactif")
            api.abort(400, "Sondage invalide ou non actif")

        data = request.get_json()
        option_value = data.get('option_value')
        if not option_value:
            current_app.logger.error("option_value est manquant dans la requête")
            api.abort(400, "option_value est requis")

        option = SurveyOption.query.filter_by(survey_id=survey_id, option_value=option_value).first()
        if not option:
            current_app.logger.error(f"Option avec valeur {option_value} invalide pour le sondage {survey_id}")
            api.abort(400, "Option invalide")

        # Vérifier si l'utilisateur a déjà répondu
        existing_response = SurveyResponse.query.filter_by(survey_id=survey_id, customer_id=customer.id).first()
        if existing_response:
            current_app.logger.warning(f"Utilisateur {user_identifiant} a déjà répondu au sondage {survey_id}")
            api.abort(400, "Vous avez déjà répondu à ce sondage")

        # Enregistrer la réponse avec user_id
        response = SurveyResponse(
            survey_id=survey_id,
            user_id=user.id,  # Ajout de user_id
            customer_id=customer.id,
            option_id=option.id
        )
        db.session.add(response)
        db.session.commit()
        current_app.logger.info(f"Réponse enregistrée avec succès pour le sondage {survey_id} par {user_identifiant}")

        return {
            'msg': 'Réponse enregistrée avec succès',
            'survey_id': survey_id,
            'option_value': option_value
        }