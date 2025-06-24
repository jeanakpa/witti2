from flask import Blueprint, current_app, request
from flask_restx import Api, Resource, fields
import uuid
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from Customer.models import Customer, Transaction
from Category.models import Category
from Lot.models import Notification
from Models.token_blacklist import TokenBlacklist
from extensions import db
from datetime import datetime, timedelta
from Account.models import Account
from Customer.models import Customer
from Models.referral import Referral


customer_bp = Blueprint('customer', __name__)
reward_bp = Blueprint('reward', __name__)
api = Api(customer_bp, version='1.0', title='Customer API', description='API for customer operations')

# Define category ranges
CATEGORIES = [
    {"name": "Eco Premium", "code": "A", "min": 0, "max": 100},
    {"name": "Executive", "code": "B", "min": 100, "max": 1000},
    {"name": "Executive +", "code": "C", "min": 1000, "max": 3000},
    {"name": "First Class", "code": "D", "min": 3000, "max": float('inf')}
]

# Define response models for dashboard
dashboard_model = api.model('Dashboard', {
    'category': fields.String(description='Customer category'),
    'jetons': fields.Integer(description='Total jetons'),
    'percentage': fields.Float(description='Percentage within category range'),
    'short_name': fields.String(description='Short name'),
    'tokens_to_next_tier': fields.Integer(description='Jetons needed to reach next tier'),
    'last_transactions': fields.List(fields.Raw, description='Last 5 transactions')
})

# Define response models for transactions
transaction_model = api.model('Transaction', {
    'date': fields.String(description='Transaction date'),
    'amount': fields.String(description='Amount'),
    'type': fields.String(description='Transaction type (DEPOSIT/WITHDRAWAL)')
})

trends_model = api.model('Trends', {
    'deposit_percentage': fields.Float(description='Percentage of deposit transactions'),
    'withdrawal_percentage': fields.Float(description='Percentage of withdrawal transactions')
})

transactions_response_model = api.model('TransactionsResponse', {
    'transactions': fields.List(fields.Nested(transaction_model), description='List of transactions'),
    'total_transactions': fields.Integer(description='Total number of transactions'),
    'period_start': fields.String(description='Start of the period'),
    'period_end': fields.String(description='End of the period'),
    'trends': fields.Nested(trends_model, description='Transaction trends (deposit and withdrawal percentages)')
})

# Define response model for notifications
notification_model = api.model('Notification', {
    'id': fields.Integer(description='Notification ID'),
    'message': fields.String(description='Notification message'),
    'created_at': fields.String(description='Creation date')
})

notifications_response_model = api.model('NotificationsResponse', {
    'msg': fields.String(description='Success message'),
    'notifications': fields.List(fields.Nested(notification_model), description='List of notifications')
})

# Define response model for profile
profile_model = api.model('Profile', {
    'first_name': fields.String(description='Customer first name'),
    'short_name': fields.String(description='Customer short name'),
    'agency': fields.String(description='Customer agency'),
    'jetons': fields.Integer(description='Total jetons'),
    'category': fields.String(description='Customer category'),
    'percentage': fields.Float(description='Percentage within category range'),
    'tokens_to_next_tier': fields.Integer(description='Jetons needed to reach next tier')
})
#Invitation de parrainage
referral_model = api.model('Referral', {
    'referral_link': fields.String(description='Lien de parrainage'),
    'referred_email': fields.String(description='Email de l\'ami invité'),
    'status': fields.String(description='Statut du parrainage'),
    'created_at': fields.DateTime(description='Date de création')
})

# Define response model for logout
logout_response_model = api.model('LogoutResponse', {
    'msg': fields.String(description='Logout message')
})

