from flask import Blueprint, current_app, request, jsonify
from flask_restx import Api, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from datetime import datetime
from Lot.models import Recompense, Favorite, CartItem, Stock, Order, Notification
from Account.models import Account
from Customer.models import Customer
import uuid

lot_bp = Blueprint('lot', __name__, url_prefix='/lot')
api = Api(lot_bp, version='1.0', title='Lot API', description='API for lot and reward operations')

# Define category ranges for rewards
CATEGORIES = [
    {"name": "Eco Premium", "min": 0, "max": 100},
    {"name": "Executive", "min": 101, "max": 1000},
    {"name": "Executive +", "min": 1001, "max": 3000},
    {"name": "First Class", "min": 3001, "max": float('inf')}
]

# Define response models for rewards
reward_model = api.model('Reward', {
    'id': fields.Integer(description='Reward ID'),
    'title': fields.String(description='Reward title'),
    'tokens_required': fields.Integer(description='Tokens required'),
    'category': fields.String(description='Reward category'),
    'image_url': fields.String(description='Image URL')
})

favorites_response_model = api.model('FavoritesResponse', {
    'count': fields.Integer(description='Number of favorites'),
    'items': fields.List(fields.Nested(reward_model), description='List of favorite rewards')
})

cart_item_model = api.model('CartItem', {
    'id': fields.Integer(description='Reward ID'),
    'title': fields.String(description='Reward title'),
    'quantity': fields.Integer(description='Quantity'),
    'tokens_required_per_item': fields.Integer(description='Tokens required per item'),
    'total_tokens': fields.Integer(description='Total tokens for this item'),
    'image_url': fields.String(description='Image URL'),
    'transaction_id': fields.String(description='Transaction ID')
})

cart_response_model = api.model('CartResponse', {
    'jetons_disponibles': fields.Integer(description='Available tokens'),
    'jetons_requis': fields.Integer(description='Required tokens'),
    'achat_possible': fields.Boolean(description='Purchase possible'),
    'transactions': fields.List(fields.Nested(cart_item_model), description='Cart items'),
    'notifications': fields.List(fields.String, description='Messages')
})

order_model = api.model('Order', {
    'id': fields.String(description='Order ID'),
    'customer': fields.String(description='Customer name'),
    'contact': fields.String(description='Contact number'),
    'date': fields.String(description='Order date'),
    'heure': fields.String(description='Order time'),
    'amount': fields.Float(description='Total amount in tokens'),
    'status': fields.String(description='Order status'),
    'item': fields.String(description='Reward title'),
    'quantity': fields.Integer(description='Quantity'),
    'messages': fields.List(fields.String, description='Order messages')
})

orders_response_model = api.model('OrdersResponse', {
    'msg': fields.String(description='Success message'),
    'orders': fields.List(fields.Nested(order_model), description='List of orders')
})

@api.route('/rewards', methods=['GET'])
class ListRewards(Resource):
    @jwt_required()
    @api.marshal_with(reward_model, as_list=True)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        # Get all rewards
        rewards = Recompense.query.all()
        requested_category = request.args.get('category')

        # Assign category to each reward based on tokens (jeton)
        rewards_with_category = []
        for r in rewards:
            jeton = r.jeton
            category = None
            for cat in CATEGORIES:
                if cat['min'] <= jeton <= cat['max']:
                    category = cat['name']
                    break
            rewards_with_category.append({
                "id": r.id,
                "title": r.libelle,
                "tokens_required": r.jeton,
                "category": category,
                "image_url": r.recompense_image if r.recompense_image else None
            })

        # Sort rewards by category
        rewards_with_category.sort(key=lambda x: x['category'] or '')

        # Filter by category if requested
        if requested_category:
            filtered_rewards = [r for r in rewards_with_category if r['category'] == requested_category]
        else:
            filtered_rewards = rewards_with_category

        current_app.logger.info(f"Rewards retrieved for user {user_id}, requested category: {requested_category}, total: {len(filtered_rewards)}")
        return filtered_rewards

@api.route('/rewards/<int:reward_id>/favorite', methods=['POST'])
class ToggleFavorite(Resource):
    @jwt_required()
    def post(self, reward_id):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        # Check if the reward exists
        reward = Recompense.query.get(reward_id)
        if not reward:
            api.abort(404, "Récompense non trouvée")

        # Check if already favorited
        favorite = Favorite.query.filter_by(user_id=user.id, reward_id=reward_id).first()
        if favorite:
            db.session.delete(favorite)
            db.session.commit()
            return jsonify({"msg": "Récompense retirée des favoris"})
        else:
            new_favorite = Favorite(user_id=user.id, reward_id=reward_id)
            db.session.add(new_favorite)
            db.session.commit()
            return jsonify({"msg": "Récompense ajoutée aux favoris"})

