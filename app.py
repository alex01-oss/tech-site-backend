import time
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from config.config import Config
from extensions import db, cache
from routes.menu import menu_bp
from routes.catalog import catalog_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
cache.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
swagger = Swagger(app)


app.register_blueprint(menu_bp)
app.register_blueprint(catalog_bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

