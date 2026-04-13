from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    cart_items = db.relationship('Cart', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return f'<Customer {self.username}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(50), unique=True) # Ej: Ref. 091058
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación con las variantes
    variants = db.relationship('ProductVariant', backref='product', lazy=True)

    def __str__(self):
        return f'<Product {self.product_name}>'

class ProductVariant(db.Model):
    """Aquí es donde vive el catálogo tipo Leonisa (SKUs)"""
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    
    sku = db.Column(db.String(50), unique=True, nullable=False) # El número de 5 dígitos (ej: 40261)
    color = db.Column(db.String(50))
    size = db.Column(db.String(20))
    stock = db.Column(db.Integer, default=0)

    # El carrito y las órdenes ahora apuntan a la VARIANTE exacta
    carts = db.relationship('Cart', backref='variant', lazy=True)
    orders = db.relationship('Order', backref='variant', lazy=True)

    def __str__(self):
        return f'<Variant {self.sku} - {self.color}/{self.size}>'

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    # Cambiamos product_link por variant_link
    variant_link = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)

    def __str__(self):
        return f'<Cart Item {self.id}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False, default='Pending')
    payment_id = db.Column(db.String(1000), nullable=False)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    # Cambiamos product_link por variant_link
    variant_link = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)

    def __str__(self):
        return f'<Order {self.id}>'