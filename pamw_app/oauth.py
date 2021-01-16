import datetime
import os

from authlib.integrations.flask_client import OAuth
from flask import Blueprint, session, redirect, url_for, request

from pamw_app import models
from pamw_app.api import jwt

oauth = OAuth()

auth0 = oauth.register(
    'auth0',
    client_id='OljNoPiMEcR04rFtJohEwcsXke9zQxc2',
    client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
    api_base_url='https://dev-oxz1g2jk.eu.auth0.com',
    access_token_url='https://dev-oxz1g2jk.eu.auth0.com/oauth/token',
    authorize_url='https://dev-oxz1g2jk.eu.auth0.com/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

oauth_bp = Blueprint('oauth_bp', __name__,
                     template_folder='templates')


@oauth_bp.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    user_data = resp.json()
    user = models.User.query.filter_by(username=user_data['nickname']).first()
    if 'api' in request.args:
        handle_api_oauth(user, user_data)
    else:
        if user is None:
            user = register_through_oauth(user_data, 'sender')['user']
        login_through_oauth(user)
        return redirect(url_for('web_bp.index'))


@oauth_bp.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=url_for('oauth_bp.callback_handling', _external=True))


@oauth_bp.route('/logout')
def logout():
    return redirect(f'https://dev-oxz1g2jk.eu.auth0.com/v2/logout?client_id=OljNoPiMEcR04rFtJohEwcsXke9zQxc2&returnTo={url_for("web_bp.logout", _external=True)}')


def register_through_oauth(user_data, user_type):
    new_data = {
        'first_name': user_data['given_name'],
        'last_name': user_data['family_name'],
        'username': user_data['nickname'],
        'oauth': True,
        'user_type': user_type,
        'address': 'undefined',
    }
    return models.User.register(**new_data)


def login_through_oauth(user):
    ses = models.Session.register(user_id=user.id)
    session['sid'] = ses.id
    session['oauth'] = True
    session['timestamp'] = datetime.datetime.now().timestamp()


def handle_api_oauth(user, user_data):
    if user is None:
        user = register_through_oauth(user_data, 'sender')['user']
    token = jwt.jwt_encode_callback(user)
    print(jwt.auth_response_callback(token, user))
    return 'ok', 200


