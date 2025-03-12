from extensions import db

class CartItem(db.Model):
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    article = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, default=1)
    currency = db.Column(db.String(10))
    
    def __repr__(self):
        return f'<CartItem {self.article} for user {self.user_id}>'