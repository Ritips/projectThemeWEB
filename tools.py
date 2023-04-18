from flask_jwt_simple import create_jwt
from flask import jsonify
from cryptography.fernet import Fernet


key = Fernet.generate_key()
fernet = Fernet(key)


def create_jwt_generate_response(user):
    cp_user = user
    cp_user.set_password(None)
    j_token = {"token": create_jwt(identity=cp_user)}
    return jsonify(j_token)


def encrypt_password(password):
    return fernet.encrypt(password.encode())


def decrypt_password(password):
    return fernet.decrypt(password).decode()
