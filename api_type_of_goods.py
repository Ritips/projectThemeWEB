import sqlalchemy.exc
from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.type_of_goods import Category


parser = reqparse.RequestParser()
parser.add_argument("title", required=True, location="args")
parser.add_argument("id", type=int, required=False, location='args')


def abort_if_category_not_found(id_category):
    db_sess = db_session.create_session()
    if not db_sess.query(Category).get(id_category):
        abort(404, message=f"Category {id_category} not Found")


class CategoryResource(Resource):
    @staticmethod
    def get(id_category):
        abort_if_category_not_found(id_category)
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        db_sess.close()
        return jsonify({"categories": category.to_dict(only=('id', 'title'))})

    @staticmethod
    def put(id_category):
        abort_if_category_not_found(id_category)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        category2 = db_sess.query(Category).get(args['id'])
        if category2 and category != category2:
            db_sess.close()
            abort(409, message=f"Category {args['id']} already exists")
        try:
            category.title = args["title"]
            category.id = args["id"]
            db_sess.commit()
            db_sess.close()
            return jsonify({"success": "OK"})
        except sqlalchemy.exc.IntegrityError:
            db_sess.close()
            abort(409, message=f"Category {args['title']} already exists")

    @staticmethod
    def delete(id_category):
        abort_if_category_not_found(id_category)
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        db_sess.delete(category)
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": "OK"})


class CategoryListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        categories = db_sess.query(Category).all()
        db_sess.close()
        return jsonify({"categories": [category.to_dict(only=('id', 'title')) for category in categories]})

    @staticmethod
    def post():
        args = parser.parse_args()
        category = Category()
        db_sess = db_session.create_session()
        try:
            category.title = args["title"]
            db_sess.add(category)
            db_sess.commit()
            db_sess.close()
        except sqlalchemy.exc.IntegrityError:
            db_sess.close()
            abort(409, message=f"Category {args['title']} already exists")
        return jsonify({"success": "OK"})
