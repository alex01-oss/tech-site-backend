from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

refresh_token_bp = Blueprint('refresh_token', __name__)

@refresh_token_bp.route('/api/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    
    return jsonify({
        "token": new_access_token
    }), 200