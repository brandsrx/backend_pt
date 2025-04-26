from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger

from app.config import Config
from app.database import init_db

from app.controllers.auth_controller import auth_bp
from app.controllers.user_controller import user_bp
from app.controllers.post_controller import post_bp

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)
swagger = Swagger(app)
CORS(app)

# Inicializar base de datos
init_db()

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(post_bp, url_prefix='/api/post')


if __name__ == "__main__":
    app.run(debug=True)