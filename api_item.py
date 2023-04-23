from data import db_session
from flask_restful import Resource, reqparse, abort
from flask import jsonify
from data.items import Item


parser = reqparse.RequestParser()
parser.add_argument('id', type=int, location='args')
parser.add_argument('previous_id', type=int, location='args')
parser.add_argument("title", location="args")
parser.add_argument("id_category", type=int, location="args", default=None)
parser.add_argument("img_path", location="args", default='/static/img/default.png')
parser.add_argument("cost", type=int, location="args")
parser.add_argument("description", location="args", default='-')


class ItemResource(Resource):
    @staticmethod
    def get(id_item):
        db_sess = db_session.create_session()
        items = db_sess.query(Item).get(id_item)
        db_sess.close()
        if not items:
            abort(404, message=f"Item {id_item} not found")
        return jsonify({"items": items.to_dict(
            only=("id", "title", "id_category", "img_path", "cost", "description"))})

    @staticmethod
    def delete(id_item):
        db_sess = db_session.create_session()
        items = db_sess.query(Item).get(id_item)
        if not items:
            abort(404, message=f"Item {id_item} not found")
        db_sess.delete(items)
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": "OK"})

    @staticmethod
    def put(id_item):
        db_sess = db_session.create_session()
        args = parser.parse_args()
        item = db_sess.query(Item).get(args['previous_id'])
        if not item:
            db_sess.close()
            abort(404, message=f"Item {id_item} NOT FOUND")
        item2 = db_sess.query(Item).get(id_item)
        if item2 and args['previous_id'] != id_item:
            db_sess.close()
            abort(409, message=f'Item with id: {args["id"]} already exists')
        item.id, item.title, item.id_category = args['id'], args['title'], args['id_category']
        item.img_path = args['img_path']
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": 'OK'})


class ItemListResource(Resource):
    @staticmethod
    def get():
        args = parser.parse_args()
        db_sess = db_session.create_session()
        if args['id_category'] is None:
            items = db_sess.query(Item).all()
            db_sess.close()
        else:
            items = db_sess.query(Item).filter(Item.id_category == args['id_category']).all()
            db_sess.close()
            if not items:
                abort(404, message=f"{args['id_category']} not Found")
        return jsonify({"items": [item.to_dict(
            only=("id", 'title', 'id_category', 'img_path', "cost", "description")) for item in items]})

    @staticmethod
    def post():
        args = parser.parse_args()
        if args['title'] is None:
            abort(400, message="'title': 'Missing required parameter in the query string'")
        item = Item()
        item.set_information(title=args["title"], id_category=args["id_category"], img_path=args["img_path"])
        db_sess = db_session.create_session()
        db_sess.add(item)
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": "OK"})
