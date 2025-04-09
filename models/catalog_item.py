from flask_bcrypt import Bcrypt
from extensions import db

bcrypt = Bcrypt()

class CatalogItem(db.Model):
    __tablename__ = 'catalog'

    code = db.Column(db.String(50), primary_key=True)
    shape = db.Column(db.String(100))
    dimensions = db.Column(db.String(100))
    images = db.Column(db.Text)

    def __repr__(self):
        return f'<CatalogItem {self.Article}>'