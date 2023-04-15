from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.admins import Admin
from data.authorisation_log import User


parser = reqparse.RequestParser()
parser.add_argument("login_id", type=int, required=True, location="args")


def abort_if_admin_not_found(admin_id):
    db_sess = db_session.create_session()
    if not db_sess.query(Admin).get(admin_id):
        abort(404, message=f"Admin {admin_id} not Found")


def abort_if_exists(login_id):
    db_sess = db_session.create_session()
    if db_sess.query(Admin).filter_by(login_id=login_id).first():
        abort(409, message=f"Admin {login_id} already exists")


def abort_if_user_not_found(login_id):
    db_sess = db_session.create_session()
    if not db_sess.query(User).filter_by(id=login_id).first():
        abort(404, message=f'User {login_id} not Found')


class AdminResource(Resource):
    @staticmethod
    def get(admin_id):
        abort_if_admin_not_found(admin_id)
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).get(admin_id)
        user = admin.user
        name, surname, email, phone, second_email = user.name, user.surname, user.email, user.phone, user.second_email
        return jsonify({
            "admins": {
                "id": admin.id, "user_id": admin.login_id, "name": name, "surname": surname, "email": email,
                "phone": phone, "second_email": second_email
            }
        })

    @staticmethod
    def put(admin_id):
        abort_if_admin_not_found(admin_id)
        args = parser.parse_args()
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).filter_by(id=admin_id).first()
        if admin.login_id != args["login_id"]:
            abort_if_exists(args["login_id"])
            admin.login_id = args["login_id"]
        db_sess.commit()
        return jsonify({"success": "OK"})

    @staticmethod
    def delete(admin_id):
        abort_if_admin_not_found(admin_id)
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).filter_by(id=admin_id).first()
        db_sess.delete(admin)
        db_sess.commit()
        return jsonify({"success": "OK"})


class AdminListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        admins = db_sess.query(Admin).all()
        return jsonify({
            "admins": [
                {
                    "id": admin.id, "user_id": admin.login_id,
                    "name": admin.user.name, "surname": admin.user.surname, "email": admin.user.email,
                    "phone": admin.user.phone, "second_email": admin.user.second_email
                } for admin in admins
            ]
        })

    @staticmethod
    def post():
        args = parser.parse_args()
        abort_if_exists(args["login_id"])
        abort_if_user_not_found(args["login_id"])
        admin = Admin()
        admin.login_id = args["login_id"]
        db_sess = db_session.create_session()
        db_sess.add(admin)
        db_sess.commit()
        return jsonify({"success": "OK"})
