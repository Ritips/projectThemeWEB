import api_admins
import api_order
import api_order_to_items
import api_type_of_goods
from data import db_session
from flask import redirect, Flask, render_template, jsonify, request, session
from flask_restful import abort
from data.authorisation_log import User
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
    response2 = requests.get('http://127.0.0.1:5000/api/items')
    if response and response2:
        print(session)
        categories = response.json()["categories"]
        items = response2.json()["items"]
        format_categories = [categories[i: i + 3] for i in range(0, len(categories), 3)]
        return render_template('categories.html', title="SystemSHOP", current_user=current_user, items=items,
                               show_cart=('items' in session and session['items']['id_item']),
                               categories=format_categories)
    return jsonify(response.json())


def check_access():
    if not current_user.admins:
        abort(403, message="No access")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/certain_category/<int:category_id>')
def get_items_certain_category(category_id):
    response = requests.get('http://127.0.0.1:5000/api/items', params={"id_category": category_id})
    response2 = requests.get(f'http://127.0.0.1:5000/api/type_of_goods/{category_id}')
    category = response2.json()["categories"]
    if response:
        items = response.json()["items"]
        return render_template("one_category.html", title=category["title"], current_user=current_user, response=True,
                               show_cart=('items' in session and session['items']['id_item']),
                               items=items, category=category)
    return render_template("one_category.html", title=category["title"], current_user=current_user, response=False,
                           show_cart=('items' in session and session['items']['id_item']),
                           items=None, category=category)


@app.route('/categories')
@login_required
def categories_management():
    check_access()
    response = requests.get('http://127.0.0.1:5000/api/type_of_goods')
    categories = response.json()['categories'] if response else []
    return render_template('management_categories.html',
                           current_user=current_user, title='Categories', categories=categories)


@app.route('/categories/delete/<int:id_category>')
@login_required
def delete_category(id_category):
    check_access()
    requests.delete(f'http://127.0.0.1:5000/api/type_of_goods/{id_category}')
    response = requests.get('http://127.0.0.1:5000/api/type_of_goods')
    categories = response.json()['categories'] if response else []
    return render_template('management_categories.html',
                           current_user=current_user, title='Categories', categories=categories)


@app.route('/categories/edit/<int:id_category>', methods=['GET', 'POST'])
@login_required
def edit_category(id_category):
    check_access()
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
    check_access()
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
    check_access()
    response = requests.get("http://127.0.0.1:5000/api/items")
    if response:
        return render_template('management_items.html',
                               title="Items", current_user=current_user, items=response.json()['items'])
    return jsonify(response.json())


@app.route('/management_items/delete/<int:id_item>')
@login_required
def delete_item(id_item):
    check_access()
    response = requests.delete(f"http://127.0.0.1:5000/api/items/{id_item}")
    if response:
        return redirect('/management_items')
    return response.json()


@app.route('/management_items/edit/<int:id_item>', methods=['GET', 'POST'])
@login_required
def edit_item(id_item):
    check_access()
    response = requests.get(f"http://127.0.0.1:5000/api/items/{id_item}")
    if not response:
        return response.json()
    form = ItemEditForm()
    info = response.json()['items']
    previous_id = info['id']
    if request.method == 'GET':
        form.id_item.data = info['id']
        form.title.data = info['title']
        form.id_category.data = info['id_category']
        form.path_previous_image.data = info['img_path']
        form.cost.data = info["cost"]
        form.description.data = info['description']

    if form.validate_on_submit():
        params = {'id': form.id_item.data, "title": form.title.data, "id_category": form.id_category.data,
                  "img_path": info['img_path'], "previous_id": previous_id, 'cost': form.cost.data,
                  'description': form.description.data}
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
        form.path_previous_image.data = params['img_path']
        return render_template('edit_item.html', form=form, current_user=current_user, title='Edit Item',
                               message=response.json()["message"])
    return render_template('edit_item.html', form=form, current_user=current_user, title="Edit Item")


