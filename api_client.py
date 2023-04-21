import sqlalchemy.exc
from flask_restful import Resource, abort, reqparse
from flask import jsonify
from data import db_session
from data.clients import Client

parser = reqparse.RequestParser()
parser.add_argument("user_id", type=int, required=True, location="args")


class ClientResource(Resource):
    @staticmethod
    def get(id_client):
        db_sess = db_session.create_session()
        client = db_sess.query(Client).get(id_client)
        db_sess.close()
        if not client:
            abort(404, message=f"Client {id_client} not Found")
        return jsonify({"clients": client.to_dict(only=('id', 'login_id'))})

    @staticmethod
    def delete(id_client):
        db_sess = db_session.create_session()
        client = db_sess.query(Client).get(id_client)
        if not client:
            db_sess.close()
            abort(404, message=f"Client {id_client} not Found")
        db_sess.delete(client)
        db_sess.commit()
        db_sess.close()
        return jsonify({"success": "OK"})

    @staticmethod
    def put(id_client):
        args = parser.parse_args()
        db_sess = db_session.create_session()
        client = db_sess.query(Client).get(id_client)
        if not client:
            db_sess.close()
            abort(404, message=f"Client {id_client} not Found")
        try:
            client.login_id = args["user_id"]
            db_sess.commit()
            db_sess.close()
            return jsonify({"success": "OK"})
        except sqlalchemy.exc.IntegrityError:
            abort(409, message=f"Client who was already connected to user with id: {args['user_id']} already exists")


class ClientListResource(Resource):
    @staticmethod
    def get():
        db_sess = db_session.create_session()
        clients = db_sess.query(Client).all()
        db_sess.close()
        return jsonify({"clients": [
            item.to_dict(only=('id', 'login_id')) for item in clients
        ]})

    @staticmethod
    def post():
        args = parser.parse_args()
        db_sess = db_session.create_session()
        try:
            client = Client()
            client.login_id = args["user_id"]
            db_sess.add(client)
            db_sess.commit()
            db_sess.close()
            return jsonify({"success": "OK"})
        except sqlalchemy.exc.IntegrityError:
            db_sess.close()
            abort(409, message=f"Client who was already connected to user with id: {args['user_id']} already exists")
