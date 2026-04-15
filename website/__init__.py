from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager # 1. Importar

db = SQLAlchemy()
DB_URI = 'postgresql://postgres:crashtitan2003@localhost:5432/online_store'

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'The Pretty Boy, Dirty Boy'
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    # 2. Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login' # A dónde redirigir si no está logueado
    login_manager.init_app(app)

    from .models import Customer # Asegúrate de que tu modelo se llame Customer o User

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    # Registro de Blueprints
    from .views import views
    from .auth import auth
    from .admin import admin

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(admin, url_prefix='/admin')

    from .models import Customer, Product, ProductVariant, Cart, Order
    with app.app_context():
        db.create_all()

    return app