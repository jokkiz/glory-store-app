from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User



class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Пароль', validators=[Required()])
    remember_me = BooleanField('Запомнить меня?')
    submit = SubmitField('Войти')


class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email('Неверно указан email')])
    username = StringField('Логин',
                           validators=[Required(),
                                       Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                        'Логин должен содержать только буквы, цифры, точки и нижние подчеркивания')])
    password = PasswordField('Пароль', validators=[Required(), EqualTo('password2', 'Пароли должны совпадать')])
    password2 = PasswordField('Повторите пароль', validators=[Required()])
    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Данный Email уже зарегистрирован')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Данный логин уже зарегистрирован')
