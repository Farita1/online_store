from flask import Blueprint, render_template, flash, redirect, request, url_for, current_app
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

@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    # Seguridad: Solo Farita (ID 1)
    if current_user.id != 1:
        return render_template('404.html'), 404

    item_to_update = Product.query.get_or_404(item_id)
    form = ShopItemForm()

    if form.validate_on_submit():
        # --- LÓGICA DE PRECIO INTELIGENTE ---
        # Si el usuario cambió el precio actual, el anterior se actualiza solo
        nuevo_precio = form.current_price.data
        if item_to_update.current_price != nuevo_precio:
            item_to_update.previous_price = item_to_update.current_price
        
        # Actualización de campos
        item_to_update.product_name = form.product_name.data
        item_to_update.current_price = nuevo_precio
        item_to_update.in_stock = form.in_stock.data
        item_to_update.flash_sale = form.flash_sale.data

        # Gestión de Imagen Opcional
        file = form.product_picture.data
        if file and hasattr(file, 'filename') and file.filename != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.root_path, 'static/uploads', filename))
            item_to_update.product_picture = filename

        try:
            db.session.commit()
            flash(f'¡{item_to_update.product_name} actualizado con éxito!', 'success')
            return redirect(url_for('admin.shop_items'))
        except Exception as e:
            db.session.rollback()
            flash('Error al guardar en la base de datos', 'danger')

    # Si hay errores de validación (ej. letras en el precio)
    elif request.method == 'POST':
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{getattr(form, field).label.text}: {error}", "danger")

    # Carga inicial de datos
    elif request.method == 'GET':
        form.product_name.data = item_to_update.product_name
        form.previous_price.data = item_to_update.previous_price
        form.current_price.data = item_to_update.current_price
        form.in_stock.data = item_to_update.in_stock
        form.flash_sale.data = item_to_update.flash_sale

    return render_template('update-item.html', form=form, item=item_to_update, user=current_user)


@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    # Seguridad: Solo el admin (ID 1)
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get_or_404(item_id)
            
            image_path = os.path.join(current_app.root_path, 'static/uploads', item_to_delete.product_picture)
            if os.path.exists(image_path): os.remove(image_path)

            db.session.delete(item_to_delete)
            db.session.commit()
            flash(f'Producto "{item_to_delete.product_name}" eliminado con éxito', 'success')
            return redirect(url_for('admin.add_shop_items')) # Redirige a la gestión
        except Exception as e:
            db.session.rollback()
            flash('Error al eliminar el producto', 'danger')
            return redirect(url_for('admin.add_shop_items'))
    return render_template('404.html'), 404