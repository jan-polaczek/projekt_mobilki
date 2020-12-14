from setuptools import setup

setup(
    name='pamw_app',
    packages=['pamw_app'],
    include_package_data=True,
    install_requires=[
        'flask', 'python-dotenv', 'bcrypt', 'flask_sqlalchemy', 'pymysql', 'flask_restful', 'flask-marshmallow', 'marshmallow-sqlalchemy', 'flask_jwt'
    ],
)
