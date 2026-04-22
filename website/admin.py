from flask import Blueprint, render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_required
from website.models import Product
from .forms import ShopItemForm
from website import db
import os
from werkzeug.utils import secure_filename

admin = Blueprint('admin', __name__)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
def add_shop_items():
    # 1. Verificación de Seguridad estricta: 
    # Solo el usuario con ID 1 puede ver esta sección.
    if not current_user.is_authenticated or current_user.id != 1:
        # Mostramos 404 para que no sepan que la ruta existe
        return render_template('404.html'), 404

    form = ShopItemForm()
    
    if form.validate_on_submit():
        # Procesar la imagen
        file = form.product_picture.data
        filename = secure_filename(file.filename)
        
        # Ruta de guardado
        upload_path = os.path.join(current_app.root_path, 'static/uploads', filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        file.save(upload_path)
        
        # Crear el nuevo producto (Modelo Product)
        new_item = Product(
            product_name=form.product_name.data,
            current_price=form.current_price.data,
            previous_price=form.previous_price.data,
            in_stock=form.in_stock.data,
            product_picture=filename,
            flash_sale=form.flash_sale.data
        )
        
        try:
            db.session.add(new_item)
            db.session.commit()
            flash(f'Producto "{new_item.product_name}" añadido con éxito', 'success')
            return redirect(url_for('admin.add_shop_items'))
        except Exception as e:
            db.session.rollback()
            print(f"Error en DB: {e}")
            flash('Error al agregar el producto a la base de datos', 'danger')

    # Consultar items para la tabla de Zora
    items = Product.query.order_by(Product.date_added.desc()).all()
    
    return render_template('add-shop-items.html', form=form, items=items, user=current_user)

@admin.route('/shop-items', methods=['GET','POST'])
def shop_items():
    # Misma validación de seguridad por ID
    if not current_user.is_authenticated or current_user.id != 1:
        return render_template('404.html'), 404
        
    items = Product.query.order_by(Product.date_added.desc()).all()
    return render_template('shop-items.html', items=items, user=current_user)