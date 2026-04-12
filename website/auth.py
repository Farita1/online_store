from flask import Blueprint


auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    return 'Página de inicio de sesión'


@auth.route('/sign-up')
def sign_up():
    return 'Página de registro'