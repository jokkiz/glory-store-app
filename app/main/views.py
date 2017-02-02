from datetime import datetime
from time import strftime
from flask import render_template, session, redirect, url_for, abort, flash, request, current_app
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm, EditEventForm, EventForm, AddAmenityForm
from .. import db
from ..models import User, Role, Event, Amenity
from flask_login import login_required, current_user
from ..decorators import admin_required
from sqlalchemy import desc


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
        flash('Профиль был успешно обновлен', 'success')
        return redirect(url_for('.user', username=current_user.username))
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.middle_name.data = current_user.middle_name
    form.birthday.data = current_user.birthday
    form.about_me.data = current_user.about_me
    form.location.data = current_user.location
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.middle_name = form.middle_name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('Профиль был успешно обновлен', 'success')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.middle_name.data = user.middle_name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/edit-event/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(id):
    e = Event.query.get_or_404(id)
    print(e.short_name)
    form = EditEventForm(e)
    if form.validate_on_submit():
        e.short_name = form.short_name.data
        e.name = form.name.data
        e.description = form.description.data
        e.location = form.location.data
        e.date_begin = form.date_begin.data
        e.date_end = form.date_end.data
        db.session.add(e)
        flash('Мероприятие было успешно обновлено', 'success')
        return redirect(url_for('.event', short_name=e.short_name))
    form.short_name.data = e.short_name
    form.name.data = e.name
    form.location.data = e.location
    form.description.data = e.description
    form.date_begin.data = e.date_begin.strftime('%d.%m.%Y %H:%M')
    form.date_end.data = e.date_end.strftime('%d.%m.%Y %H:%M')
    return render_template('edit_event.html', form=form)


@main.route('/events/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    form = EventForm()
    e = Event(short_name=form.short_name.data,
              name=form.name.data,
              description=form.description.data,
              location=form.location.data,
              date_begin=form.date_begin.data,
              date_end=form.date_end.data,
              owner_id=current_user.id)
    if form.validate_on_submit():
        db.session.add(e)
        db.session.commit()
        flash('Событие было успешно добавлено', 'success')
        return redirect(url_for('.event', short_name=form.short_name.data))
    form.short_name.data = e.short_name
    form.name.data = e.name
    form.description.data = e.description
    form.location.data = e.location
    form.date_begin.data = e.date_begin
    form.date_end.data = e.date_end
    return render_template('add_event.html', form=form)


@main.route('/events/<short_name>')
def event(short_name):
    e = Event.query.filter_by(short_name=short_name).first()
    if e is not None:
        u = User.query.filter_by(id=e.owner_id).first()
    else:
        u = None
    return render_template('event.html', event=e, user=u)


@main.route('/events')
def events_list():
    page = request.args.get('page', 1, type=int)
    pagination = Event.query.order_by(Event.date_end.desc()).paginate(
        page, per_page=current_app.config['GS_EVENT_PER_PAGE'], error_out=False
    )

    list_events = pagination.items
    return render_template('events_list.html', events_list=list_events, pagination=pagination)


@main.route('/amenities/add')
@admin_required
def add_amenity(short_name):
    form = AddAmenityForm()
    e = Event.query.filter_by(short_name=short_name).first()
    amenity = Amenity(short_name=form.short_name.data,
                      name=form.name.data,
                      cost=form.cost.data,
                      event=e)
    if form.validate_on_submit():
        db.session.add(amenity)
        db.session.commit()
        flash('Вариант пребывания успешно добавлен', 'success')
        return redirect(url_for('.event', short_name=short_name))
    form.short_name.data = amenity.short_name
    form.name.data = amenity.name
    form.cost.data = amenity.cost
    return render_template('add_amenity.html', form=form)

