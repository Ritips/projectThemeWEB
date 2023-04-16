from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.orders import Order
import datetime


parser = reqparse.RequestParser()
parser.add_argument("client_id", type=int, required=True, location="args")
parser.add_argument("date_order", location="args", default=-1)
parser.add_argument("deliver_days", type=int, location="args", default=-1)


def abort_if_wrong_date(date):
    try:
        date_date, date_time = date.split(' ')
        year, month, day = map(int, date_date.split('-'))
        hours, minutes, seconds = map(int, map(lambda x: x.split('.')[0], date_time.split(':')))
        datetime.datetime(year=year, month=month, day=day, hour=hours, minute=minutes, second=seconds)
    except ValueError:
        abort(400, message=f"Wrong date {date}. Format is (%Y-%m-%d %H:%M:%S)")
    except TypeError:
        abort(400, message=f"Wrong date {date}. Format is (%Y-%m-%d %H:%M:%S)")


class OrderResource(Resource):
    @staticmethod
    def get(id_order):
        db_sess = db_session.create_session()
        order = db_sess.query(Order).get(id_order)
        if not order:
            abort(404, message=f'Order {id_order} not Found')
        return jsonify({
            "orders": {
                "id": order.id, "client_id": order.client_id, "date_order": order.date_order,
                "deliver_days": order.deliver_days
            }
        })

    @staticmethod
    def put(id_order):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        order = db_sess.query(Order).get(id_order)
        if not order:
            abort(404, message=f'Order {id_order} not Found')
        order.client_id = args["client_id"]

        if args["date_order"] != -1:
            date = args['date_order']
            try:
                date_date, date_time = date.split(' ')
                year, month, day = map(int, date_date.split('-'))
                hours, minutes, seconds = map(int, map(lambda x: x.split('.')[0], date_time.split(':')))
                datetime.datetime(year=year, month=month, day=day, hour=hours, minute=minutes, second=seconds)
                order.date_order = datetime.datetime(year=year, month=month,
                                                     day=day, hour=hours, minute=minutes, second=seconds)
            except ValueError:
                abort(400, message=f"Wrong date {date}. Format is (%Y-%m-%d %H:%M:%S)")
            except TypeError:
                abort(400, message=f"Wrong date {date}. Format is (%Y-%m-%d %H:%M:%S)")
        if args["deliver_days"] != -1:
            order.deliver_days = args["deliver_days"]
        db_sess.commit()
        return jsonify({"success": "OK"})

    @staticmethod
    def delete(id_order):
        db_sess = db_session.create_session()
        order = db_sess.query(Order).get(id_order)
        if not order:
            abort(404, message=f'Order {id_order} not Found')
        db_sess.delete(order)
        db_sess.commit()
        return jsonify({"success": "OK"})


class OrderListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        orders = db_sess.query(Order).all()
        return jsonify({
            "orders": [
                {"id": order.id, "client_id": order.client_id, "date_order": order.date_order,
                 "deliver_days": order.deliver_days} for order in orders
            ]
        })

    @staticmethod
    def post():
        args = parser.parse_args()
        order = Order()
        order.client_id = args["client_id"]
        if args["date_order"] != -1:
            date = args['date_order']
            try:
                date_date, date_time = date.split(' ')
                year, month, day = map(int, date_date.split('-'))
                hours, minutes, seconds = map(int, map(lambda x: x.split('.')[0], date_time.split(':')))
                datetime.datetime(year=year, month=month, day=day, hour=hours, minute=minutes, second=seconds)
                order.date_order = datetime.datetime(year=year, month=month,
                                                     day=day, hour=hours, minute=minutes, second=seconds)
            except ValueError:
                abort(400, message=f"Wrong date {date}. Format is (%Y-%m-%d %H:%M:%S)")
            except TypeError:
                abort(400, message=f"Wrong date {date}. Format is (%Y-%m-%d %H:%M:%S)")
        if args["deliver_days"] != -1:
            order.deliver_days = args["deliver_days"]
        return jsonify({"success": "OK"})
