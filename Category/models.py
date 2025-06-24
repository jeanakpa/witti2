from extensions import db

class Category(db.Model):
    __tablename__ = 'category_category'
    id = db.Column(db.BigInteger, primary_key=True)
    category_name = db.Column(db.String(50), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=False)
    cat_point = db.Column(db.Integer, nullable=False)
    recomp_point = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Category {self.category_name}>"