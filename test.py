from requests import get, delete, post, put


# http://127.0.0.1:5000/api/

print('----------------GET ALL-----------------')
print('----------------users-------------------')

response = get("http://127.0.0.1:5000/api/users")
print(response.json())
print('-----------------admins-----------------')

response = get("http://127.0.0.1:5000/api/admins")
print(response.json())
print('-----------------clients----------------')

response = get("http://127.0.0.1:5000/api/clients")
print(response.json())
print('-----------------orders-----------------')

response = get("http://127.0.0.1:5000/api/orders")
print(response.json())
print('----------------items-------------------')
response = get("http://127.0.0.1:5000/api/items")
print(response.json())
print('-----------------categories-------------')

response = get("http://127.0.0.1:5000/api/type_of_goods")
print(response.json())
print('------------------order_to_items--------')

response = get("http://127.0.0.1:5000/api/order_to_item")
print(response.json())
print('----------------------------------------')
exit()

params = {
    "title": 'nice_title', "id_category": ""
}
response = post("http://127.0.0.1:5000/api/items", params=params)
print(response.json())


params = {
    "title": 'ya_shrek'
}
response = post('http://127.0.0.1:5000/api/type_of_goods', params=params)
print(response.json())

params = {
    "title": 'ya_shrek2'
}
response = post('http://127.0.0.1:5000/api/type_of_goods', params=params)
print(response.json())


int_param = 19
params = {
    "login": f'login{int_param}', 'password': 'password', 'email': f'email{int_param}',
    'name': 'name', 'surname': 'surname'
}
response = post('http://127.0.0.1:5000/api/users', params=params)
print(response.json())


params = {"user_id": 5}
response = post('http://127.0.0.1:5000/api/clients', params=params)
print(response.json())