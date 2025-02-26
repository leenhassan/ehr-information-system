import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate
from flask_login import LoginManager

login_manager = LoginManager()

migrate = Migrate()
 # Import the blueprint

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    
    print(__name__)

    # Set a secret key
    app.config['SECRET_KEY'] = 'narwhals'

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Khadija2005*@localhost/ehr_database'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = 'dija.aa1714@gmail.com'
    app.config['MAIL_PASSWORD'] = 'rdfo zlhm aqeq ytmd'

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Set up login manager
    login_manager.init_app(app)
    login_manager.login_view = "main.login"  # Redirect to the login page if not authenticated
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    # Import and register blueprints
    from app.routes import main 
    app.register_blueprint(main)
    return app
