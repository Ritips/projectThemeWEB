import sqlalchemy.exc
from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.authorisation_log import User
from data.clients import Client
import tools


parser = reqparse.RequestParser()
parser.add_argument("login", required=True, location="args")
parser.add_argument("password", required=True, location="args")
parser.add_argument("email", required=True, location="args")
parser.add_argument("name", required=True, location="args")
parser.add_argument("surname", required=True, location="args")
parser.add_argument("phone", location="args")
parser.add_argument("second_email", location="args")


class UserResource(Resource):
    @staticmethod
    def get(user_id):
        db_sess = db_session.create_session()
        users = db_sess.query(User).get(user_id)
        if not users:
            abort(404, message=f"User {user_id} not found")
        return jsonify({"users": users.to_dict(only=("id", "login", "name",
                                                     "surname", "email", "phone", "second_email"))})

    @staticmethod
    def delete(user_id):
        db_sess = db_session.create_session()
        users = db_sess.query(User).get(user_id)
        if not users:
            abort(404, message=f"User {user_id} not found")
        db_sess.delete(users)
        db_sess.commit()
        return jsonify({"success": "OK"})

    @staticmethod
    def put(user_id):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(user_id)
        if not user:
            abort(404, message=f"User {user_id} not found")
        if user.login != args["login"]:
            user.login = args["login"]
        if user.email != args["email"]:
            user.email = args["email"]
        if args["phone"] and user.phone != args["phone"]:
            user.phone = args["phone"]
        if args["second_email"]:
            user.second_email = args["second_email"]
        user.name, user.surname = args["name"], args["surname"]
        user.set_password(args["password"])
        try:
            db_sess.commit()
        except sqlalchemy.exc.IntegrityError as er:
            text = str(er.args)
            if 'login' in text:
                text = f'Login {args["login"]} is already used'
            elif 'email' in text:
                text = f'Email {args["email"]} is already used'
            elif 'phone' in text:
                text = f'Phone {args["phone"]} is already used'
            abort(409, message=text)
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
        db_sess = db_session.create_session()
        user = User()
        user.login = args['login']
        dec_email = tools.decrypt_password(args['email'])
        user.email = dec_email
        user.name, user.surname = args['name'], args['surname']
        dec_password = tools.decrypt_password(args['password'])
        user.set_password(dec_password)
        if args["phone"]:
            user.phone = args['phone']
        if args["second_email"]:
            user.set_second_email(args["second_email"])
        client = Client()
        client.user = user
        db_sess.add(client)
        try:
            db_sess.add(user)
            db_sess.commit()
        except sqlalchemy.exc.IntegrityError as er:
            text = str(er.args)
            if 'login' in text:
                text = f'Login {args["login"]} is already used'
            elif 'email' in text:
                text = f'Email {args["email"]} is already used'
            elif 'phone' in text:
                text = f'Phone {args["phone"]} is already used'
            abort(409, message=text)
        return jsonify({"success": "OK"})
