import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm


class OrderItem(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'order_items'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id_order = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('orders.id'))
    id_item = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("items.id"))

    orders = orm.relationship("Order", back_populates="ordered_items")
    items = orm.relationship("Item", back_populates="orders")
