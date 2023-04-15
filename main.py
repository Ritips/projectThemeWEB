from data import db_session
from flask import redirect, Flask, render_template
from flask_login import current_user
from data.clients import Client
from data.orders import Order
from data.admins import Admin
from data.order_items import OrderItem
from data.authorisation_log import User
from data.items import Item
from data.type_of_goods import Category


app = Flask(__name__)


@app.route('/')
def main_page():
    return 'noen'


def test():
    s = db_session.create_session()
    res = s.query(User).filter(User.id == 1).first()


def main():
    db_session.global_init('db/Supercell_is_piece_of_sheet8.sqlite')
    test()
    # app.run()


if __name__ == '__main__':
    main()
