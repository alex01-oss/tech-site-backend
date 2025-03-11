from flask_bcrypt import Bcrypt
from extensions import db

bcrypt = Bcrypt()

class Tool(db.Model):
    __tablename__ = 'products'

    article = db.Column(db.String(50), primary_key=True)
    category = db.Column(db.String(100))
    line = db.Column(db.String(100))
    subline = db.Column(db.String(100))
    title = db.Column(db.Text)
    price = db.Column(db.Numeric)
    currency = db.Column(db.String(10))
    unit = db.Column(db.String(10))
    images = db.Column(db.Text)
    available = db.Column(db.Boolean)
    
    name_param1 = db.Column(db.String(100))
    unit_param1 = db.Column(db.String(50))
    value_param1 = db.Column(db.String(100))
    
    name_param2 = db.Column(db.String(100))
    unit_param2 = db.Column(db.String(50))
    value_param2 = db.Column(db.String(100))
    
    name_param3 = db.Column(db.String(100))
    unit_param3 = db.Column(db.String(50))
    value_param3 = db.Column(db.String(100))
    
    name_param4 = db.Column(db.String(100))
    unit_param4 = db.Column(db.String(50))
    value_param4 = db.Column(db.String(100))
    
    name_param5 = db.Column(db.String(100))
    unit_param5 = db.Column(db.String(50))
    value_param5 = db.Column(db.String(100))
    
    name_param6 = db.Column(db.String(100))
    unit_param6 = db.Column(db.String(50))
    value_param6 = db.Column(db.String(100))
    
    name_param7 = db.Column(db.String(100))
    unit_param7 = db.Column(db.String(50))
    value_param7 = db.Column(db.String(100))

    def __repr__(self):
        return f'<Tool {self.Article}>'