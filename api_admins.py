import sqlalchemy.exc
from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.admins import Admin


parser = reqparse.RequestParser()
parser.add_argument("login_id", type=int, required=True, location="args")


class AdminResource(Resource):
    @staticmethod
    def get(admin_id):
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).get(admin_id)
        db_sess.close()
        if not admin:
            abort(404, message=f"Admin {admin_id} not Found")
        return jsonify({
            "admins": {
                "id": admin.id, "user_id": admin.login_id
            }
        })

    @staticmethod
    def put(admin_id):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).get(admin_id)
        if not admin:
            db_sess.close()
            abort(404, message=f"Admin {admin_id} not Found")
        try:
            admin.login_id = args["login_id"]
            db_sess.commit()
            db_sess.close()
            return jsonify({"success": "OK"})
        except sqlalchemy.exc.IntegrityError:
            db_sess.close()
            abort(409, message=f"Admin {args['login_id']} already exists")

    @staticmethod
    def delete(admin_id):
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).get(admin_id)
        if not admin:
            db_sess.close()
            abort(404, message=f"Admin {admin_id} not Found")
        db_sess.delete(admin)
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": "OK"})


class AdminListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        admins = db_sess.query(Admin).all()
        db_sess.close()
        return jsonify({
            "admins": [
                {
                    "id": admin.id, "user_id": admin.login_id,
                } for admin in admins
            ]
        })

    @staticmethod
    def post():
        args = parser.parse_args()
        db_sess = db_session.create_session()
        try:
            admin = Admin()
            admin.login_id = args["login_id"]
            db_sess.add(admin)
            db_sess.commit()
            db_sess.close()
            return jsonify({"success": "OK"})
        except sqlalchemy.exc.IntegrityError:
            db_sess.close()
            abort(409, message=f"Admin {args['login_id']} already exists")
