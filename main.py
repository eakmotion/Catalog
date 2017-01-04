from flask import Flask
app = Flask(__name__)

from flask import render_template

def require_authorization(func):
    return 'authorized'

@app.route('/')
@app.route('/category')
def main_page():
    return render_template('base.html')

@app.route('/order')
def order_page():
    our_fruits = ['Apple', 'Lemon', 'Orange']
    return render_template('order.html', foods = our_fruits)

@app.route('/about')
def about_page():
    return 'About Page'

@app.route('/login')
def showLogin():
    return 'Login'

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    return 'FB connect'

@app.route('/fbdisconnect')
def fbdisconnect():
    return 'FB disconnect'

@app.route('/gconnect', methods=['POST'])
def gconnect():
    return 'Google connect'

@app.route('/gdisconnect')
def gdisconnect():
    return 'Google disconnect'

@app.route('/disconnect')
def disconnect():
    return 'Disconnect'

@app.route('/catalog/item/new', methods=['GET', 'POST'])
# @require_authorization
def new_category_item():
    return 'new item'

@app.route('/catalog/<string:category_name>/<string:item_name>/edit', methods=['GET', 'POST'])
# @require_authorization
def edit_category_item(category_name, item_name):
    return 'edit item'

@app.route('/catalog/<string:category_name>/<string:item_name>/delete', methods=['GET', 'POST'])
# @require_authorization
def delete_category_item(category_name, item_name):
    return 'deleted item'

@app.route('/catalog/<string:category_name>/items')
def show_items(category_name):
    return category_name

@app.route('/catalog/<string:category_name>/<string:item_name>')
def view_category_item(category_name, item_name):
    return item_name

@app.route('/catalog.json')
def items_json():
    return 'Json API'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
