import os
import re
import uuid
from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, flash, session, url_for, \
    Response
import bcrypt
import datetime

app = Flask(__name__)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY')
)

import pamw_app.models as models

@app.context_processor
def session_info():
    logged_in = 'sid' in session
    print(session)
    if logged_in:
        try:
            user = models.Session.query.get(session['sid']).user.as_dict()
            print(user)
        except TypeError:
            user = None
            logged_in = False
            session.clear()
    else:
        user = None
    return dict(logged_in=logged_in, user=user)

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
    models.Session.query.get(session.get('sid')).delete()
    session.clear()
    return redirect(url_for('index'))


@app.route('/sender/authorize', methods=['POST'])
def authorize():
    username = request.form.get('username')
    password = request.form.get('password')
    if not models.User.authorize(username, password):
        flash('Niewłaściwa nazwa użytkownika i/lub hasło!')
        return redirect('/sender/login')
    else:
        user = models.User.query.filter_by(username=username).first()
        ses = models.Session.register(user_id=user.id)
        session['sid'] = ses.id
        session['timestamp'] = datetime.datetime.now().timestamp()
        print(session)
        return redirect(url_for('index'))


@app.route('/sender/register', methods=['POST'])
def register():
    data = request.form.to_dict()
    result = models.User.register(**data)
    if len(result['errors']) == 0:
        return redirect('/sender/login')
    else:
        return render_template('sign_up.html', errors=result['errors'])


@app.route('/sender/check')
def check_username():
    username = request.args.get('username')
    return jsonify(models.User.check_username(username))


@app.route('/sender/dashboard', methods=['GET', 'POST'])
def packages():
    sid = session.get('sid')
    if sid is not None:
        user = models.Session.query.get(sid).user
        user_packages = user.packages
    if request.method == 'GET':
        if sid is None:
            return redirect(url_for('index'))
        return render_template('packages.html', packages=user_packages)
    elif request.method == 'POST':
        if sid is None:
            return Response(status=401)
        
        package_data = {
            'id': str(uuid.uuid4()),
            'sender_id': user.id,
            'receiver': request.form.get('receiver'),
            'cell': request.form.get('cell'),
            'size': request.form.get('size')
        }
        res = models.Package.register(**package_data)
        errors = res['errors']
        if len(errors) > 0:
            return render_template('new_package.html', errors=errors)
        return redirect(url_for('packages'))


@app.route('/sender/dashboard/<package_id>', methods=['DELETE'])
def package(package_id):
    models.Package.query.get(package_id).delete()
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
    app.run(ssl_context='adhoc')

