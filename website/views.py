from flask import Blueprint, redirect, render_template, request, flash, url_for
from flask_login import login_required, current_user
from .models import Cart, Order, Product, ProductVariant
from . import db

import mercadopago
import uuid
import os
import json
from dotenv import load_dotenv

load_dotenv()

views = Blueprint('views', __name__)

sdk = mercadopago.SDK(os.getenv("MP_ACCESS_TOKEN"))


@views.route('/place-order')
@login_required
def place_order():

    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()

    if not customer_cart:
        flash('Tu carrito está vacío', category='warning')
        return redirect(url_for('views.home'))

    total = sum(item.variant.product.current_price * item.quantity for item in customer_cart)
    total = int(total)

    preference_data = {
        "items": [{
            "title": "Compra en Zora Store",
            "quantity": 1,
            "unit_price": total,
            "currency_id": "COP"
        }],
        "back_urls": {
                "success": "https://justifier-likeness-wolf.ngrok-free.dev/payment-success",
            "failure": "https://justifier-likeness-wolf.ngrok-free.dev/",
            "pending": "https://justifier-likeness-wolf.ngrok-free.dev/orders"
        },
        "binary_mode": True,
        "payment_methods": {
            "installments": 1,
            "excluded_payment_types": [{"id": "ticket"}]
        }
    }

    response = sdk.preference().create(preference_data)

    checkout_url = response["response"].get("init_point")
    return redirect(checkout_url)

@views.route('/payment-success')
@login_required
def payment_success():

    payment_id = request.args.get('payment_id') or request.args.get('collection_id')

    if not payment_id:
        flash('Pago inválido', category='error')
        return redirect(url_for('views.home'))

    payment_info = sdk.payment().get(payment_id)
    payment = payment_info["response"]

    if payment.get("status") != "approved":
        flash('El pago no fue aprobado', category='warning')
        return redirect(url_for('views.orders'))

    existing_order = Order.query.filter_by(payment_id=str(payment_id)).first()
    if existing_order:
        flash('La orden ya fue procesada', category='info')
        return redirect(url_for('views.orders'))

    cart_items = Cart.query.filter_by(customer_link=current_user.id).all()

    for item in cart_items:
        order = Order(
            quantity=item.quantity,
            price=item.variant.product.current_price,
            status='Paid',
            payment_id=str(payment_id),
            customer_link=current_user.id,
            variant_link=item.variant_link
        )
        db.session.add(order)

        item.variant.stock -= item.quantity
        db.session.delete(item)

    db.session.commit()

    flash('¡Pago aprobado! Tu pedido está en camino.', category='success')
    return redirect(url_for('views.orders'))

@views.route('/orders')
@login_required
def orders():
    orders = Order.query.filter_by(
        customer_link=current_user.id
    ).order_by(Order.date_ordered.desc()).all()

    return render_template("orders.html", orders=orders)


@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True).all()
    cart = Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
    return render_template('home.html', items=items, cart=cart)


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):

    product = Product.query.get_or_404(item_id)
    variant = ProductVariant.query.filter_by(product_id=item_id).first()

    if not variant:
        variant = ProductVariant(
            product_id=item_id,
            sku=f"DEF-{product.id}-{product.reference_code}",
            color="Único",
            size="Estándar",
            stock=product.in_stock
        )
        db.session.add(variant)
        db.session.commit()

    cart_item = Cart.query.filter_by(
        variant_link=variant.id,
        customer_link=current_user.id
    ).first()

    if cart_item:
        if cart_item.quantity < variant.stock:
            cart_item.quantity += 1
        else:
            flash('No hay más stock disponible', category='warning')
            return redirect(url_for('views.show_cart'))
    else:
        db.session.add(Cart(
            quantity=1,
            variant_link=variant.id,
            customer_link=current_user.id
        ))

    db.session.commit()
    flash(f'{product.product_name} añadido al carrito.', category='success')
    return redirect(url_for('views.show_cart'))


@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = sum(item.variant.product.current_price * item.quantity for item in cart)
    return render_template('cart.html', cart=cart, amount=amount, total=amount + 200)