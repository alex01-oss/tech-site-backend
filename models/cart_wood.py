from extensions import db

class CartWoodItem(db.Model):
    __tablename__ = 'cart_wood_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    shape = db.Column(db.String(255), nullable=True)
    dimensions = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Integer, default=1)
    images = db.Column(db.Text)
    
    def __repr__(self):
        return f'<CartWoodItem {self.code} for user {self.user_id}>'