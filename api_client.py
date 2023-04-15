from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.clients import Client
from data.authorisation_log import User


parser = reqparse.RequestParser()
parser.add_argument("user_id", type=int, required=True, location="args")


def abort_if_client_not_found(client_id):
    db_sess = db_session.create_session()
    if not db_sess.query(Client).get(client_id):
        abort(404, message=f"Client {client_id} not Found")


def abort_if_exists(user_id):
    db_sess = db_session.create_session()
    if db_sess.query(Client).filter_by(login_id=user_id).first():
        abort(409, message=f"Client who was already connected to user with id: {user_id} already exists")


def abort_if_user_not_found(login_id):
    db_sess = db_session.create_session()
    if not db_sess.query(User).filter_by(id=login_id).first():
        abort(404, message=f'User {login_id} not Found')


class ClientResource(Resource):
    @staticmethod
    def get(id_client):
        abort_if_client_not_found(id_client)
        db_sess = db_session.create_session()
        client = db_sess.query(Client).get(id_client)
        user = client.user
        name, surname, email, phone, second_email = user.name, user.surname, user.email, user.phone, user.second_email
        orders = client.orders
        return jsonify({"clients": {
            "id": client.id, "user_id": client.login_id,
            "name": name, "surname": surname, "email": email, "phone": phone, "second_email": second_email,
            "orders": [item for item in orders]
        }})

    @staticmethod
    def delete(id_client):
        abort_if_client_not_found(id_client)
        db_sess = db_session.create_session()
        client = db_sess.query(Client).get(id_client)
        db_sess.delete(client)
        db_sess.commit()
        return jsonify({"success": "OK"})

    @staticmethod
    def put(id_client):
        args = parser.parse_args()
        abort_if_client_not_found(id_client)
        abort_if_exists(args["user_id"])
        abort_if_user_not_found(args["user_id"])
        db_sess = db_session.create_session()
        client = db_sess.query(Client).get(id_client)
        client.login_id = args["user_id"]
        db_sess.commit()
        return jsonify({"success": "OK"})


class ClientListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        clients = db_sess.query(Client).all()
        dict_clients = {"clients": []}
        for client in clients:
            user = client.user
            name, surname, email, phone = user.name, user.surname, user.email, user.phone
            second_email = user.second_email
            orders = client.orders
            client_dict = {"name": name, "surname": surname, "email": email, "phone": phone,
                           "second_email": second_email, "orders": [item for item in orders]}
            dict_clients["clients"].append(client_dict)
        return jsonify(dict_clients)

    @staticmethod
    def post():
        args = parser.parse_args()
        abort_if_exists(args["user_id"])
        abort_if_user_not_found(args["user_id"])
        client = Client()
        db_sess = db_session.create_session()
        db_sess.add(client)
        db_sess.commit()
        return jsonify({"success": "OK"})
