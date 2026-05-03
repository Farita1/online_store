from flask import Blueprint, redirect, render_template, request, jsonify, flash
from flask_login import login_required, current_user
from .models import Cart, Product, ProductVariant
from . import db

views = Blueprint('views', __name__)

@views.route('/')
def home():
    items = Product.query.filter_by(flash_sale=True).all()
    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    # 1. Obtener el producto
    product = Product.query.get_or_404(item_id)
    
    # 2. Intentar obtener la primera variante
    variant = ProductVariant.query.filter_by(product_id=item_id).first()
    
    # 3. Si no existe ninguna variante, creamos una por defecto para que funcione el sistema
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
            print(f"Error al crear variante por defecto: {e}")
            flash('No se pudo procesar el producto (falta variante)')
            return redirect(request.referrer)

    # 4. Verificar si ya existe en el carrito
    item_exists = Cart.query.filter_by(variant_link=variant.id, customer_link=current_user.id).first()
    
    if item_exists:
        try:
            item_exists.quantity += 1
            db.session.commit()
            flash(f'¡Cantidad de {product.product_name} actualizada!', category='success')
        except Exception as e:
            db.session.rollback()
            flash('Error al actualizar cantidad', category='error')
    else:
        # 5. Si no existe, crear nuevo item en el carrito ligado a la variante
        new_cart_item = Cart(
            quantity=1,
            variant_link=variant.id,
            customer_link=current_user.id
        )
        try:
            db.session.add(new_cart_item)
            db.session.commit()
            flash(f'¡{product.product_name} añadido al carrito!', category='success')
        except Exception as e:
            db.session.rollback()
            print(f"Error al añadir al carrito: {e}")
            flash('Hubo un problema al añadir el producto')

    return redirect(request.referrer)

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