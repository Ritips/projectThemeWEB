import api_admins
import api_order
import api_order_to_items
import api_type_of_goods
from data import db_session
from flask import redirect, Flask, render_template, jsonify, request
from flask_restful import abort
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
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.privacy_forms import CheckPasswordForm, ChangePasswordForm
from forms.category_form import CategoryEditForm, CategoryAddForm
from forms.ItemForm import ItemAddForm, ItemEditForm
from flask_jwt_simple import JWTManager
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.utils import secure_filename
import os
import tools


app = Flask(__name__)
api = Api(app)
app.config["SECRET_KEY"] = "pythonWEBProjectSecretKey"
app.config["JWT_SECRET_KEY"] = 'pythonWEBProjectSecretKey'
app.config['JWT_EXPIRES'] = datetime.timedelta(hours=24)
app.config["JWT_IDENTITY_CLAIM"] = 'user'
app.config['JWT_HEADER_NAME'] = 'authorization'
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=30)
app.jwt = JWTManager(app)
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def main_page():
    response = requests.get('http://127.0.0.1:5000/api/type_of_goods')
    if response:
        categories = response.json()["categories"]
        format_categories = [categories[i: i + 3] for i in range(0, len(categories), 3)]
        return render_template('main_page.html', title="SystemSHOP", current_user=current_user,
                               categories=format_categories)
    return jsonify(response.json())


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/certain_category/<int:category_id>')
def get_items_certain_category(category_id):
    response = requests.get('http://127.0.0.1:5000/api/items', params={"id_category": category_id})
    print(response)  # test check code
    if response:
        print(response.json())  # test print
    return render_template("main_page.html", title="SystemSHOP", current_user=current_user)  # temporal render_template


@app.route('/categories')
@login_required
def categories_management():
    response = requests.get('http://127.0.0.1:5000/api/type_of_goods')
    categories = response.json()['categories'] if response else []
    return render_template('management_categories.html',
                           current_user=current_user, title='Categories', categories=categories)


@app.route('/categories/delete/<int:id_category>')
@login_required
def delete_category(id_category):
    requests.delete(f'http://127.0.0.1:5000/api/type_of_goods/{id_category}')
    response = requests.get('http://127.0.0.1:5000/api/type_of_goods')
    categories = response.json()['categories'] if response else []
    return render_template('management_categories.html',
                           current_user=current_user, title='Categories', categories=categories)


@app.route('/categories/edit/<int:id_category>', methods=['GET', 'POST'])
@login_required
def edit_category(id_category):
    form = CategoryEditForm()
    if request.method == 'GET':
        response = requests.get(f'http://127.0.0.1:5000/api/type_of_goods/{id_category}')
        if not response:
            abort(response.status_code, message=response.json()['message'])
        info = response.json()["categories"]
        form.title.data = info['title']
        form.id_category.data = info['id']
    if form.validate_on_submit():
        params = {'id': form.id_category.data, 'title': form.title.data}
        response = requests.put(f'http://127.0.0.1:5000/api/type_of_goods/{id_category}', params=params)
        if response:
            return redirect('/categories')
        return render_template('edit_category.html', form=form, title="Editing category",
                               current_user=current_user, message=response.json()['message'])
    return render_template('edit_category.html', form=form, title="Editing category", current_user=current_user)


@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    form = CategoryAddForm()
    if form.validate_on_submit():
        params = {'title': form.title.data}
        response = requests.post('http://127.0.0.1:5000/api/type_of_goods', params=params)
        if not response:
            return render_template("add_category.html", form=form, title="Adding category",
                                   current_user=current_user, message=response.json()['message'])
        return redirect('/categories')
    return render_template('add_category.html', form=form, title="Adding category", current_user=current_user)


@app.route('/management_items')
@login_required
def items_management():
    response = requests.get("http://127.0.0.1:5000/api/items")
    if response:
        return render_template('management_items.html',
                               title="Items", current_user=current_user, items=response.json()['items'])
    return jsonify(response.json())


@app.route('/management_items/delete/<int:id_item>')
@login_required
def delete_item(id_item):
    response = requests.delete(f"http://127.0.0.1:5000/api/items/{id_item}")
    if response:
        return redirect('/management_items')
    return response.json()


