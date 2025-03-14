from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config.config import Config
from extensions import db, cache
from flask_limiter import Limiter
from flask_migrate import Migrate

from routes.menu import menu_bp
from routes.login import login_bp
from routes.catalog import catalog_bp
from routes.register import register_bp
from routes.get_cart import get_cart_bp
from routes.add_to_cart import add_to_cart_bp
from routes.update_cart import update_cart_bp
from routes.woodworking import woodworking_bp
from routes.remove_from_cart import remove_from_cart_bp

from routes.static import images_bp

from flask_jwt_extended import JWTManager
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
limiter = Limiter(key_func=get_remote_address, storage_uri="redis://localhost:6379/0")

limiter.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
cache.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
swagger = Swagger(app)

app.register_blueprint(menu_bp)
app.register_blueprint(catalog_bp)
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(get_cart_bp)
app.register_blueprint(add_to_cart_bp)
app.register_blueprint(update_cart_bp)
app.register_blueprint(woodworking_bp)
app.register_blueprint(remove_from_cart_bp)

app.register_blueprint(images_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
