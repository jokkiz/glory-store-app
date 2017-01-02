from datetime import datetime
from flask import render_template, session, redirect, url_for, abort, flash
from . import main
from .forms import NameForm, EditProfileForm
from .. import db
from ..models import User
from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.middle_name = form.middle_name.data
        current_user.about_me = form.about_me.data
        current_user.location = form.location.data
        current_user.birthday = form.birthday.data
        db.session.add(current_user)
        flash('Профиль был обновлен', 'info')
        return redirect(url_for('.user', username=current_user.username))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.middle_name.data = current_user.middle_name
    form.birthday.data = current_user.birthday
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    return render_template('edit_profile.html', form=form)