@app.route('/management_items/add', methods=['GET', 'POST'])
@login_required
def add_item():
    check_access()
    form = ItemAddForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        title = form.title.data
        id_category = form.id_category.data
        image = form.image.data
        description = form.description.data
        cost = form.cost.data
        if not image:
            path = '/static/img/default.png'
            filename = None
        else:
            filename = secure_filename(image.filename)
            path = f'/static/img/{filename}'
        params = {'title': title, "id_category": id_category, "img_path": path,
                  "cost": cost, "description": description}
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
    session.clear()
    session.pop('items', None)
    logout_user()
    return redirect('/')


@app.route('/client_log')
@login_required
def client_log():
    check_access()
    response = requests.get('http://127.0.0.1:5000/api/clients')
    if response:
        return render_template("ClientsLog.html", clients=response.json()['clients'], title='ClientLog',
                               current_user=current_user)
    return response.json()


@app.route('/client_log/delete_client/<int:id_client>')
@login_required
def delete_client(id_client):
    check_access()
    response = requests.delete(f'http://127.0.0.1:5000/api/clients/{id_client}')
    if response:
        return redirect('/client_log')
    return response.json()


@app.route('/client_log/edit_client/<int:id_client>', methods=['GET', 'POST'])
@login_required
def edit_client(id_client):
    check_access()
    from forms.client_form import EditClientForm
    response = requests.get(f"http://127.0.0.1:5000/api/clients/{id_client}")
    if not response:
        return response.json()
    form = EditClientForm()
    info = response.json()['clients']
    previous_id = info['client']['id']
    if request.method == 'GET':
        form.id_client.data = info['client']['id']
        form.bool_admin.data = False
    if form.validate_on_submit():
        id_client = form.id_client.data
        user_id = info['client']['login_id']
        if form.bool_admin.data:
            params = {'login_id': user_id}
            response = requests.post('http://127.0.0.1:5000/api/admins', params=params)
            if not response:
                return render_template('ClientEditLog.html', current_user=current_user,
                                       title='EditClient', message=response.json()['message'], form=form)
            response = requests.delete(f'http://127.0.0.1:5000/api/clients/{id_client}')
            if not response:
                return render_template('ClientEditLog.html', current_user=current_user,
                                       title='EditClient', message=response.json()['message'], form=form)
            return redirect('/client_log')
        else:
            params = {"user_id": user_id, 'previous_id': previous_id}
            response = requests.put(f'http://127.0.0.1:5000/api/clients/{id_client}', params=params)
            if response:
                return redirect('/client_log')
            return render_template('ClientEditLog.html', current_user=current_user,
                                   title='EditClient', message=response.json()['message'], form=form)
    return render_template('ClientEditLog.html', current_user=current_user, title='EditClient', form=form)


@app.route('/orders_log')
@login_required
def log_orders():
    check_access()
    response = requests.get('http://127.0.0.1:5000/api/orders')
    if response:
        response = response.json()
        return render_template('orders-log.html', title="LogOrders",
                               current_user=current_user, orders=response['orders'], particular_title='Log Orders')
    return response.json()["message"]


@app.route('/log_customer_orders/<int:id_customer>')
@app.route('/client_log/log_customer_orders/<int:id_customer>')
@login_required
def log_customer_orders(id_customer):
    params = {"client_id": id_customer, "check_client": True}
    if current_user.admins:
        response = requests.get('http://127.0.0.1:5000/api/orders', params=params)
        if response:
            response = response.json()
            return render_template(
                'orders-log.html', title="LogOrders", current_user=current_user,
                orders=response['orders'], particular_title='Log Orders')
        return response.json()
    if current_user.clients and current_user.clients[0].id == id_customer:
        response = requests.get('http://127.0.0.1:5000/api/orders', params=params)
        if response:
            response = response.json()
            return render_template(
                'orders-log.html', title="LogOrders", current_user=current_user,
                orders=response['orders'], particular_title='My orders')
        return response.json()
    abort(403, message="No access")


