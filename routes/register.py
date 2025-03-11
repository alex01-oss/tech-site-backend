from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
# from config.config import Config
from models.user import User
from extensions import db
# from extensions import limiter

register_bp = Blueprint('register', __name__)

# @limiter.limit(Config.LIMIT_PER_MINUTE)
@register_bp.route("/api/register", methods=['POST'])
def register():
    
    """
    Регістрація
    ---
    responses:
      200:
        description: Регістрація успішна
      409:
        descriprion: Пошта вже зареєстрована
      201:
        description: Реєстрація успішна
    """
    
    data = request.get_json()
    
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "missing required fields"}), 400
        
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "email already in use"}), 409
    
    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()
    
    token = create_access_token(identity=new_user.id)

    return jsonify({"message": "user registered succesfully", "token": token}), 201
