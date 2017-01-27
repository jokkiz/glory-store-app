from flask_wtf import Form
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, DateTimeField, DecimalField
from wtforms.fields.html5 import DateField, DateTimeLocalField # , DateTimeField
from wtforms.validators import Required, Length, Email, Regexp, Optional
from wtforms import ValidationError
from ..models import Role, User, Event
from flask_pagedown.fields import PageDownField


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


class EditProfileForm(Form):
    first_name = StringField('Имя', validators=[Required(),
                                                Length(2, 128,
                                                       message="Имя не может быть короче 2 и длинее 128 символов")])
    last_name = StringField('Фамилия',
                            validators=[Required(),
                                        Length(2, 128,
                                               message="Фамилия не может быть короче 2 и длинее 128 символов")])
    middle_name = StringField('Отчество',
                              validators=[Required(),
                                          Length(1, 128,
                                          message="Отчество не может быть короче 1 и длинее 128 символов")])
    birthday = DateField('День рождения', format="%Y-%m-%d")
    about_me = PageDownField('Обо мне')
    location = StringField('Местонахождение',
                           validators=[Length(3, 64,
                                              message="Длина местонахождения должна быть от 3 до 64 символов")])
    submit = SubmitField('Подтвердить')


class EditProfileAdminForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Логин',
                           validators=[Required(),
                                       Length(1, 64),
                                       Regexp('^[A-Za-z][A-Za-z0-9_.]*$'), 0,
                                              'Логин должен содержать только буквы, цифры, точки и нижние подчеркивания'])
    confirmed = BooleanField('Подтверждение регистрации')
    role = SelectField('Роль', coerce=int)
    first_name = StringField('Имя',
                             validators=[Required(), Length(1, 128, message="Имя должно быть от 1 до 128 символов")])
    last_name = StringField('Фамилия',
                            validators=[Required(), Length(1, 128, message="Фамилия должна быть от 1 до 128 символов")])
    middle_name = StringField('Отчество',
                              validators=[Length(1, 128, message="Отчество должно быть от 1 до 128 символов")])
    birthday = DateField('День рождения', format='%Y-%m-%d')
    about_me = PageDownField('Обо мне')
    location = StringField('Местонахождение',
                           validators=[Length(3, 64,
                                              message="Длина местонахождения должна быть от 3 до 64 символов")])
    submit = SubmitField('Подтвердить')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Данный email уже зарегистрирован')

    def validate_username(self, field):
        if field.data != self.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Пользователь с данным логином уже существует')


class EditEventForm(Form):
    short_name = StringField('Краткое наименование',
                             validators=[Required(message="Данное поле является обязательным для заполнения"),
                                         Length(2, 20, message="Длина короткого наименования мероприятия должна быть от 2 до 20 символов"),
                                         Regexp('[А-Яа-яA-Za-z0-9_]*$', 0, 'Короткое наименование может содержать только буквы, цифры и нижние подчеркивания')])
    name = StringField('Полное наименование',
                       validators=[Required(message="Данное поле является обязательным для заполнения"),
                                   Length(2, 64, message="Длина полного наименования мероприятия должна быть от 2 до 64 символов")])
    description = PageDownField('Описание мероприятия')
    date_begin = DateTimeField('Дата начала мероприятия', format="%d.%m.%Y %H:%M", validators=[Optional()])
    date_end = DateTimeField('Дата окончания мероприятия', format="%d.%m.%Y %H:%M", validators=[Optional()])
    location = StringField('Место проведения', validators=[Length(0, 64, message="Длина строки места проведения должна не превышать 64 символа")])
    submit = SubmitField('Изменить мероприятие')

    def __init__(self, event, *args, **kwargs):
        super(EditEventForm, self).__init__(*args, **kwargs)
        self.event = event

    def validate_short_name(self, field):
        if field.data != self.event.short_name and Event.query.filter_by(short_name=field.data).first():
            raise ValidationError('Мероприятие с данным коротким наименованием уже существует')


class EventForm(Form):
    short_name = StringField('Краткое наименование',
                             validators=[Required(message="Данное поле является обязательным для заполнения"),
                                         Length(2, 20, message="Длина короткого наименования мероприятия должна быть от 2 до 20 символов"),
                                         Regexp('[А-Яа-яA-Za-z0-9_]*$', 0, 'Короткое наименование может содержать только буквы, цифры и нижние подчеркивания')])
    name = StringField('Полное наименование',
                       validators=[Required(message="Данное поле является обязательным для заполнения"),
                                   Length(2, 64, message="Длина полного наименования мероприятия должна быть от 2 до 64 символов")])
    description = PageDownField('Описание мероприятия')
    date_begin = DateTimeField('Дата начала мероприятия', format="%d.%m.%Y %H:%M", validators=[Optional()])
    date_end = DateTimeField('Дата окончания мероприятия', format="%d.%m.%Y %H:%M", validators=[Optional()])
    location = StringField('Место проведения', validators=[Length(0, 64, message="Длина строки места проведения должна не превышать 64 символа")])
    submit = SubmitField('Добавить мероприятие')


class AddAmenityForm(Form):
    short_name = StringField('Вариант мероприятия', validators=[Required(message="Данное поле является обязательным для заполнения"),
                                                                Length(2, 20, message="Длина поля должна быть от 2 до 20 символов")])
    name = StringField('Описание', validators=[Length(2, 64, message="Длина поля должна быть от 2 до 64 символов")])
    cost = DecimalField('Цена')
    submit = SubmitField('Добавить вариант пребывания')
