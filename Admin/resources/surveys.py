# admin/resources/surveys.py
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Account.models import Account
from Survey.models import Survey, SurveyOption, SurveyResponse
from Customer.models import Customer
from extensions import db
from Admin.views import api

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

survey_input_model = api.model('SurveyInput', {
    'title': fields.String(required=True, description='Survey title'),
    'description': fields.String(description='Survey description'),
    'is_active': fields.Boolean(description='Is survey active?', default=True)
})

survey_response_model = api.model('SurveyResponse', {
    'msg': fields.String(description='Success message'),
    'survey_id': fields.Integer(description='Survey ID')
})

survey_result_model = api.model('SurveyResult', {
    'option_text': fields.String(description='Option text'),
    'option_value': fields.Integer(description='Option value'),
    'percentage': fields.Float(description='Percentage of responses'),
    'count': fields.Integer(description='Number of responses')
})

survey_response_detail_model = api.model('SurveyResponseDetail', {
    'response_id': fields.Integer(description='Response ID'),
    'customer_code': fields.String(description='Customer code'),
    'first_name': fields.String(description='Customer first name'),
    'short_name': fields.String(description='Customer short name'),
    'phone_number': fields.String(description='Customer phone number'),
    'option_text': fields.String(description='Selected option text'),
    'option_value': fields.Integer(description='Selected option value'),
    'submitted_at': fields.String(description='Submission date')
})

class AdminSurveys(Resource):
    @jwt_required()
    @api.expect(survey_input_model)
    @api.marshal_with(survey_response_model, code=201)
    def post(self):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not admin.is_superuser:
            api.abort(403, "Seuls les super admins peuvent créer des sondages")
        data = request.get_json()
        survey = Survey(title=data['title'], description=data.get('description'), is_active=data.get('is_active', True))
        db.session.add(survey)
        db.session.commit()
        options = [
            SurveyOption(survey_id=survey.id, option_text="Très mal", option_value=1),
            SurveyOption(survey_id=survey.id, option_text="Mal", option_value=2),
            SurveyOption(survey_id=survey.id, option_text="Moyen", option_value=3),
            SurveyOption(survey_id=survey.id, option_text="Bien", option_value=4),
            SurveyOption(survey_id=survey.id, option_text="Très bien", option_value=5)
        ]
        db.session.add_all(options)
        db.session.commit()
        return {"msg": "Sondage créé avec succès", "survey_id": survey.id}, 201

    @jwt_required()
    @api.marshal_with(survey_model, as_list=True)
    def get(self):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            api.abort(403, "Utilisateur non autorisé")
        surveys = Survey.query.all()
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

class AdminSurvey(Resource):
    @jwt_required()
    @api.expect(survey_input_model)
    @api.marshal_with(survey_response_model)
    def put(self, survey_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not admin.is_superuser:
            api.abort(403, "Seuls les super admins peuvent modifier des sondages")
        survey = Survey.query.get(survey_id)
        if not survey:
            api.abort(404, "Sondage non trouvé")
        data = request.get_json()
        survey.title = data.get('title', survey.title)
        survey.description = data.get('description', survey.description)
        survey.is_active = data.get('is_active', survey.is_active)
        db.session.commit()
        return {"msg": "Sondage modifié avec succès", "survey_id": survey.id}

    @jwt_required()
    @api.marshal_with(survey_response_model)
    def delete(self, survey_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not admin.is_superuser:
            api.abort(403, "Seuls les super admins peuvent supprimer des sondages")
        survey = Survey.query.get(survey_id)
        if not survey:
            api.abort(404, "Sondage non trouvé")
        SurveyResponse.query.filter_by(survey_id=survey_id).delete()
        SurveyOption.query.filter_by(survey_id=survey_id).delete()
        db.session.delete(survey)
        db.session.commit()
        return {"msg": "Sondage supprimé avec succès", "survey_id": survey_id}

class SurveyResults(Resource):
    @jwt_required()
    @api.marshal_with(survey_result_model, as_list=True)
    def get(self, survey_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            api.abort(403, "Utilisateur non autorisé")
        survey = Survey.query.get(survey_id)
        if not survey:
            api.abort(404, "Sondage non trouvé")
        options = SurveyOption.query.filter_by(survey_id=survey_id).all()
        total_responses = SurveyResponse.query.filter_by(survey_id=survey_id).count()
        results = []
        for option in options:
            response_count = SurveyResponse.query.filter_by(survey_id=survey_id, option_id=option.id).count()
            percentage = (response_count / total_responses * 100) if total_responses > 0 else 0
            results.append({
                'option_text': option.option_text,
                'option_value': option.option_value,
                'percentage': round(percentage, 2),
                'count': response_count
            })
        return results

class SurveyResponses(Resource):
    @jwt_required()
    @api.marshal_with(survey_response_detail_model, as_list=True)
    def get(self, survey_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            api.abort(403, "Utilisateur non autorisé")
        survey = Survey.query.get(survey_id)
        if not survey:
            api.abort(404, "Sondage non trouvé")
        responses = SurveyResponse.query.filter_by(survey_id=survey_id).all()
        response_data = []
        for response in responses:
            customer = Customer.query.get(response.customer_id)
            option = SurveyOption.query.get(response.option_id)
            response_data.append({
                'response_id': response.id,
                'customer_code': customer.customer_code,
                'first_name': customer.first_name,
                'short_name': customer.short_name,
                'phone_number': customer.phone_number,
                'option_text': option.option_text,
                'option_value': option.option_value,
                'submitted_at': str(response.submitted_at)
            })
        return response_data