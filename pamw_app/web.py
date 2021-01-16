from flask import Blueprint, render_template, request, redirect, jsonify, flash, session, url_for, \
    Response, make_response
import pamw_app.models as models
from functools import update_wrapper
import time
import datetime

from pamw_app.utils import separate_array_by_key

web_bp = Blueprint('web_bp', __name__,
                   template_folder='templates')


def protected(fn):
    def wrapped_function(*args, **kwargs):
        sid = session.get('sid')
        if sid is None:
            return "Unauthorized", 401
        kwargs['user'] = models.Session.query.get(session['sid']).user
        return fn(*args, **kwargs)
    return update_wrapper(wrapped_function, fn)


@web_bp.context_processor
def session_info():
    logged_in = 'sid' in session
    if logged_in:
        try:
            user = models.Session.query.get(session['sid']).user.as_dict()
            oauth = session['oauth']
        except TypeError:
            user = None
            logged_in = False
            oauth = False
            session.clear()
    else:
        user = None
        oauth = False
    return dict(logged_in=logged_in, user=user, oauth=oauth)


@web_bp.route('/')
def index():
    return render_template('index.html')


@web_bp.route('/sender/sign-up')
def sign_up():
    return render_template('sign_up.html')


@web_bp.route('/sender/login')
def login():
    return render_template('login.html')


@web_bp.route('/sender/logout')
def logout():
    models.Session.query.get(session.get('sid')).delete()
    session.clear()
    return redirect(url_for('web_bp.index'))


@web_bp.route('/sender/authorize', methods=['POST'])
def authorize():
    username = request.form.get('username')
    password = request.form.get('password')
    user = models.User.authorize(username, password)
    if user is None or user.user_type != 'sender':
        flash('Niewłaściwa nazwa użytkownika i/lub hasło!')
        return redirect('/sender/login')
    else:
        ses = models.Session.register(user_id=user.id)
        session['sid'] = ses.id
        session['timestamp'] = datetime.datetime.now().timestamp()
        session['oauth'] = False
        return redirect(url_for('web_bp.index'))


@web_bp.route('/sender/register', methods=['POST'])
def register():
    data = request.form.to_dict()
    data['user_type'] = 'sender'
    result = models.User.register(**data)
    if len(result['errors']) == 0:
        return redirect('/sender/login')
    else:
        return render_template('sign_up.html', errors=result['errors'])


@web_bp.route('/sender/check')
def check_username():
    username = request.args.get('username')
    return jsonify(models.User.check_username(username))


@web_bp.route('/sender/dashboard', methods=['GET', 'POST'])
@protected
def packages(**kwargs):
    user = kwargs['user']
    if request.method == 'GET':
        user_packages_all = user.packages
        user_package_labels, user_packages = separate_array_by_key(user_packages_all, 'status', 'Utworzona etykieta')
        return render_template('packages.html', packages=user_packages, labels=user_package_labels)

    elif request.method == 'POST':
        package_data = {
            'sender_id': user.id,
            'receiver': request.form.get('receiver'),
            'cell': request.form.get('cell'),
            'size': request.form.get('size')
        }
        res = models.Package.register(**package_data)
        errors = res['errors']
        if len(errors) > 0:
            return render_template('new_package.html', errors=errors)
        return redirect(url_for('web_bp.packages'))


@web_bp.route('/sender/dashboard/new')
@protected
def new_package(**kwargs):
    return render_template('new_package.html')


@web_bp.route('/notifications/subscribe')
@protected
def subscribe(**kwargs):
    user = kwargs['user']
    return poll_db(user)


def poll_db(user):
    for i in range(25):
        time.sleep(1)
        notifications = models.Notification.get_unread_notifications_for_user(user.id)
        if len(notifications) > 0:
            content = models.Notification.many_as_dict(notifications)
            models.Notification.mark_many_as_read(notifications)
            resp = make_response(content, 200)
            return resp
    return '', 404
