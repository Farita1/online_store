from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_user, login_required, logout_user
from .forms import SignUpForm, LoginForm
from .models import Customer # Asegúrate del punto si está en el mismo paquete
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        customer = Customer.query.filter_by(email=email).first()
        if customer and customer.verify_password(password=password):
            login_user(customer)
            return redirect(url_for('views.home'))
        else:
            flash('Email o contraseña incorrectos. Intenta de nuevo.', category='error')
            
    return render_template('login.html', form=form)

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        
        if password1 == password2:
            # Verificamos si el usuario ya existe para evitar errores de BD
            user_exists = Customer.query.filter_by(email=email).first()
            if user_exists:
                flash('El correo ya está registrado.', category='error')
                return render_template('signup.html', form=form)

            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password1 # Asegúrate que tu modelo encripte esto en el setter
            
            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('¡Cuenta creada con éxito! Ya puedes iniciar sesión.', category='success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                print(e)
                flash('Error al crear la cuenta. Intenta más tarde.', category='error')
        else:
            flash('Las contraseñas no coinciden.', category='error')
            
    return render_template('signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente.', category='success')
    return redirect(url_for('auth.login'))