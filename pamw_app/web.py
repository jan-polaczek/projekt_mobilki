from flask import Blueprint, render_template, request, redirect, jsonify, flash, session, url_for, \
    Response
import pamw_app.models as models
import datetime

from pamw_app.utils import separate_array_by_key

web_bp = Blueprint('web_bp', __name__,
                   template_folder='templates')


@web_bp.context_processor
def session_info():
    logged_in = 'sid' in session
    if logged_in:
        try:
            user = models.Session.query.get(session['sid']).user.as_dict()
        except TypeError:
            user = None
            logged_in = False
            session.clear()
    else:
        user = None
    return dict(logged_in=logged_in, user=user)


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
def packages():
    sid = session.get('sid')
    if sid is not None:
        user = models.Session.query.get(sid).user
    if request.method == 'GET':
        if sid is None:
            return redirect(url_for('web_bp.index'))
        user_packages_all = user.packages
        user_package_labels, user_packages = separate_array_by_key(user_packages_all, 'status', 'Utworzona etykieta')
        return render_template('packages.html', packages=user_packages, labels=user_package_labels)
    elif request.method == 'POST':
        if sid is None:
            return Response(status=401)

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
def new_package():
    sid = session.get('sid')
    if sid is None:
        return redirect(url_for('web_bp.index'))
    else:
        return render_template('new_package.html')
