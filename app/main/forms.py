from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, DateField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Role, User


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(Form):
    first_name = StringField('Имя', validators=[Length(0, 128)])
    last_name = StringField('Фамилия', validators=[Length(0, 128)])
    middle_name = StringField('Отчество', validators=[Length(0, 128)])
    birthday = DateField('День рождения', format="%d/%m/%Y")
    about_me = TextAreaField('Обо мне')
    location = StringField('Местонахождение', validators=[Length(3, 64)])
    submit = SubmitField('Подтвердить')
