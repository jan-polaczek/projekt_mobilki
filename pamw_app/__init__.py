import os
import re
import uuid
import click
from flask import Flask, render_template, send_from_directory, request, redirect, jsonify, flash, session, url_for, \
    Response
from pamw_app.api import api_bp as api_bp, jwt as jwt
from flask_cors import CORS, cross_origin
from pamw_app.web import web_bp as web_bp
from pamw_app.serializers import ma as ma
import pamw_app.models as models

app = Flask(__name__)
cors = CORS(app)
# nie definiuję czasu ważności JWT, bo domyślnie jest on dość krótki (5 minut)
app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SECRET_KEY=os.environ.get('FLASK_SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DB_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_AUTH_URL_RULE='/api/auth/',
        JWT_AUTH_HEADER_PREFIX='BEARER',
        CORS_ALLOW_HEADERS='*',
        CORS_METHODS='*',
        CORS_ORIGINS='*'
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
    load_data('data.json')
    click.echo('Database reset.')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


def load_data(path):
    with open(path, 'r') as file:


if __name__ == '__main__':
    app.run()
    

