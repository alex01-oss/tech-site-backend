from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from models.user import User
from extensions import db
from flask_jwt_extended import create_refresh_token

register_bp = Blueprint('register', __name__)

@register_bp.route("/api/register", methods=['POST'])
def register():
    
    """
    Регістрація
    ---
    responses:
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
    
    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return jsonify({
      "message": "user registered succesfully",
      "token": access_token,
      "refreshToken": refresh_token,
      "user": {
        "email": new_user.email,
        "username": new_user.username
      }
    }), 201
