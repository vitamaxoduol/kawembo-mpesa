from flask import Flask
from dbconfig import db
# from flask_migrate import Migrate
# from flask_cors import CORS
# from flask_socketio import SocketIO
import os
# from app import current_app
from routes.register_routes import register_routes
# from mpesa.register_routes import register_routes
# from flask_jwt_extended import JWTManager

from flask import Flask, current_app
from ext import migrate, CORS, socketio, jwt
from config import Config
from flask_mail import Mail
# from flask_mpesa import MpesaAPI



def create_app():
    app = Flask(__name__, static_url_path='/swagger-ui', static_folder='swagger_ui')
    app.config.from_object(Config)

    basedir = os.path.abspath(os.path.dirname(__file__))
    db_dir = os.path.join(basedir, 'instance')
    try:
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, Config.SQLALCHEMY_DATABASE_URI)
    except Exception as e:
        print(f"Error creating directory: {e}")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    socketio.init_app(app)
    
    # Assign JWT configurations from config.py
    jwt.secret_key = app.config['JWT_SECRET_KEY']
    jwt.blacklist_enabled = app.config['JWT_BLACKLIST_ENABLED']
    jwt.blacklist_token_checks = app.config['JWT_BLACKLIST_TOKEN_CHECKS']

    # Initialize Flask-Mail
    mail = Mail()

    # Set up email
    app.config['MAIL_SERVER'] = Config.MAIL_SERVER
    app.config['MAIL_PORT'] = Config.MAIL_PORT
    app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD
    app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS
    app.config['MAIL_USE_SSL'] = Config.MAIL_USE_SSL

    # Initialize Flask app with mail settings
    mail.init_app(app)

    # mp = MpesaAPI(app)

    return app

app = create_app()

server_url = "https://kawebo.onrender.com"

# Initialize JWTManager with the app
jwt.init_app(app)


if __name__ == '__main__':
    with app.app_context():
        # jwt_key = current_app.config['JWT_SECRET_KEY']
        # register_routes(app, db, server_url, socketio)
        # db.create_all()
        # # app.run(debug=True, host="0.0.0.0")
        # socketio.run(app, debug=True, host="0.0.0.0")

        jwt_key = current_app.config['JWT_SECRET_KEY']
        register_routes(app, db, server_url, socketio)
        db.create_all()
        print("Initializing Socket.IO server...")
        socketio.init_app(app)
        print("Socket.IO server initialized")
        print("Starting Flask app...")
        app.run(debug=True, host="0.0.0.0")