@api.route('/<string:customer_code>/dashboard')
class CustomerDashboard(Resource):
    @jwt_required()
    @api.marshal_with(dashboard_model)
    def get(self, customer_code):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}, Requested customer_code: {customer_code}")

            if customer_code != identifiant:
                current_app.logger.warning(f"Access denied: {customer_code} does not match {identifiant}")
                return {"message": "Access denied: You can only access your own dashboard"}, 403

            customer = db.session.query(Customer).filter_by(customer_code=identifiant).first()
            current_app.logger.info(f"Customer query result: {customer}")
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant/customer_code: {identifiant}")
                return {"message": "Customer not found"}, 404

            current_app.logger.info(f"Customer found: ID={customer.id}, solde={customer.solde}")

            category = customer.category
            jetons = customer.solde or 0
            category_name = category.category_name if category else "Unknown"
            current_app.logger.info(f"Category: {category_name}, Jetons: {jetons}")

            percentage = 0
            tokens_to_next_tier = 0
            for i, cat in enumerate(CATEGORIES):
                if cat['min'] <= jetons < cat['max']:
                    range_width = cat['max'] - cat['min']
                    position_in_range = jetons - cat['min']
                    percentage = (position_in_range / range_width) * 100 if range_width > 0 else 0
                    if i + 1 < len(CATEGORIES):
                        tokens_to_next_tier = CATEGORIES[i + 1]['min'] - jetons
                    break
            if not tokens_to_next_tier:
                tokens_to_next_tier = 0
            current_app.logger.info(f"Percentage: {percentage}, Tokens to next tier: {tokens_to_next_tier}")

            transactions = db.session.query(Transaction).filter_by(customer_id=customer.id).order_by(Transaction.deposit_date.desc()).limit(5).all()
            last_transactions = [
                {
                    "date": t.deposit_date,
                    "amount": str(t.montant) if t.montant else "0.00",
                    "type": t.sens
                }
                for t in transactions
            ]
            current_app.logger.info(f"Transactions fetched: {len(last_transactions)}")

            dashboard = {
                "category": category_name,
                "jetons": jetons,
                "percentage": round(percentage, 2),
                "short_name": customer.short_name,
                "tokens_to_next_tier": tokens_to_next_tier,
                "last_transactions": last_transactions
            }

            current_app.logger.info(f"Dashboard retrieved for customer_code: {customer_code}")
            return dashboard, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching dashboard: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/<string:customer_code>/transactions')
class CustomerTransactions(Resource):
    @jwt_required()
    @api.marshal_with(transactions_response_model)
    def get(self, customer_code):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}, Requested customer_code: {customer_code}")

            if customer_code != identifiant:
                current_app.logger.warning(f"Access denied: {customer_code} does not match {identifiant}")
                return {"message": "Access denied: You can only access your own transactions"}, 403

            customer = db.session.query(Customer).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant/customer_code: {identifiant}")
                return {"message": "Customer not found"}, 404

            # Get filter parameters from query string
            period = request.args.get('period', 'month').lower()
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            # Current date
            now = datetime(2025, 5, 24, 23, 21)

            # Define period boundaries
            if period == 'month':
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                period_end = now
            elif period == 'week':
                # Week starts on Monday
                days_to_monday = (now.weekday() - 0) % 7
                period_start = (now - timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
                period_end = now
            elif period == 'year':
                period_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                period_end = now
            elif period == 'custom':
                if not start_date or not end_date:
                    return {"message": "start_date and end_date are required for custom period"}, 400
                try:
                    period_start = datetime.strptime(start_date, '%Y-%m-%d')
                    period_end = datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                    if period_end < period_start:
                        return {"message": "end_date must be after start_date"}, 400
                except ValueError:
                    return {"message": "Invalid date format, use YYYY-MM-DD"}, 400
            else:
                return {"message": "Invalid period, use 'month', 'week', 'year', or 'custom'"}, 400

            # Convert period boundaries to strings for SQL comparison
            period_start_str = period_start.strftime('%Y-%m-%d %H:%M:%S')
            period_end_str = period_end.strftime('%Y-%m-%d %H:%M:%S')

            # Fetch transactions within the period
            transactions = db.session.query(Transaction).filter(
                Transaction.customer_id == customer.id,
                Transaction.deposit_date >= period_start_str,
                Transaction.deposit_date <= period_end_str
            ).order_by(Transaction.deposit_date.desc()).all()

            transactions_list = [
                {
                    "date": t.deposit_date,
                    "amount": str(t.montant) if t.montant else "0.00",
                    "type": t.sens
                }
                for t in transactions
            ]

            # Calculate trends
            total_transactions = len(transactions)
            deposit_count = sum(1 for t in transactions if t.sens == 'DEPOSIT')
            withdrawal_count = sum(1 for t in transactions if t.sens == 'WITHDRAWAL')

            deposit_percentage = (deposit_count / total_transactions * 100) if total_transactions > 0 else 0
            withdrawal_percentage = (withdrawal_count / total_transactions * 100) if total_transactions > 0 else 0

            trends = {
                "deposit_percentage": round(deposit_percentage, 2),
                "withdrawal_percentage": round(withdrawal_percentage, 2)
            }

            response = {
                "transactions": transactions_list,
                "total_transactions": total_transactions,
                "period_start": period_start_str,
                "period_end": period_end_str,
                "trends": trends
            }

            current_app.logger.info(f"Transactions retrieved for customer_code: {customer_code}, period: {period}, trends: {trends}")
            return response, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching transactions: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/<string:customer_code>/notifications')
class CustomerNotifications(Resource):
    @jwt_required()
    @api.marshal_with(notifications_response_model)
    def get(self, customer_code):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}, Requested customer_code: {customer_code}")

            if customer_code != identifiant:
                current_app.logger.warning(f"Access denied: {customer_code} does not match {identifiant}")
                return {"message": "Access denied: You can only access your own notifications"}, 403

            customer = db.session.query(Customer).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant/customer_code: {identifiant}")
                return {"message": "Customer not found"}, 404

            # Récupérer les notifications de l'utilisateur
            notifications = Notification.query.filter_by(user_id=customer.account_id).order_by(Notification.created_at.desc()).all()

            notifications_data = [{
                'id': notification.id,
                'message': notification.message,
                'created_at': str(notification.created_at) if notification.created_at else "Unknown"
            } for notification in notifications]

            return {
                'msg': 'Notifications récupérées avec succès',
                'notifications': notifications_data
            }, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching notifications: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/<string:customer_code>/profile')
