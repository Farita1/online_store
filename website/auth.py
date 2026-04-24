from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, login_required, logout_user
from .forms import PasswordChangeForm, SignUpForm, LoginForm
from .models import Customer, Product 
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
            user_exists = Customer.query.filter_by(email=email).first()
            if user_exists:
                flash('El correo ya está registrado.', category='error')
                return render_template('signup.html', form=form)

            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password1 
            
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

@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    # 1. Verificamos si el usuario actual es el Administrador (ID 1)
    if current_user.id == 1:
        # Obtenemos los productos para mostrar el conteo en las stats del dashboard
        items = Product.query.all() 
        return render_template('admin_profile.html', customer=current_user, items=items)

    # 2. Si no es admin, cargamos el perfil de cliente normal
    customer = Customer.query.get_or_404(customer_id)
    
    # Seguridad: Evitar que un usuario vea el perfil de otro (opcional pero recomendado)
    if current_user.id != customer.id:
        return redirect(url_for('auth.profile', customer_id=current_user.id))
        
    return render_template('profile.html', customer=customer)


@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    # Seguridad: solo el dueño de la cuenta puede cambiar su propia clave
    if current_user.id != customer_id:
        flash('No tienes permiso para realizar esta acción.', category='error')
        return redirect(url_for('views.home'))

    customer = Customer.query.get_or_404(customer_id)
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        
        if not customer.verify_password(current_password):
            flash('La contraseña actual es incorrecta.', category='error')
        elif new_password != confirm_password:
            flash('Las nuevas contraseñas no coinciden.', category='error')
        else:
            try:
                customer.password = new_password 
                db.session.commit()
                flash('Contraseña cambiada exitosamente.', category='success')
                return redirect(url_for('auth.profile', customer_id=customer.id))
            except Exception as e:
                db.session.rollback()
                flash('Error al actualizar la base de datos.', category='error')
    
    # Pasamos 'customer' para que el HTML pueda usar sus datos si es necesario
    return render_template('change_password.html', form=form, customer=customer)