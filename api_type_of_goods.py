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


def abort_if_category_exists(title):
    db_sess = db_session.create_session()
    if db_sess.query(Category).filter_by(title=title).first():
        abort(409, message=f"Category {title} already exists")


class CategoryResource(Resource):
    @staticmethod
    def get(id_category):
        abort_if_category_not_found(id_category)
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        products = category.products
        return jsonify({"categories": {
            "title": category.title,
            "products": [item.to_dict(
                only=("title", "id_category", "img_path")) for item in products]}})

    @staticmethod
    def put(id_category):
        abort_if_category_not_found(id_category)
        args = parser.parse_args()
        abort_if_category_exists(args["title"])
        db_sess = db_session.create_session()
        category = db_sess.query(Category).get(id_category)
        category.title = args["title"]
        db_sess.commit()
        return jsonify({"success": "OK"})

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
        return jsonify({
            "categories": [
                {"title": category.title,
                 "products": [item.to_dict(
                     only=("title", "id_category", "img_path")
                 ) for item in category.products]} for category in categories]})

    @staticmethod
    def post():
        args = parser.parse_args()
        abort_if_category_exists(args["title"])
        category = Category()
        category.title = args["title"]
        db_sess = db_session.create_session()
        db_sess.add(category)
        db_sess.commit()
        return jsonify({"success": "OK"})
