from flask import Blueprint, send_from_directory

images_bp = Blueprint('images', __name__)

@images_bp.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)
