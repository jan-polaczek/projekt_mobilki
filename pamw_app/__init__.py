import os
import re
import uuid
import click
from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, flash, session, url_for, \
    Response
from pamw_app.api import api_bp as api_bp, jwt as jwt
from pamw_app.web import web_bp as web_bp
from pamw_app.serializers import ma as ma
import pamw_app.models as models

app = Flask(__name__)

# nie definiuję czasu ważności JWT, bo domyślnie jest on dość krótki (5 minut)
app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DB_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_AUTH_URL_RULE='/api/auth',
        JWT_AUTH_HEADER_PREFIX='BEARER'
    )

models.db.init_app(app)
ma.init_app(app)
jwt.init_app(app)
app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(web_bp, url_prefix='/')

@app.cli.command()
def reset_db():
    click.echo('Resetting database...')
    models.db.drop_all()        
    models.db.create_all()
    models.User.register(username='admin', first_name='Pan', last_name='Admin', password='password', address='Poufne', user_type='sender')
    models.User.register(username='jan', first_name='Jan', last_name="Polaczek", password='password', address='ul. Ulicowa 1/23 01-001 Warszawa', user_type='driver')
    models.Package.register(sender_id = 1, receiver='Odbiorca', cell='WAW-001', size='5kg')
    click.echo('Database reset.')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == '__main__':
    app.run()
    

