from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField
from wtforms.validators import DataRequired, length, NumberRange


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Nombre de usuario', validators=[DataRequired(), length(min=3, max=100)])
    password1 = PasswordField('Ingresa tu contraseña', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirma tu contraseña', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Registrarse')

class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar sesión')