from data import db_session
from data.order_items import OrderItem
from flask_restful import Resource, abort, reqparse
from flask import jsonify


parser = reqparse.RequestParser()
parser.add_argument('id_order', type=int, required=True, location="args")
parser.add_argument("id_item", type=int, required=True, location="args")


def abort_if_order_item_not_exists(id_order_item):
    db_sess = db_session.create_session()
    if not db_sess.query(OrderItem).get(id_order_item):
        abort(404, message=f'OrderItem {id_order_item} Not Found')


class OrderItemResource(Resource):
    @staticmethod
    def get(id_order_item):
        abort_if_order_item_not_exists(id_order_item)
        db_sess = db_session.create_session()
        order_item = db_sess.query(OrderItem).get(id_order_item)
        return jsonify({"order_items": order_item.to_dict(only=("id", 'id_order', "id_item"))})

    @staticmethod
    def delete(id_order_item):
        abort_if_order_item_not_exists(id_order_item)
        db_sess = db_session.create_session()
        order_item = db_sess.query(OrderItem).get(id_order_item)
        db_sess.delete(order_item)
        db_sess.commit()
        return jsonify({"success": "OK"})


class OrderItemListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        order_items = db_sess.query(OrderItem).all()
        return jsonify({"order_items": [
            item.to_dict(only=('id', 'id_order', 'id_item')) for item in order_items
        ]})

    @staticmethod
    def post():
        args = parser.parse_args()
        order_item = OrderItem()
        order_item.id_item = args["id_item"]
        order_item.id_order = args["id_order"]
        db_sess = db_session.create_session()
        db_sess.add(order_item)
        db_sess.commit()
        return jsonify({"success": "OK"})
