from flask import Blueprint, render_template

from website.models import Product


views = Blueprint('views', __name__)# Esto es como include en Django, es para importar las vistas a la aplicación principal


@views.route('/')
def home():
    
    item = Product.query.filter_by(flash_sale=True)
    return render_template('home.html', item=item)