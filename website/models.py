from . import db
from flask_login import UserMixin
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)

    cart_items = db.relationship('Cart', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    reference_code = db.Column(db.String(50), unique=True)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=True)
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    in_stock = db.Column(db.Integer, default=0)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    variants = db.relationship('ProductVariant', backref='product', lazy=True)


class ProductVariant(db.Model):
    __tablename__ = 'product_variant'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    color = db.Column(db.String(50))
    size = db.Column(db.String(20))
    stock = db.Column(db.Integer, default=0)

    carts = db.relationship('Cart', backref='variant', lazy=True)
    orders = db.relationship('Order', backref='variant', lazy=True)

    def __str__(self):
        return f'<Variant {self.sku}>'


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    variant_link = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)

    def __str__(self):
        return f'<Cart Item {self.id}>'


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    # precio UNITARIO
    price = db.Column(db.Float, nullable=False)

    status = db.Column(db.String(100), nullable=False, default='Pending')
    payment_id = db.Column(db.String(1000), nullable=False)
    date_ordered = db.Column(db.DateTime, default=datetime.utcnow)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    variant_link = db.Column(db.Integer, db.ForeignKey('product_variant.id'), nullable=False)

    @property
    def product(self):
        return self.variant.product

    def __str__(self):
        return f'<Order {self.id}>'


class GymClient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    plan_type = db.Column(db.String(20), nullable=False)  
    monthly_price = db.Column(db.Float, nullable=False)

    payment_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date, nullable=False)

    def is_active(self):
        return self.expiration_date >= date.today()