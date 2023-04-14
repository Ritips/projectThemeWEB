import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Item(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "items"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    type_of_goods = sqlalchemy.Column(sqlalchemy.String)
    img_path = sqlalchemy.Column(sqlalchemy.String)
