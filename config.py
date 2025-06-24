import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'APZENPtcP_RAkxvWL9MNwQBIxOajuKqbNXdynEIXisw'
    #SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:mywitti@localhost:5432/witti'
    SQLALCHEMY_DATABASE_URI = 'postgresql://user_test:123456@10.125.30.25:5432/production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or '4AZvSj-VQzll1zsTxY9dLtLSMn2obqpxVjVrwQwWAPk'

    # Ajout pour l'onboarding
    COUNTRY_LIST = {
        1: "Côte d'Ivoire",
        2: "Burkina Faso",
        3: "Sénégal"
    }
