from data import db_session
from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data.items import Item


parser = reqparse.RequestParser()
parser.add_argument("title", required=True, location="args")
parser.add_argument("id_category", type=int, location="args", default=0)
parser.add_argument("img_path", location="args", default='/static/img/default.png')


class ItemResource(Resource):
    @staticmethod
    def get(id_item):
        db_sess = db_session.create_session()
        items = db_sess.query(Item).get(id_item)
        if not items:
            abort(404, message=f"Item {id_item} not found")
        return jsonify({"items": items.to_dict(
            only=("id", "title", "id_category", "img_path"))})

    @staticmethod
    def delete(id_item):
        db_sess = db_session.create_session()
        items = db_sess.query(Item).get(id_item)
        if not items:
            abort(404, message=f"Item {id_item} not found")
        db_sess.delete(items)
        db_sess.commit()
        return jsonify({"success": "OK"})


class ItemListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        items = db_sess.query(Item).all()
        return jsonify({"items": [item.to_dict(
            only=("id", 'title', 'id_category', 'img_path')) for item in items]})

    @staticmethod
    def post():
        args = parser.parse_args()
        item = Item()
        item.set_information(title=args["title"], id_category=args["id_category"], img_path=args["img_path"])
        db_sess = db_session.create_session()
        db_sess.add(item)
        db_sess.commit()
        return jsonify({"success": "OK"})
