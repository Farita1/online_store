from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate   # 👈 NUEVO

db = SQLAlchemy()
migrate = Migrate()                 # 👈 NUEVO

DB_URI = 'postgresql://postgres:crashtitan2003@localhost:5432/online_store'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'The Pretty Boy, Dirty Boy'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    migrate.init_app(app, db)       # 👈 CLAVE

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html', error=error), 404

    # Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from .models import Customer

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    # Blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    return app