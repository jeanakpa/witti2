# admin/resources/stats.py (corrigé complet)
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from Account.models import Account
from Customer.models import Customer
from Lot.models import Order, Recompense, order_items
from Models.page_visit import PageVisit  # Ajoute l'importation
from Admin.views import api
from extensions import db
from sqlalchemy.sql import desc

stats_model = api.model('Stats', {
    'total_customers': fields.Integer(description='Total Customers'),
    'top_customer_tokens': fields.String(description='Customer with Most Tokens'),
    'pending_orders': fields.Integer(description='Pending Orders'),
    'cancelled_orders': fields.Integer(description='Cancelled Orders'),
    'validated_orders': fields.Integer(description='Validated Orders'),
    'most_visited_pages': fields.String(description='Most Visited Pages'),
    'most_purchased_reward': fields.String(description='Most Purchased Reward')
})

class Stats(Resource):
    @jwt_required()
    @api.marshal_with(stats_model)
    def get(self):
        user_id = get_jwt_identity()
        user = Account.query.filter_by(identifiant=user_id).first()
        if not user or not (user.is_admin or user.is_superuser):
            api.abort(403, "Accès interdit")
        total_customers = Customer.query.count()
        top_customer = Customer.query.order_by(Customer.solde.desc()).first()
        top_customer_tokens = f"{top_customer.first_name} {top_customer.short_name} ({top_customer.solde} tokens)" if top_customer else "N/A"
        pending_orders = Order.query.filter_by(status='pending').count()
        cancelled_orders = Order.query.filter_by(status='cancelled').count()
        validated_orders = Order.query.filter_by(status='validated').count()
        # Récupérer les pages les plus visitées (limité aux 3 premières)
        most_visited = db.session.query(PageVisit.path, db.func.count(PageVisit.path).label('visit_count')) \
            .group_by(PageVisit.path) \
            .order_by(desc(db.func.count(PageVisit.path))) \
            .limit(3) \
            .all()
        most_visited_pages = ", ".join([page[0] for page in most_visited]) if most_visited else "Aucune donnée"
        # Récupérer l'article le plus commandé
        most_purchased_reward_query = db.session.query(Recompense, db.func.count(order_items.c.reward_id).label('purchase_count')) \
            .join(order_items, Recompense.id == order_items.c.reward_id) \
            .join(Order, Order.id == order_items.c.order_id) \
            .filter(Order.status == 'validated') \
            .group_by(Recompense.id) \
            .order_by(desc(db.func.count(order_items.c.reward_id))) \
            .first()
        most_purchased_reward_name = most_purchased_reward_query[0].libelle if most_purchased_reward_query else "N/A"
        return {
            'total_customers': total_customers,
            'top_customer_tokens': top_customer_tokens,
            'pending_orders': pending_orders,
            'cancelled_orders': cancelled_orders,
            'validated_orders': validated_orders,
            'most_visited_pages': most_visited_pages,
            'most_purchased_reward': most_purchased_reward_name
        }