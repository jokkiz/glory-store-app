from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request
import datetime
from datetime import datetime as dt
import hashlib
import bleach
from markdown import markdown


class Permissions:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'Пользователь': (Permissions.FOLLOW |
                             Permissions.COMMENT |
                             Permissions.WRITE_ARTICLES, True),
            'Модератор': (Permissions.FOLLOW |
                          Permissions.COMMENT |
                          Permissions.WRITE_ARTICLES |
                          Permissions.MODERATE_COMMENTS, False),
            'Администратор': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class User(UserMixin, db.Model):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    # личные данные
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    middle_name = db.Column(db.String(128))
    birthday = db.Column(db.Date())
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())

    member_since = db.Column(db.DateTime(), default=dt.utcnow())
    last_seen = db.Column(db.DateTime(), default=dt.utcnow())
    avatar_hash = db.Column(db.String(32))
    events_owning = db.relationship('Event', backref='owner', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('Пароль не является атрибутом для чтения')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['GS_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permissions.ADMINISTER)

    def ping(self):
        self.last_seen = dt.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash0 = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash0, size=size,
                                                                     default=default, rating=rating)

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.load(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     first_name=forgery_py.name.first_name(),
                     last_name=forgery_py.name.last_name(),
                     birthday=forgery_py.date.date(True, min_delta=5110, max_delta=18250),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True)
                     )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(64))
    description = db.Column(db.Text)
    description_html = db.Column(db.Text)
    date_begin = db.Column(db.DateTime(), default=dt.utcnow())
    date_end = db.Column(db.DateTime(), default=dt.utcnow())
    location = db.Column(db.String(128))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    amenities = db.relationship('Amenity', backref='')

    @staticmethod
    def generate_fake(count=30):
        from random import seed, randint
        from sqlalchemy.exc import IntegrityError
        import forgery_py

        seed()
        u = User.query.filter_by(username='jokkiz').first()

        for i in range(count):
            date_begin = forgery_py.date.date()
            date_end = date_begin + datetime.timedelta(days=randint(1,5))
            e = Event(short_name=forgery_py.lorem_ipsum.title(1),
                      name=forgery_py.lorem_ipsum.words(3),
                      description=forgery_py.lorem_ipsum.sentence(),
                      date_begin=date_begin,
                      date_end=date_end,
                      location=forgery_py.address.city(),
                      owner=u,
                      amenities=Amenity.query.offset(2))
            db.session.add(e)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    @staticmethod
    def on_changed_description(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol',
                        'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.description_html = bleach.linkify(bleach.clean(
            markdown(value or u'', ouput_format='html'),
            tags=allowed_tags, strip=True))


db.event.listen(Event.description, 'set', Event.on_changed_description)

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Amenity(db.Model):
    __tablename_ = 'amenities'
    id = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(20))
    name = db.Column(db.String(64))
    cost = db.Column(db.Numeric())
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
