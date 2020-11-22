import os
import re
import uuid
from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, flash, session, url_for, \
    Response
import bcrypt
import datetime
from db.redis_dao import RedisDAO

app = Flask(__name__)


@app.context_processor
def session_info():
    logged_in = 'sid' in session
    if logged_in:
        try:
            user = dao.get_current_user(session['sid'])
        except TypeError:
            user = None
            logged_in = False
            session.clear()
    else:
        user = None
    return dict(logged_in=logged_in, user=user)


app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY')
)
dao = RedisDAO()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/sender/sign-up')
def sign_up():
    return render_template('sign_up.html')


@app.route('/sender/login')
def login():
    return render_template('login.html')


@app.route('/sender/logout')
def logout():
    dao.delete_session(session.get('sid'))
    session.clear()
    return redirect(url_for('index'))


@app.route('/sender/authorize', methods=['POST'])
def authorize():
    username = request.form.get('username')
    unhashed_password = request.form.get('password')
    password = dao.get_password(username)
    if not password or not bcrypt.checkpw(unhashed_password.encode('utf-8'), password.encode('utf-8')):
        flash('Niewłaściwa nazwa użytkownika i/lub hasło!')
        return redirect('/sender/login')
    else:
        sid = str(uuid.uuid4())
        dao.set_session(sid, username)
        session['sid'] = sid
        session['timestamp'] = datetime.datetime.now().timestamp()
        return redirect(url_for('index'))


@app.route('/sender/register', methods=['POST'])
def register():
    form = request.form
    errors = []
    user_data = {}
    if is_valid('username', form.get('username')):
        user_data['username'] = form.get('username')
    else:
        errors.append('Błędna nazwa użytkownika')
    if is_valid('password', form.get('password')):
        user_data['password'] = bcrypt.hashpw(form.get('password').encode('utf-8'), bcrypt.gensalt())
    else:
        errors.append('Błędne hasło')
    if is_valid('firstname', form.get('firstname')):
        user_data['firstname'] = form.get('firstname')
    else:
        errors.append('Błędne imię')
    if is_valid('lastname', form.get('lastname')):
        user_data['lastname'] = form.get('lastname')
    else:
        errors.append('Błędne nazwisko')
    if is_valid('address', form.get('address')):
        user_data['address'] = form.get('address')
    else:
        errors.append('Błędny adres')
    if dao.check_username(form.get('username'))[form.get('username')] == 'unavailable':
        errors.append('Nazwa użytkownika zajęta')

    if len(errors) == 0:
        dao.register(user_data)
        return redirect('/sender/login')
    else:
        return render_template('sign_up.html', errors=errors)


@app.route('/sender/check')
def check_username():
    username = request.args.get('username')
    return jsonify(dao.check_username(username))


@app.route('/sender/dashboard', methods=['GET', 'POST'])
def packages():
    sid = session.get('sid')
    if sid is not None:
        username = dao.get_username(sid)
        user_packages = dao.get_packages(username)
    if request.method == 'GET':
        if sid is None:
            return redirect(url_for('index'))
        return render_template('packages.html', packages=user_packages)
    elif request.method == 'POST':
        if sid is None:
            return Response(status=401)
        errors = validate_package(request.form)
        if len(errors) > 0:
            return render_template('new_package.html', errors=errors)
        package_data = {
            'id': str(uuid.uuid4()),
            'receiver': request.form.get('receiver'),
            'cell': request.form.get('cell'),
            'size': request.form.get('size')
        }
        dao.create_package(username, package_data)
        return redirect(url_for('packages'))


@app.route('/sender/dashboard/<package_id>', methods=['DELETE'])
def package(package_id):
    dao.delete_package(package_id)
    return Response(status=200)


@app.route('/sender/dashboard/new')
def new_package():
    sid = session.get('sid')
    if sid is None:
        return redirect(url_for('index'))
    else:
        return render_template('new_package.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=False)


def is_valid(field, value):
    PL = 'ĄĆĘŁŃÓŚŹŻ'
    pl = 'ąćęłńóśźż'
    if field == 'firstname':
        return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
    if field == 'lastname':
        return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
    if field == 'password':
        return re.compile('.{8,}').match(value.strip())
    if field == 'username':
        return re.compile('[a-z]{3,12}').match(value)
    if field == 'address':
        return re.compile(f'[a-zA-Z{pl}{PL}0-9\-.]').match(value.strip())
    return False


def validate_package(form):
    PL = 'ĄĆĘŁŃÓŚŹŻ'
    pl = 'ąćęłńóśźż'
    errors = []
    if not re.compile(f'[a-zA-Z{pl}{PL}0-9\-\.,]').match(form.get('receiver')):
        errors.append('Niewłaściwy adres odbiorcy.')
    if not re.compile('^[A-Z]{3}-\d{2,3}$').match(form.get('cell')):
        errors.append('Niewłaściwy numer skrytki.')
    if not re.compile('^\d{1,10} {0,1}[a-z]{1,10}$').match(form.get('size')):
        errors.append('Niewłaściwy rozmiar paczki.')
    return errors
