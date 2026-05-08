from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import DateField, SelectField, StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, length, NumberRange, Optional, EqualTo

class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Nombre de usuario', validators=[DataRequired(), length(min=3, max=100)])
    password1 = PasswordField('Ingresa tu contraseña', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirma tu contraseña', validators=[
        DataRequired(), 
        EqualTo('password1', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Contraseña actual', validators=[DataRequired()])
    new_password = PasswordField('Nueva contraseña', validators=[DataRequired(), length(min=6)])
    confirm_password = PasswordField('Confirma la nueva contraseña', validators=[
        DataRequired(), 
        EqualTo('new_password', message='Las contraseñas deben coincidir')
    ])
    changed_password = SubmitField('Cambiar contraseña')

class ShopItemForm(FlaskForm):
    product_name = StringField('Nombre del producto', 
        validators=[DataRequired(message="El nombre es obligatorio")])

    current_price = FloatField('Precio actual', 
        validators=[DataRequired(), NumberRange(min=0, message="El precio no puede ser negativo")])

    previous_price = FloatField('Precio anterior', 
        validators=[Optional(), NumberRange(min=0)])

    in_stock = IntegerField('Stock disponible', 
        validators=[DataRequired(), NumberRange(min=0)])

    product_picture = FileField('Imagen del producto', 
    validators=[
        Optional(), # Esto es clave
        FileAllowed(['jpg', 'png', 'jpeg', 'webp'], '¡Solo imágenes!')
    ])
    
    flash_sale = BooleanField('¿Es una Oferta Flash?')

    submit = SubmitField('Guardar Producto')


class GymClientForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Teléfono')
    plan_type = SelectField(
        'Tipo de plan',
        choices=[('mensual', 'Mensual'), ('trimestral', 'Trimestral'), ('anual', 'Anual')],
        validators=[DataRequired()]
    )
    start_date = DateField('Fecha inicio', format='%Y-%m-%d')
    end_date = DateField('Fecha fin', format='%Y-%m-%d')
    is_active = BooleanField('Activo')
    submit = SubmitField('Guardar')