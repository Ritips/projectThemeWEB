from data import db_session
from flask import redirect, Flask, render_template
from data.clients import Client
from data.orders import Order
from data.admins import Admin
from data.order_items import OrderItem
from data.authorisation_log import User
from data.items import Item
from data.type_of_goods import Category
from flask_restful import Api
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
import datetime
import requests
import api_client
import api_item
import api_users


app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "pythonWEBProjectSecretKey"
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=30)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main_page():
    return 'noen'


def test():
    s = db_session.create_session()
    res = s.query(User).all()


def main():
    db_session.global_init('db/Supercell_is_piece_of_sheet9.sqlite')
    # test()
    api.add_resource(api_item.ItemResource, "/api/items/<int:id_item>")
    api.add_resource(api_item.ItemListResource, "/api/items")
    api.add_resource(api_users.UserResource, '/api/users/<int:id_user>')
    api.add_resource(api_users.UserListResource, '/api/users')
    api.add_resource(api_client.ClientResource, '/api/clients/<int:id_client>')
    api.add_resource(api_client.ClientListResource, '/api/clients')
    app.run()


if __name__ == '__main__':
    main()
