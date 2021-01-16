from flask_sqlalchemy import SQLAlchemy
import bcrypt
import re
import uuid
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy(engine_options={'isolation_level': 'READ COMMITTED'})


def generate_uuid():
    return str(uuid.uuid4())


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    oauth_id = db.Column(db.String(50), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    password = db.Column(db.String(60))
    username = db.Column(db.String(30))
    address = db.Column(db.String(100))
    user_type = db.Column(db.String(10))
    oauth = db.Column(db.Boolean(), default=False)
    packages = db.relationship('Package', backref='sender', lazy=True)

    def __init__(self, **kwargs):
        if 'password' in kwargs:
            kwargs['password'] = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt())
        super().__init__(**kwargs)

    def check_password(self, password):
        return password and bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def __repr__(self):
        return f'User: {self.username}'

    def as_dict(self):
        res = {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'username': self.username,
            'address': self.address,
            'user_type': self.user_type,
            'packages': []
        }
        for package in self.packages:
            res['packages'].append(package.as_dict())
        return res

    @hybrid_property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @staticmethod
    def authorize(username, password, api=False):
        user = User.query.filter_by(username=username).first()
        if user is None or user.oauth or not user.check_password(password) or api and not user.user_type == 'driver':
            return None
        else:
            return user

    @staticmethod
    def check_username(username):
        res = {}
        if User.query.filter_by(username=username).first() is None:
            res[username] = 'available'
        else:
            res[username] = 'unavailable'
        return res

    @staticmethod
    def register(**kwargs):
        errors = []
        user_data = {}
        if User.is_valid('username', kwargs.get('username', '')):
            user_data['username'] = kwargs.get('username')
        else:
            errors.append('Błędna nazwa użytkownika')
        if User.is_valid('password', kwargs.get('password', '')) or kwargs.get('oauth', False):
            user_data['password'] = kwargs.get('password', '')
        else:
            errors.append('Błędne hasło')
        if User.is_valid('first_name', kwargs.get('first_name', '')):
            user_data['first_name'] = kwargs.get('first_name')
        else:
            errors.append('Błędne imię')
        if User.is_valid('last_name', kwargs.get('last_name', '')):
            user_data['last_name'] = kwargs.get('last_name')
        else:
            errors.append('Błędne nazwisko')
        if User.is_valid('address', kwargs.get('address', '')):
            user_data['address'] = kwargs.get('address')
        else:
            errors.append('Błędny adres')
        if User.check_username(kwargs.get('username'))[kwargs.get('username')] == 'unavailable':
            errors.append('Nazwa użytkownika zajęta')

        user_data['user_type'] = kwargs.get('user_type')

        if len(errors) == 0:
            user = User(**user_data)
            db.session.add(user)
            db.session.commit()
        else:
            user = None
        return {'user': user, 'errors': errors}

    @staticmethod
    def is_valid(field, value):
        PL = 'ĄĆĘŁŃÓŚŹŻ'
        pl = 'ąćęłńóśźż'
        if field == 'first_name':
            return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
        if field == 'last_name':
            return re.compile(f'[A-Z{PL}][a-z{pl}]+').match(value)
        if field == 'password':
            return re.compile('.{8,}').match(value.strip())
        if field == 'username':
            return re.compile('[a-z]{3,12}').match(value)
        if field == 'address':
            return re.compile(f'[a-zA-Z{pl}{PL}0-9\-.]').match(value.strip())
        return False


class Package(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid, unique=True, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver = db.Column(db.String(100))
    cell = db.Column(db.String(7))
    size = db.Column(db.String(30))
    status = db.Column(db.String(20))

    def __init__(self, **kwargs):
        if not kwargs.get('status'):
            self.status = 'Utworzona etykieta'
        super().__init__(**kwargs)

    def __repr__(self):
        return f'Package: sender_id: {self.sender_id}, receiver: {self.receiver}'

    def as_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver': self.receiver,
            'cell': self.cell,
            'size': self.size,
            'status': self.status
        }
    
    def delete(self):
        if self.status == 'Utworzona etykieta':
            db.session.delete(self)
            db.session.commit()
            return True
        else:
            return False

    def increment_status(self):
        statuses = ['Utworzona etykieta', 'Nadana', 'W drodze', 'Dostarczona', 'Odebrana']
        current_status_idx = statuses.index(self.status)
        if current_status_idx == len(statuses) - 1:
            return False
        else:
            self.status = statuses[current_status_idx + 1]
            db.session.commit()
            return True

    @staticmethod
    def register(**kwargs):
        errors = Package.validate(**kwargs)
        if len(errors) == 0:
            p = Package(**kwargs)
            db.session.add(p)
            db.session.commit()
        else:
            p = None
        return {'package': p, 'errors': errors}

    @staticmethod
    def validate(**kwargs):
        PL = 'ĄĆĘŁŃÓŚŹŻ'
        pl = 'ąćęłńóśźż'
        errors = []
        if not re.compile(f'[a-zA-Z{pl}{PL}0-9\-\.,]').match(kwargs.get('receiver', '')):
            errors.append('Niewłaściwy adres odbiorcy.')
        if not re.compile('^[A-Z]{3}-\d{2,3}$').match(kwargs.get('cell', '')):
            errors.append('Niewłaściwy numer skrytki.')
        if not re.compile('^\d{1,10} {0,1}[a-z]{1,10}$').match(kwargs.get('size', '')):
            errors.append('Niewłaściwy rozmiar paczki.')
        if User.query.filter_by(id=kwargs.get('sender_id', -1)).first() is None:
            errors.append('Nie znaleziono nadawcy.')
        return errors


class Session(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    @staticmethod
    def register(**kwargs):
        s = Session(**kwargs)
        db.session.add(s)
        db.session.commit()
        return s


class Notification(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(500))
    timestamp = db.Column(db.DateTime(), default=datetime.now)
    read = db.Column(db.Boolean, default=False)

    user = db.relationship('User')

    def mark_as_read(self):
        self.read = True
        db.session.commit()

    def as_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'read': self.read
        }

    @staticmethod
    def many_as_dict(notifications):
        res = []
        for notification in notifications:
            res.append(notification.as_dict())
        return {'notifications': res}

    @staticmethod
    def register(**kwargs):
        n = Notification(**kwargs)
        db.session.add(n)
        db.session.commit()
        return n

    @staticmethod
    def get_unread_notifications_for_user(user_id):
        return Notification.query.filter_by(user_id=user_id, read=False).all()

    @staticmethod
    def mark_many_as_read(notifications):
        for notification in notifications:
            notification.read = True
        db.session.commit()