@api.route('/favorites', methods=['GET'])
class GetFavorites(Resource):
    @jwt_required()
    @api.marshal_with(favorites_response_model)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        favorites = Favorite.query.filter_by(user_id=user.id).all()
        favorite_rewards = []
        for fav in favorites:
            reward = Recompense.query.get(fav.reward_id)
            if reward:
                favorite_rewards.append({
                    "id": reward.id,
                    "title": reward.libelle,
                    "tokens_required": reward.jeton,
                    "category": next((cat['name'] for cat in CATEGORIES if cat['min'] <= reward.jeton <= cat['max']), None),
                    "image_url": reward.recompense_image if reward.recompense_image else None
                })

        return {"count": len(favorite_rewards), "items": favorite_rewards}

@api.route('/cart', methods=['POST'])
class AddToCart(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        data = request.get_json()
        reward_id = data.get('reward_id')
        quantity = data.get('quantity', 1)

        # Validate input
        if not reward_id or quantity <= 0:
            api.abort(400, "ID de récompense et quantité valides requis")

        # Check if reward exists
        reward = Recompense.query.get(reward_id)
        if not reward:
            api.abort(404, "Récompense non trouvée")

        # Check stock
        stock = Stock.query.filter_by(reward_id=reward_id).first()
        if not stock or stock.quantity_available < quantity:
            api.abort(400, "Quantité insuffisante en stock")

        # Check if item is already in cart
        cart_item = CartItem.query.filter_by(user_id=user.id, reward_id=reward_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(user_id=user.id, reward_id=reward_id, quantity=quantity)
            db.session.add(cart_item)

        stock.quantity_available -= quantity
        db.session.commit()

        return jsonify({
            "msg": "Récompense ajoutée au panier",
            "quantity": cart_item.quantity,
            "total_tokens": cart_item.quantity * reward.jeton
        })

@api.route('/cart', methods=['GET'])
class ViewCart(Resource):
    @jwt_required()
    @api.marshal_with(cart_response_model)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        transactions = []
        total_required = 0
        # Récupérer le client associé à l'utilisateur via customer_code
        customer = Customer.query.filter_by(customer_code=user_id).first()
        jetons_disponibles = customer.solde if customer else 0

        for item in cart_items:
            reward = Recompense.query.get(item.reward_id)
            if reward:
                transaction = {
                    "id": item.id,
                    "title": reward.libelle,
                    "quantity": item.quantity,
                    "tokens_required_per_item": reward.jeton,
                    "total_tokens": item.quantity * reward.jeton,
                    "image_url": reward.recompense_image if reward.recompense_image else None,
                    "transaction_id": str(uuid.uuid4())
                }
                transactions.append(transaction)
                total_required += item.quantity * reward.jeton

        achat_possible = jetons_disponibles >= total_required
        notifications = ["Vérifiez vos jetons disponibles avant l'achat."] if not achat_possible else []

        return {
            "jetons_disponibles": jetons_disponibles,
            "jetons_requis": total_required,
            "achat_possible": achat_possible,
            "transactions": transactions,
            "notifications": notifications
        }

@api.route('/place-order', methods=['POST'])
class PlaceOrder(Resource):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user:
            api.abort(404, "Utilisateur non trouvé")

        # Récupérer le client associé à l'utilisateur via customer_code
        customer = Customer.query.filter_by(customer_code=user_id).first()
        if not customer:
            api.abort(404, "Client non trouvé")

        cart_items = CartItem.query.filter_by(user_id=user.id).all()
        if not cart_items:
            api.abort(400, "Panier vide")

        total_amount = 0
        for item in cart_items:
            reward = Recompense.query.get(item.reward_id)
            if reward:
                total_amount += item.quantity * reward.jeton

        # Create order without debiting tokens
        order = Order(user_id=user.id, customer_id=customer.id, amount=total_amount, contact="N/A")
        db.session.add(order)

        # Clear cart without debiting or updating stock (handled during validation)
        for item in cart_items:
            db.session.delete(item)
        db.session.commit()

        # Add notification
        notification = Notification(user_id=user.id, message=f"Commande #{order.id} passée avec succès pour {total_amount} jetons (en attente de validation).")
        db.session.add(notification)
        db.session.commit()

        return jsonify({
            "msg": "Commande passée avec succès (en attente de validation)",
            "order_id": order.id,
            "amount": total_amount,
            "status": order.status
        })