import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Admin(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'admins'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    login_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    user = orm.relationship("User", back_populates="admins")
