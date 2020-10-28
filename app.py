import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)


@app.route('/')
def hello_world():
    app.logger.info(app.url_map)
    return render_template('index.html')


@app.route('/sender/sign-up')
def sign_up():
    return render_template('sign_up.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=False)
