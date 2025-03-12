from flask import Blueprint, jsonify, request
from models.user import User
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token

login_bp = Blueprint('login', __name__)

@login_bp.route("/api/login", methods=['POST'])
def login():
    
    """
    Авторизація
    ---
    responses:
      200:
        description: Авторизація успішна
      400:
        description: Відсутні поля
      401:
        description: Невірна пошта чи пароль
    """
    
    data = request.get_json()
    
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "missing required fields"}), 400
        
    user = User.query.filter_by(email=data["email"]).first()
    
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "invalid email or password"}), 401
    
    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "token": access_token,
        "refreshToken": refresh_token,
    }), 200