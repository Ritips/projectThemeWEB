from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.authorisation_log import User


parser = reqparse.RequestParser()
parser.add_argument("login", required=True, location="args")
parser.add_argument("password", required=True, location="args")
parser.add_argument("email", required=True, location="args")
parser.add_argument("name", required=True, location="args")
parser.add_argument("surname", required=True, location="args")
parser.add_argument("phone", location="args")
parser.add_argument("second_email", location="args")


def abort_if_users_not_found(user_id):
    db_sess = db_session.create_session()
    users = db_sess.query(User).get(user_id)
    if not users:
        abort(404, message=f"User {user_id} not found")


def abort_if_email_is_already_used(email):
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter_by(email=email).first()
    if users:
        abort(409, message=f"Email {email} is already used")


def abort_if_phone_is_already_used(phone):
    db_sess = db_session.create_session()
    users = db_sess.query(User).filter_by(phone=phone).first()
    if users:
        abort(409, message=f"Phone {phone} is already used")


class UserResource(Resource):
    @staticmethod
    def get(user_id):
        abort_if_users_not_found(user_id)
        db_sess = db_session.create_session()
        users = db_sess.query(User).get(user_id)
        return jsonify({"users": users.to_dict(only=("id", "login", "name",
                                                     "surname", "email", "phone", "second_email"))})

    @staticmethod
    def delete(user_id):
        abort_if_users_not_found(user_id)
        db_sess = db_session.create_session()
        users = db_sess.query(User).get(user_id)
        db_sess.delete(users)
        db_sess.commit()
        return jsonify({"success": "OK"})


class UserListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        users = db_sess.query(User).all()
        return jsonify({"users": [item.to_dict(only=(
            "id", "login", "name", "surname", "email", "phone", "second_email")) for item in users]})

    @staticmethod
    def post():
        args = parser.parse_args()
        abort_if_email_is_already_used(args["email"])
        if args["phone"]:
            abort_if_phone_is_already_used(args["phone"])
        db_sess = db_session.create_session()
        user = User()
        user.set_information(login=args["login"], email=args["email"], name=args["name"], surname=args["surname"])
        user.set_password(args["password"])
        if args["phone"]:
            user.set_phone(args["phone"])
        if args["second_email"]:
            user.set_second_email(args["second_email"])
        db_sess.add(user)
        db_sess.commit()
        return jsonify({"success": "OK"})
