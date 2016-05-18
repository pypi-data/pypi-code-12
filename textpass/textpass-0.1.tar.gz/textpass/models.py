import base64
from . import db, app
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
                            db.DateTime,
                            default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp())


class User(Base):

    __tablename__ = 'user'
    __table_args__ = (db.UniqueConstraint('phone'), {})

    phone = db.Column(db.String(128), nullable=False)
    challenge = db.Column(db.String(128), nullable=False)

    def __init__(self, phone, challenge):
        self.phone = phone
        self.challenge = challenge

    def __repr__(self):
        return '<User %r>' % (self.phone)

    def get_or_create(self):
        instance = db.session.query(User).filter_by(phone=self.phone).first()
        if instance:
            instance.challenge = self.challenge
            db.session.commit()
        else:
            instance = self
            db.session.add(instance)
            db.session.commit()
        return instance

    def generate_auth_token(self, expiration=app.config['TOKEN_EXPIRY']):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        encoded_token = base64.b64encode(s.dumps({'phone': self.phone}))
        return encoded_token

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            print 'SignatureExpired'
            return None  # valid token, but expired
        except BadSignature:
            print 'BadSignature'
            return None  # invalid token
        user = User.query.filter_by(phone=data['phone']).first()
        return user

    def serialize(self):
        return {
            'phone': self.phone
        }
