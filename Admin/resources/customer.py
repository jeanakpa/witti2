# admin/resources/customer.py
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Customer.models import Customer
from Account.models import Account
from Admin.views import api

customer_model = api.model('Customer', {
    'id': fields.Integer(description='Customer ID'),
    'customer_code': fields.String(description='Customer Code'),
    'short_name': fields.String(description='Short Name'),
    'first_name': fields.String(description='First Name'),
    'gender': fields.String(description='Gender'),
    'birth_date': fields.String(description='Birth Date'),
    'phone_number': fields.String(description='Phone Number'),
    'street': fields.String(description='Street'),
    'total': fields.Integer(description='Total'),
    'solde': fields.Integer(description='Solde')
})

class CustomerList(Resource):
    @jwt_required()
    @api.marshal_with(customer_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        customers = Customer.query.all()
        return [{
            'id': customer.id,
            'customer_code': customer.customer_code,
            'short_name': customer.short_name,
            'first_name': customer.first_name,
            'gender': customer.gender,
            'birth_date': customer.birth_date,
            'phone_number': customer.phone_number,
            'street': customer.street,
            'total': customer.total,
            'solde': customer.solde
        } for customer in customers]