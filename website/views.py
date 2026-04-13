from flask import Blueprint, render_template


views = Blueprint('views', __name__)# Esto es como include en Django, es para importar las vistas a la aplicación principal


@views.route('/')
def home():
    return render_template('home.html')