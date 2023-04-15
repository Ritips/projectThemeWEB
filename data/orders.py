import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
import datetime


class Order(SqlAlchemyBase, SerializerMixin):
    __tablename__ = "orders"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    client_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("clients.id"))
    date_order = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())
    deliver_days = sqlalchemy.Column(sqlalchemy.Integer, default=30)

    client = orm.relationship("Client", back_populates="orders")
    ordered_items = orm.relationship("OrderItem", back_populates="orders")
