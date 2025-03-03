from flask import Blueprint, jsonify, request
from schemas.db_schemas import User
from extensions import db

register_bp = Blueprint('register', __name__)

@register_bp.route("/api/register", methods=['POST'])
def register():
    
    """
    Регістрація
    ---
    responses:
      200:
        description: Регістрація успішна
    """
    
    data = request.get_json()
    # print(request.data)
    
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "missing required fields"}), 400
        
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "email already in use"}), 409
    
    new_user = User(username=data["username"], email=data["email"])
    new_user.set_password(data["password"])
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "user registered succesfully"}), 201