@app.route('/management_items/edit/<int:id_item>', methods=['GET', 'POST'])
@login_required
def edit_item(id_item):
    response = requests.get(f"http://127.0.0.1:5000/api/items/{id_item}")
    if not response:
        return response.json()
    form = ItemEditForm()
    info = response.json()['items']
    if request.method == 'GET':
        form.id_item.data = info['id']
        form.title.data = info['title']
        form.id_category.data = info['id_category']
        form.path_previous_image.data = info['img_path']
    if form.validate_on_submit():
        params = {'id': form.id_item.data, "title": form.title.data, "id_category": form.id_category.data,
                  "img_path": info['img_path']}
        image = form.image.data
        filename = None
        if image:
            filename = secure_filename(image.filename)
            path = f'/static/img/{filename}'
            params['img_path'] = path
        response = requests.put(f'http://127.0.0.1:5000/api/items/{form.id_item.data}', params=params)
        if response:
            if image:
                image.save(os.path.join('static/img', filename))
            return redirect('/management_items')
        return render_template('edit_item.html', form=form, current_user=current_user, title='Edit Item',
                               message=response.json()["message"])
    return render_template('edit_item.html', form=form, current_user=current_user, title="Edit Item")


@app.route('/management_items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    form = ItemAddForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        title = form.title.data
        id_category = form.id_category.data
        image = form.image.data
        if not image:
            path = '/static/img/default.png'
            filename = None
        else:
            filename = secure_filename(image.filename)
            path = f'/static/img/{filename}'
        params = {'title': title, "id_category": id_category, "img_path": path}
        response = requests.post('http://127.0.0.1:5000/api/items', params=params)
        if response:
            if image:
                image.save(os.path.join('static/img', filename))
            return redirect('/management_items')
        return render_template('add_item.html',
                               form=form, current_user=current_user,
                               title='Add Item', message=response.json()['message'])
    return render_template('add_item.html', form=form, current_user=current_user, title='Add Item')


@app.route('/privacy_settings')
@login_required
def privacy_setting():
    return render_template("privacy_settings.html", title='Privacy settings', current_user=current_user)


@app.route('/privacy_settings/alert/<int:message_id>')
@login_required
def privacy_settings_alert_function(message_id):
    return render_template("privacy_settings.html", title='Privacy settings',
                           current_user=current_user, message_id=message_id)


@app.route('/privacy_settings/check_password', methods=['GET', 'POST'])
@login_required
def check_password():
    form = CheckPasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):
            return redirect('/privacy_settings/change_password')
        return render_template("privacy_check_password.html", current_user=current_user, title="SystemShop",
                               message="Incorrect password", form=form)
    return render_template("privacy_check_password.html", current_user=current_user, title="SystemShop", form=form)


@app.route('/privacy_settings/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if form.password.data == form.repeat_password.data:
            db_sess = db_session.create_session()
            user = db_sess.query(User).get(current_user.id)
            user.set_password(form.password.data)
            db_sess.commit()
            return redirect('/privacy_settings')
        return render_template('privacy_change_password.html', current_user=current_user, title='SystemShop',
                               message="Password missmatch", form=form)
    return render_template('privacy_change_password.html', current_user=current_user, title='SystemShop', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter_by(login=form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me)
            return redirect('/')
        return render_template('login.html', title="Authorization",
                               message="Incorrect login or password", form=form)
    return render_template('login.html', title="Authorization", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.repeat_password.data:
            return render_template('register.html', title='Registration', form=form,
                                   message='Password missmatch')
        params = {
            "login": form.login.data, 'password': tools.encrypt_password(form.password.data),
            'email': tools.encrypt_password(form.email.data),
            'name': form.name.data, 'surname': form.surname.data
        }
        response = requests.post('http://127.0.0.1:5000/api/users', params=params)
        if response:
            return redirect('/login')
        return render_template('register.html', title='Registration', form=form,
                               message=response.json()["message"])
    return render_template('register.html', title='Registration', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


def main():
    db_session.global_init('db/Supercell_is_piece_of_sheet10.sqlite')
    api.add_resource(api_item.ItemResource, "/api/items/<int:id_item>")
    api.add_resource(api_item.ItemListResource, "/api/items")
    api.add_resource(api_users.UserResource, '/api/users/<int:id_user>')
    api.add_resource(api_users.UserListResource, '/api/users')
    api.add_resource(api_client.ClientResource, '/api/clients/<int:id_client>')
    api.add_resource(api_client.ClientListResource, '/api/clients')
    api.add_resource(api_admins.AdminResource, '/api/admins/<int:id_admin>')
    api.add_resource(api_admins.AdminListResource, '/api/admins')
    api.add_resource(api_type_of_goods.CategoryResource, '/api/type_of_goods/<int:id_category>')
    api.add_resource(api_type_of_goods.CategoryListResource, '/api/type_of_goods')
    api.add_resource(api_order.OrderResource, '/api/order/<int:id_order>')
    api.add_resource(api_order.OrderListResource, '/api/orders')
    api.add_resource(api_order_to_items.OrderItemResource, '/api/order_to_item/<int:id_order_item>')
    api.add_resource(api_order_to_items.OrderItemListResource, '/api/order_to_item')
    app.run()


if __name__ == '__main__':
    main()
