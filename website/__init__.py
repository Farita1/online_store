from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'The Pretty Boy, Dirty Boy'
    
    from .views import views
    from .auth import auth
    from .admin import admin
    
    app.register_blueprint(views, url_prefix='/') # localhost:5000/about-us
    app.register_blueprint(auth, url_prefix='/auth') # localhost:5000/auth/change-password
    app.register_blueprint(admin, url_prefix='/admin') # localhost:5000/admin/dashboard
    
    
    
    
    return app