@app.route('/add_to_the_cart/<int:id_item>')
def add_to_cart(id_item):
    if 'items' not in session:
        session['items'] = {"id_item": [id_item, ]}
    else:
        el = session.get('items')
        el['id_item'].append(id_item)
        session['items'] = el
    el = session['items']
    output, valid_keys = dict(), list()
    for id_item in el['id_item']:
        if id_item not in valid_keys:
            response = requests.get(f'http://127.0.0.1:5000/api/items/{id_item}')
            if not response:
                continue
            output[id_item] = response.json()['items']
        valid_keys.append(id_item)
    total_price = sum(map(lambda x: output[x]['cost'], valid_keys))
    return render_template('cart.html', current_user=current_user, title="Cart", items=valid_keys, output=output,
                           show_cart=True, total_price=f'${total_price}')


@app.route('/get_cart')
def get_cart():
    el = session.get('items')
    if not el:
        return "Cart doesn't"
    output, valid_keys = dict(), list()
    for id_item in el['id_item']:
        if id_item not in valid_keys:
            response = requests.get(f'http://127.0.0.1:5000/api/items/{id_item}')
            if not response:
                continue
            output[id_item] = response.json()['items']
        valid_keys.append(id_item)
    total_price = sum(map(lambda x: output[x]['cost'], valid_keys))
    return render_template('cart.html', current_user=current_user, title="Cart",
                           items=valid_keys, output=output, show_cart=True, total_price=f'${total_price}')


@app.route('/delete_from_the_cart/<int:id_item>')
def delete_from_cart(id_item):
    try:
        el = session.get('items')
        el['id_item'].remove(id_item)
        session['items'] = el
        output, valid_keys = dict(), list()
        for id_item in el['id_item']:
            if id_item not in valid_keys:
                response = requests.get(f'http://127.0.0.1:5000/api/items/{id_item}')
                if not response:
                    continue
                output[id_item] = response.json()['items']
            valid_keys.append(id_item)
        total_price = sum(map(lambda x: output[x]['cost'], valid_keys))
        return render_template('cart.html', current_user=current_user, title="Cart", items=valid_keys, output=output,
                               show_cart=True, total_price=f'${total_price}')
    except KeyError:
        abort(404, message='NO CART')
    except ValueError:
        abort(404, message="NOT FOUND")


@app.route('/delete_cart')
def delete_cart():
    session.pop('items', None)
    return jsonify({"success": "cart deleted"})


@app.route('/confirm_order')
@login_required
def confirm_order():
    el = session.get('items')
    if current_user.admins:
        return f"{el}; This Function not available for admin"
    client_id = current_user.clients[0].id
    params = {"client_id": client_id}
    response = requests.post('http://127.0.0.1:5000/api/orders', params=params)
    if not response:
        return response.json()
    params['check_client'] = True
    response = requests.get('http://127.0.0.1:5000/api/orders', params=params)
    if not response:
        return response.json()
    id_order = response.json()['orders'][-1]['id']
    for id_item in el['id_item']:
        params = {"id_item": id_item, "id_order": id_order}
        requests.post('http://127.0.0.1:5000/api/order_to_item', params=params)
    session.pop('items', None)
    return redirect('/')


@app.route('/client_log/log_customer_orders/check_content_order/<int:id_client>')
@app.route('/log_customer_orders/check_content_order/<int:id_client>')
@login_required
def check_content_order(id_client):
    params = {"client_id": id_client, "check_client": True, "get_items": True}
    response = requests.get('http://127.0.0.1:5000/api/orders', params=params)
    if not response:
        return response.json()
    return render_template('check_content_customer_order.html', title="OrderContent", current_user=current_user,
                           orders=response.json()['orders'])


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
