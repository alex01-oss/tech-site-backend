from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Tool(db.Model):
    __tablename__ = 'construction'
    
    Article = db.Column(db.String(50), primary_key=True)
    Category = db.Column(db.String(100))
    Line = db.Column(db.String(100))
    Subline = db.Column(db.String(100))
    Title = db.Column(db.Text)
    Price = db.Column(db.Numeric)
    Currency = db.Column(db.String(10))
    Unit = db.Column(db.String(10))
    Images = db.Column(db.Text)
    Available = db.Column(db.Boolean)
    Name_param1 = db.Column(db.String(100))
    Unit_param1 = db.Column(db.String(50))
    Value_param1 = db.Column(db.String(100))
    Name_param2 = db.Column(db.String(100))
    Unit_param2 = db.Column(db.String(50))
    Value_param2 = db.Column(db.String(100))
    Name_param3 = db.Column(db.String(100))
    Unit_param3 = db.Column(db.String(50))
    Value_param3 = db.Column(db.String(100))
    Name_param4 = db.Column(db.String(100))
    Unit_param4 = db.Column(db.String(50))
    Value_param4 = db.Column(db.String(100))
    Name_param5 = db.Column(db.String(100))
    Unit_param5 = db.Column(db.String(50))
    Value_param5 = db.Column(db.String(100))
    Name_param6 = db.Column(db.String(100))
    Unit_param6 = db.Column(db.String(50))
    Value_param6 = db.Column(db.String(100))
    Name_param7 = db.Column(db.String(100))
    Unit_param7 = db.Column(db.String(50))
    Value_param7 = db.Column(db.String(100))

    def __repr__(self):
        return f'<Tool {self.Article}>'
