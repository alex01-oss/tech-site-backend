from flask_bcrypt import Bcrypt
from extensions import db

bcrypt = Bcrypt()

class Tool(db.Model):
    __tablename__ = 'products'

    Article = db.Column('article', db.String(50), primary_key=True)
    Category = db.Column('category', db.String(100))
    Line = db.Column('line', db.String(100))
    Subline = db.Column('subline', db.String(100))
    Title = db.Column('title', db.Text)
    Price = db.Column('price', db.Numeric)
    Currency = db.Column('currency', db.String(10))
    Unit = db.Column('unit', db.String(10))
    Images = db.Column('images', db.Text)
    Available = db.Column('available', db.Boolean)
    
    Name_param1 = db.Column('name_param1', db.String(100))
    Unit_param1 = db.Column('unit_param1', db.String(50))
    Value_param1 = db.Column('value_param1', db.String(100))
    
    Name_param2 = db.Column('name_param2', db.String(100))
    Unit_param2 = db.Column('unit_param2', db.String(50))
    Value_param2 = db.Column('value_param2', db.String(100))
    
    Name_param3 = db.Column('name_param3', db.String(100))
    Unit_param3 = db.Column('unit_param3', db.String(50))
    Value_param3 = db.Column('value_param3', db.String(100))
    
    Name_param4 = db.Column('name_param4', db.String(100))
    Unit_param4 = db.Column('unit_param4', db.String(50))
    Value_param4 = db.Column('value_param4', db.String(100))
    
    Name_param5 = db.Column('name_param5', db.String(100))
    Unit_param5 = db.Column('unit_param5', db.String(50))
    Value_param5 = db.Column('value_param5', db.String(100))
    
    Name_param6 = db.Column('name_param6', db.String(100))
    Unit_param6 = db.Column('unit_param6', db.String(50))
    Value_param6 = db.Column('value_param6', db.String(100))
    
    Name_param7 = db.Column('name_param7', db.String(100))
    Unit_param7 = db.Column('unit_param7', db.String(50))
    Value_param7 = db.Column('value_param7', db.String(100))

    def __repr__(self):
        return f'<Tool {self.Article}>'