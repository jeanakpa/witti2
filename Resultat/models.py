from extensions import db

class ResultatCriteria(db.Model):
    __tablename__ = 'resultat_criteria'
    id = db.Column(db.BigInteger, primary_key=True)
    criteria_name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f"<ResultatCriteria {self.criteria_name}>"

class ResultatTotal(db.Model):
    __tablename__ = 'resultat_total'
    id = db.Column(db.BigInteger, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    customer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<ResultatTotal {self.customer} - {self.date}>"

class ResultatPoint(db.Model):
    __tablename__ = 'resultat_point'
    id = db.Column(db.BigInteger, primary_key=True)
    notation = db.Column(db.String(50), nullable=False)
    jeton = db.Column(db.Integer, nullable=False)
    mois = db.Column(db.String(20), nullable=False)
    montant = db.Column(db.BigInteger, nullable=False)
    date_notes = db.Column(db.Date, nullable=False)
    customer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<ResultatPoint {self.customer} - {self.mois}>"

class ClientRecompense(db.Model):
    __tablename__ = 'resultat_clientarecompense'
    id = db.Column(db.BigInteger, primary_key=True)
    users = db.Column(db.String(50), nullable=False)
    client = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"<ClientRecompense {self.client} - {self.score}>"

class ResultatNotation(db.Model):
    __tablename__ = 'resultat_notation'
    id = db.Column(db.BigInteger, primary_key=True)
    notation_code = db.Column(db.String(20), nullable=False)
    amount_inf = db.Column(db.Integer, nullable=False)
    amount_sup = db.Column(db.Integer, nullable=False)
    jeton = db.Column(db.Integer, nullable=False)
    criteria_id = db.Column(db.BigInteger, db.ForeignKey('resultat_criteria.id'), nullable=False)

    def __repr__(self):
        return f"<ResultatNotation {self.notation_code} - {self.amount_inf}-{self.amount_sup} - {self.jeton}>"

class ResultatNotes(db.Model):
    __tablename__ = 'resultat_notes'
    id = db.Column(db.BigInteger, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    notation = db.Column(db.String(50), nullable=False)
    jeton = db.Column(db.Integer, nullable=False)
    mois = db.Column(db.String(2), nullable=False)
    montant = db.Column(db.Integer, nullable=False)
    date_notes = db.Column(db.Date, nullable=False)
    customer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<ResultatNotes {self.user} - {self.notation} - {self.mois}>"

class ResultatScore(db.Model):
    __tablename__ = 'resultat_score'
    id = db.Column(db.BigInteger, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    score = db.Column(db.Integer, nullable=False)
    customer = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f"<ResultatScore {self.user} - {self.customer} - {self.score}>"