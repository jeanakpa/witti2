# admin/resources/stock.py (corrigé)
from flask import request
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Lot.models import Stock
from Account.models import Account
from extensions import db
from datetime import datetime
from Admin.views import api  # Correction de "Admin" à "admin"
from sqlalchemy.exc import IntegrityError

stock_model = api.model('Stock', {
    'id': fields.Integer(description='Stock ID'),
    'reward_id': fields.Integer(description='Reward ID'),
    'quantity_available': fields.Integer(description='Quantity Available'),
    'last_updated': fields.String(description='Last Updated')
})

stock_input_model = api.model('StockInput', {
    'reward_id': fields.Integer(required=True, description='Reward ID'),
    'quantity_available': fields.Integer(required=True, description='Quantity Available')
})

class StockList(Resource):
    @jwt_required()
    @api.marshal_with(stock_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        stocks = Stock.query.all()
        return [stock.to_dict() for stock in stocks]

    @jwt_required()
    @api.expect(stock_input_model)
    @api.marshal_with(stock_model, code=201)
    def post(self):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not user.is_superuser:
            api.abort(403, "Seuls les super admins peuvent ajouter du stock")
        data = request.get_json()
        reward_id = data['reward_id']
        quantity_available = data['quantity_available']

        # Vérifie si un stock existe déjà pour ce reward_id
        stock = Stock.query.filter_by(reward_id=reward_id).first()
        if stock:
            # Met à jour la quantité existante
            stock.quantity_available = quantity_available
            stock.last_updated = datetime.utcnow()
            db.session.commit()
            return stock.to_dict(), 200  # Code 200 pour une mise à jour
        else:
            # Crée un nouveau stock si aucun n'existe
            new_stock = Stock(reward_id=reward_id, quantity_available=quantity_available)
            try:
                db.session.add(new_stock)
                db.session.commit()
                return new_stock.to_dict(), 201
            except IntegrityError as e:
                db.session.rollback()
                api.abort(400, f"Erreur d'intégrité : {str(e)}")

class StockDetail(Resource):
    @jwt_required()
    @api.marshal_with(stock_model)
    def put(self, stock_id):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not user.is_superuser:
            api.abort(403, "Seuls les super admins peuvent modifier le stock")
        stock = Stock.query.get_or_404(stock_id)
        data = request.get_json()
        stock.quantity_available = data.get('quantity_available', stock.quantity_available)
        stock.last_updated = datetime.utcnow()
        db.session.commit()
        return stock.to_dict()

    @jwt_required()
    def delete(self, stock_id):
        user_id = get_jwt_identity()  # Retourne 'identifiant' (ex: 'superadmin_001')
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not user.is_superuser:
            api.abort(403, "Seuls les super admins peuvent supprimer le stock")
        stock = Stock.query.get_or_404(stock_id)
        db.session.delete(stock)
        db.session.commit()
        return {"message": "Stock supprimée avec succès"}, 200