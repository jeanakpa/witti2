# app.py
import logging
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity
from Models.page_visit import PageVisit  # Corrigé de Models à models
from Models.referral import Referral  # Corrigé de Models à models
from config import Config
from extensions import db, ma, jwt, migrate

# Importation des modèles
from Account.models import Account
from Survey.models import Survey, SurveyOption, SurveyResponse
from Faq.models import FAQ
from Customer.models import Customer, Epargne, Transaction, SoldeDepotRecurrent, Rebours, UnpaidAccount, CustomerDat
from Category.models import Category
from Lot.models import Recompense, Favorite, CartItem, Stock, Order, Notification, OrderItem
from Resultat.models import ResultatCriteria, ResultatTotal, ResultatPoint, ClientRecompense
from Models.token_blacklist import TokenBlacklist  # Corrigé de Models à models
from Support.models import SupportRequest

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    token = db.session.query(TokenBlacklist).filter_by(jti=jti).first()
    return token is not None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Application starting with logging enabled")
    app.logger.info("JWT_SECRET_KEY loaded successfully")

    # Initialisation des extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Importation des blueprints après l'initialisation
    from Account.views import accounts_bp
    from Lot.views import lot_bp
    from Customer.views import customer_bp
    from Admin.views import admin_bp
    from Faq.views import faq_bp
    from Support.views import support_bp
    from Survey.views import survey_bp

    # Enregistrement des blueprints
    app.register_blueprint(accounts_bp, url_prefix='/accounts')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(lot_bp, url_prefix='/lot')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(faq_bp, url_prefix='/faq')
    app.register_blueprint(support_bp, url_prefix='/support')
    app.register_blueprint(survey_bp, url_prefix='/survey')

    # Route pour servir les images
    @app.route('/media/<path:filename>')
    def serve_media(filename):
        return send_from_directory('media', filename)

    # Enregistrer les visites de pages
    @app.before_request
    def track_page_visit():
        path = request.path
        user_id = None
        try:
            identifiant = get_jwt_identity()
            if identifiant:
                user = Account.query.filter_by(identifiant=identifiant).first()
                user_id = user.id if user else None
        except Exception as e:
            app.logger.warning(f"Erreur lors de la récupération de l'identité : {e}")
        try:
            page_visit = PageVisit(path=path, user_id=user_id)
            db.session.add(page_visit)
            db.session.flush()
        except Exception as e:
            app.logger.error(f"Erreur lors de l'enregistrement de la visite : {e}")
            db.session.rollback()

    return app

app = create_app()


if __name__ == '__main__':
    app.run(debug=True)