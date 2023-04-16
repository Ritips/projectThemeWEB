import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy import orm
import datetime


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, unique=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    surname = sqlalchemy.Column(sqlalchemy.String)
    phone = sqlalchemy.Column(sqlalchemy.String, unique=True)
    second_email = sqlalchemy.Column(sqlalchemy.String)
    date_log_in = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    clients = orm.relationship("Client", back_populates='user')
    admins = orm.relationship("Admin", back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_information(self, login, email, name, surname):
        self.login, self.email, self.name, self.surname = login, email, name, surname

    def set_phone(self, phone):
        self.phone = phone

    def set_second_email(self, email):
        self.second_email = email
