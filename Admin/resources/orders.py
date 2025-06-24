# admin/resources/orders.py
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Account.models import Account
from Lot.models import Notification, Order, Recompense, CartItem, Stock
from Customer.models import Customer
from extensions import db
from Admin.views import api

order_model = api.model('Order', {
    'id': fields.String(description='Order ID'),
    'user_id': fields.Integer(description='User ID'),
    'customer_id': fields.Integer(description='Customer ID'),
    'amount': fields.Float(description='Total amount in tokens'),
    'status': fields.String(description='Order status'),
    'contact': fields.String(description='Contact number'),
    'date': fields.String(description='Order date'),
    'items': fields.List(fields.Nested(api.model('OrderItem', {
        'reward_id': fields.Integer(description='Reward ID'),
        'libelle': fields.String(description='Reward name'),
        'quantity': fields.Integer(description='Quantity ordered')
    })), description='Items in the order')
})

orders_response_model = api.model('OrdersResponse', {
    'msg': fields.String(description='Success message'),
    'orders': fields.List(fields.Nested(order_model), description='List of orders')
})

order_update_response_model = api.model('OrderUpdateResponse', {
    'msg': fields.String(description='Success message'),
    'status': fields.String(description='Updated order status')
})

class AdminOrders(Resource):
    @jwt_required()
    @api.marshal_with(orders_response_model)
    def get(self):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            return {"msg": "Utilisateur non autorisé"}, 403
        orders = Order.query.all()
        orders_data = []
        for order in orders:
            cart_items = CartItem.query.filter_by(user_id=order.user_id).all()
            items_data = []
            for item in cart_items:
                reward = Recompense.query.get(item.reward_id)
                if reward:
                    items_data.append({
                        'reward_id': reward.id,
                        'libelle': reward.libelle,
                        'quantity': item.quantity
                    })
            orders_data.append({
                'id': str(order.id),
                'user_id': order.user_id,
                'customer_id': order.customer_id,
                'amount': float(order.amount),
                'status': order.status,
                'contact': order.contact if order.contact else "N/A",
                'date': str(order.created_at) if order.created_at else "Unknown",
                'items': items_data
            })
        return {'msg': 'Commandes récupérées avec succès', 'orders': orders_data}

class AdminOrderDetail(Resource):
    @jwt_required()
    @api.marshal_with(order_model)
    def get(self, order_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not (admin.is_admin or admin.is_superuser):
            return {"msg": "Utilisateur non autorisé"}, 403
        order = Order.query.get(order_id)
        if not order:
            return {"msg": "Commande non trouvée"}, 404
        cart_items = CartItem.query.filter_by(user_id=order.user_id).all()
        items_data = []
        for item in cart_items:
            reward = Recompense.query.get(item.reward_id)
            if reward:
                items_data.append({
                    'reward_id': reward.id,
                    'libelle': reward.libelle,
                    'quantity': item.quantity
                })
        order_data = {
            'id': str(order.id),
            'user_id': order.user_id,
            'customer_id': order.customer_id,
            'amount': float(order.amount),
            'status': order.status,
            'contact': order.contact if order.contact else "N/A",
            'date': str(order.created_at) if order.created_at else "Unknown",
            'items': items_data
        }
        return order_data

    @jwt_required()
    def delete(self, order_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not admin.is_superuser:
            return {"msg": "Seuls les super admins peuvent supprimer les commandes"}, 403
        order = Order.query.get(order_id)
        if not order:
            return {"msg": "Commande non trouvée"}, 404
        db.session.delete(order)
        db.session.commit()
        return {"msg": f"Commande {order_id} supprimée avec succès"}, 200

class ValidateOrder(Resource):
    @jwt_required()
    @api.marshal_with(order_update_response_model)
    def put(self, order_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not admin.is_superuser:
            return {"msg": "Seuls les super admins peuvent valider les commandes"}, 403
        order = Order.query.get(order_id)
        if not order:
            return {"msg": "Commande non trouvée"}, 404
        if order.status == 'cancelled':
            return {"msg": "Une commande annulée ne peut pas être validée"}, 400
        if order.status == 'validated':
            return {"msg": "La commande est déjà validée"}, 400
        cart_items = CartItem.query.filter_by(user_id=order.user_id).all()
        for item in cart_items:
            stock = Stock.query.filter_by(reward_id=item.reward_id).first()
            if not stock or stock.quantity_available < item.quantity:
                order.status = 'cancelled'
                db.session.commit()
                customer = Customer.query.get(order.customer_id)
                reward = Recompense.query.get(item.reward_id)
                notification_user = Notification(user_id=order.user_id, message=f"Votre commande {order.id} a été annulée car l'article {reward.libelle} n'est pas disponible en stock.")
                notification_admin = Notification(user_id=admin.id, message=f"La commande {order.id} a été annulée car l'article {reward.libelle} n'est pas disponible en stock.")
                db.session.add_all([notification_user, notification_admin])
                db.session.commit()
                return {"msg": f"Commande {order_id} annulée car stock insuffisant", "status": order.status}, 200
        order.status = 'validated'
        customer = Customer.query.get(order.customer_id)
        if customer.solde < order.amount:
            return {"msg": "Solde insuffisant pour le client"}, 400
        customer.solde -= order.amount
        customer.total = customer.solde
        for item in cart_items:
            stock = Stock.query.filter_by(reward_id=item.reward_id).first()
            stock.quantity_available -= item.quantity
        customer_name = f"{customer.first_name} {customer.short_name}"
        total_items = len(cart_items)
        item_details = ", ".join([f"{item.quantity} x {Recompense.query.get(item.reward_id).libelle}" for item in cart_items])
        notification_user = Notification(user_id=order.user_id, message=f"Votre commande {order.id} de {total_items} article(s) ({item_details}) a été validée. Passez en agence pour la récupérer.")
        notification_admin = Notification(user_id=admin.id, message=f"La commande {order.id} de {customer_name} pour {total_items} article(s) ({item_details}) a été validée.")
        db.session.add_all([notification_user, notification_admin])
        db.session.commit()
        return {"msg": f"Commande {order_id} validée avec succès", "status": order.status}

class CancelOrder(Resource):
    @jwt_required()
    @api.marshal_with(order_update_response_model)
    def put(self, order_id):
        admin_identifiant = get_jwt_identity()
        admin = Account.query.filter_by(identifiant=admin_identifiant).first()
        if not admin or not admin.is_superuser:
            return {"msg": "Seuls les super admins peuvent annuler les commandes"}, 403
        order = Order.query.get(order_id)
        if not order:
            return {"msg": "Commande non trouvée"}, 404
        if order.status == 'validated':
            return {"msg": "Une commande validée ne peut pas être annulée"}, 400
        if order.status == 'cancelled':
            return {"msg": "La commande est déjà annulée"}, 400
        order.status = 'cancelled'
        customer = Customer.query.get(order.customer_id)
        notification_user = Notification(user_id=order.user_id, message=f"Votre commande {order.id} a été annulée.")
        notification_admin = Notification(user_id=admin.id, message=f"La commande {order.id} a été annulée.")
        db.session.add_all([notification_user, notification_admin])
        db.session.commit()
        return {"msg": f"Commande {order_id} annulée avec succès", "status": order.status}