class CustomerProfile(Resource):
    @jwt_required()
    @api.marshal_with(profile_model)
    def get(self, customer_code):
        try:
            identifiant = get_jwt_identity()
            current_app.logger.info(f"JWT Identity: {identifiant}, Requested customer_code: {customer_code}")

            if customer_code != identifiant:
                current_app.logger.warning(f"Access denied: {customer_code} does not match {identifiant}")
                return {"message": "Access denied: You can only access your own profile"}, 403

            customer = db.session.query(Customer).filter_by(customer_code=identifiant).first()
            if not customer:
                current_app.logger.warning(f"No customer found for identifiant/customer_code: {identifiant}")
                return {"message": "Customer not found"}, 404

            # Calculer les informations de catégorie et pourcentage
            category = customer.category
            jetons = customer.solde or 0
            category_name = category.category_name if category else "Unknown"

            percentage = 0
            tokens_to_next_tier = 0
            for i, cat in enumerate(CATEGORIES):
                if cat['min'] <= jetons < cat['max']:
                    range_width = cat['max'] - cat['min']
                    position_in_range = jetons - cat['min']
                    percentage = (position_in_range / range_width) * 100 if range_width > 0 else 0
                    if i + 1 < len(CATEGORIES):
                        tokens_to_next_tier = CATEGORIES[i + 1]['min'] - jetons
                    break
            if not tokens_to_next_tier:
                tokens_to_next_tier = 0

            profile = {
                "first_name": customer.first_name,
                "short_name": customer.short_name,
                "agency": "RGK",
                "jetons": jetons,
                "category": category_name,
                "percentage": round(percentage, 2),
                "tokens_to_next_tier": tokens_to_next_tier
            }

            current_app.logger.info(f"Profile retrieved for customer_code: {customer_code}")
            return profile, 200

        except Exception as e:
            current_app.logger.error(f"Error fetching profile: {str(e)}")
            return {"error": str(e)}, 500

@api.route('/logout')
class CustomerLogout(Resource):
    @jwt_required()
    @api.marshal_with(logout_response_model)
    def post(self):
        try:
            # Récupérer le JTI du token
            jti = get_jwt()['jti']
            # Ajouter le token à la liste noire
            blacklisted_token = TokenBlacklist(jti=jti)
            db.session.add(blacklisted_token)
            db.session.commit()

            current_app.logger.info(f"Customer logged out successfully, token JTI {jti} blacklisted")
            return {"msg": "Déconnexion réussie"}, 200

        except Exception as e:
            current_app.logger.error(f"Error during customer logout: {str(e)}")
            return {"error": str(e)}, 500
        


# Systeme de parrainage

invite_model = api.model('Invite', {
    'email': fields.String(required=True, description='Email de l\'ami à inviter')
})

class InviteResource(Resource):
    @jwt_required()
    @api.expect(invite_model)
    def post(self):
        # Récupérer l'utilisateur connecté
        identifiant = get_jwt_identity()
        user = Account.query.filter_by(identifiant=identifiant).first()
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404

        # Récupérer l'email de l'ami
        data = request.get_json()
        email = data.get('email')
        if not email:
            return {'message': 'Email requis'}, 400

        # Vérifier si l'email existe déjà dans les parrainages
        existing_referral = Referral.query.filter_by(referred_email=email).first()
        if existing_referral:
            return {'message': 'Cet email a déjà été invité'}, 400

        # Créer un nouveau parrainage
        referral_code = str(uuid.uuid4())
        referral = Referral(
            referrer_id=user.id,
            referred_email=email,
            referral_code=referral_code,
            status='pending'
        )
        db.session.add(referral)
        db.session.commit()

        referral_link = f"http://127.0.0.1:5000/accounts/refer/{referral_code}"
        return {
            'message': 'Invitation envoyée',
            'referral_link': referral_link
        }, 201

api.add_resource(InviteResource, '/invite')