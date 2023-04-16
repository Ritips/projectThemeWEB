import sqlalchemy.exc
from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.type_of_goods import Category


parser = reqparse.RequestParser()
parser.add_argument("title", required=True, location="args")


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
        return jsonify({"categories": {
            "title": category.title}})

    @staticmethod
    def put(id_category):
        abort_if_category_not_found(id_category)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        try:
            category.title = args["title"]
            db_sess.commit()
            return jsonify({"success": "OK"})
        except sqlalchemy.exc.IntegrityError:
            abort(409, message=f"Category {args['title']} already exists")

    @staticmethod
    def delete(id_category):
        abort_if_category_not_found(id_category)
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        db_sess.delete(category)
        db_sess.commit()
        return jsonify({"success": "OK"})


class CategoryListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        categories = db_sess.query(Category).all()
        return jsonify({"categories": [
                {"title": category.title} for category in categories]})

    @staticmethod
    def post():
        args = parser.parse_args()
        category = Category()
        try:
            category.title = args["title"]
            db_sess = db_session.create_session()
            db_sess.add(category)
            db_sess.commit()
        except sqlalchemy.exc.IntegrityError:
            abort(409, message=f"Category {args['title']} already exists")
        return jsonify({"success": "OK"})
