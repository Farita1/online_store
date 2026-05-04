from flask import Blueprint, redirect, render_template, request, jsonify, flash, url_for
from flask_login import login_required, current_user
from .models import Cart, Order, Product, ProductVariant
from . import db
import mercadopago
import uuid

views = Blueprint('views', __name__)

# Así debe verse en tu archivo views.py o donde inicialices el SDK
sdk = mercadopago.SDK("APP_USR-8778003157106093-050317-f6cdc983f845e1aa5c8a390ec5deddf6-3374900175")

@views.route('/place-order')
@login_required
def place_order():
    # 1. Obtener los productos del carrito de Zora para este usuario
    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    
    if not customer_cart:
        flash('Tu carrito está vacío')
        return redirect(url_for('views.home'))

    try:
        # 2. Calcular el total
        # Forzamos a int porque en pesos colombianos no usamos decimales para la API
        total_float = sum(item.variant.product.current_price * item.quantity for item in customer_cart)
        total_final = int(total_float) 

        # 3. Preparar los datos de la preferencia
        # Usamos uuid para generar una referencia externa única
        external_ref = str(uuid.uuid4())

        preference_data = {
            "items": [
                {
                    "title": "Compra en Zora Store",
                    "quantity": 1,
                    "unit_price": total_final,
                    "currency_id": "COP"
                }
            ],
            "back_urls": {
                "success": url_for('views.order', _external=True),
                "failure": url_for('views.home', _external=True),
                "pending": url_for('views.order', _external=True)
            },
            "external_reference": external_ref,
            "payment_methods": {
                "installments": 1 # Evita complicaciones de cuotas en pruebas
            },
            "binary_mode": True # Solo acepta pagos aprobados o rechazados (sin estados intermedios)
        }
        
        # 4. Crear la preferencia en el SDK de Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        
        if preference_response["status"] not in [200, 201]:
            print(f"Error Mercado Pago: {preference_response['response']}")
            flash("No se pudo conectar con la pasarela de pago.")
            return redirect(url_for('views.home'))

        preference = preference_response["response"]

        # 5. Crear los registros de la Orden en la DB antes de redirigir
        for item in customer_cart:
            new_order = Order()
            new_order.quantity = item.quantity
            new_order.price = item.variant.product.current_price
            new_order.status = 'Pending'
            new_order.payment_id = preference['id'] # Guardamos el ID de MP para rastreo
            new_order.customer_link = current_user.id
            new_order.variant_link = item.variant_link 
            
            db.session.add(new_order)
            
            # Limpiar el carrito (ya se convirtió en orden)
            db.session.delete(item)

        db.session.commit()

        # 6. Redirigir al usuario al Checkout Pro de Mercado Pago
        # Se usa 'init_point' para producción o 'sandbox_init_point' para pruebas
        return redirect(preference['init_point'])

    except Exception as e:
        db.session.rollback()
        print(f"Error crítico en Zora (place_order): {str(e)}")
        flash('Ocurrió un problema interno al procesar tu pedido.')
        return redirect(url_for('views.home'))


@views.route('/orders')
@login_required
def order():
    # Mercado Pago envía el resultado por la URL
    status = request.args.get('status')
    payment_id = request.args.get('payment_id')

    if status == 'approved':
        # Aquí buscarías la orden en tu DB con el payment_id y actualizarías su estado
        flash("¡Pago aprobado! Tu pedido está en camino.")
    
    return render_template("orders.html")

@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True).all()
    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    product = Product.query.get_or_404(item_id)
    variant = ProductVariant.query.filter_by(product_id=item_id).first()
    
    if not variant:
        try:
            variant = ProductVariant(
                product_id=item_id,
                sku=f"DEF-{product.id}-{product.reference_code}",
                color="Único",
                size="Estándar",
                stock=product.in_stock
            )
            db.session.add(variant)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('No se pudo procesar el producto', category='error')
            return redirect(url_for('views.home'))

    item_exists = Cart.query.filter_by(variant_link=variant.id, customer_link=current_user.id).first()
    
    try:
        if item_exists:
            item_exists.quantity += 1
            flash(f'Cantidad de {product.product_name} actualizada.', category='success')
        else:
            new_cart_item = Cart(
                quantity=1,
                variant_link=variant.id,
                customer_link=current_user.id
            )
            db.session.add(new_cart_item)
            flash(f'{product.product_name} añadido al carrito.', category='success')
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Error al añadir al carrito', category='error')

    # CORRECCIÓN AQUÍ: Se usa el nombre de la función 'show_cart'
    return redirect(url_for('views.show_cart'))

@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.variant.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount + 200)

@views.route('/pluscart')
@login_required
def plus_cart():
    cart_id = request.args.get('cart_id')
    c = Cart.query.get_or_404(cart_id)
    if c.quantity < c.variant.stock:
        c.quantity += 1
        db.session.commit()
    
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.variant.product.current_price * item.quantity for item in cart)

    return jsonify({
        'quantity': c.quantity,
        'amount': "{:,.0f}".format(amount),
        'total': "{:,.0f}".format(amount + 200),
        'line_total': "{:,.0f}".format(c.variant.product.current_price * c.quantity)
    })

@views.route('/minuscart')
@login_required
def minus_cart():
    cart_id = request.args.get('cart_id')
    c = Cart.query.get_or_404(cart_id)
    if c.quantity > 1:
        c.quantity -= 1
        db.session.commit()

    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.variant.product.current_price * item.quantity for item in cart)
    
    return jsonify({
        'quantity': c.quantity,
        'amount': "{:,.0f}".format(amount),
        'total': "{:,.0f}".format(amount + 200),
        'line_total': "{:,.0f}".format(c.variant.product.current_price * c.quantity)
    })

@views.route('/update-qty-manual')
@login_required
def update_qty_manual():
    cart_id = request.args.get('cart_id')
    new_qty = request.args.get('qty', type=int)
    c = Cart.query.get_or_404(cart_id)
    
    if new_qty and new_qty > 0:
        if new_qty <= c.variant.stock:
            c.quantity = new_qty
        else:
            c.quantity = c.variant.stock
    else:
        c.quantity = 1
    
    db.session.commit()
    
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.variant.product.current_price * item.quantity for item in cart)
    
    return jsonify({
        'quantity': c.quantity,
        'amount': "{:,.0f}".format(amount),
        'total': "{:,.0f}".format(amount + 200),
        'line_total': "{:,.0f}".format(c.variant.product.current_price * c.quantity)
    })

@views.route('/removecart')
@login_required
def remove_cart():
    cart_id = request.args.get('cart_id')
    c = Cart.query.get_or_404(cart_id)
    db.session.delete(c)
    db.session.commit()
    
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.variant.product.current_price * item.quantity for item in cart)
    
    return jsonify({
        'amount': "{:,.0f}".format(amount),
        'total': "{:,.0f}".format(amount + 200 if amount > 0 else 0)
    })


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')