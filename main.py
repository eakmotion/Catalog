from flask import Flask
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import User, Base, Category, Item


app = Flask(__name__)

from flask import render_template

# Connect to Database and create database session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

def require_authorization(func):
    return 'authorized'

@app.route('/')
@app.route('/category')
def main_page():
    categories = session.query(Category)
    recent_items = session.query(Item)
    return render_template('main.html',
                           categories=categories, items=recent_items)

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
    categories = session.query(Category).order_by(asc(Category.name))
    selected_category = session.query(Category).filter_by(
        name=category_name).one()
    return render_template('main.html', categories=categories,
                           category=selected_category)

@app.route('/catalog/<string:category_name>/<string:item_name>')
def view_category_item(category_name, item_name):
    try:
        selected_item = session.query(Item).join(Category).filter(
            Item.name == item_name).filter(
            Category.name == category_name).one()
        return render_template('item.html',
                               item = selected_item)
    except:
        return 'Error'

@app.route('/catalog.json')
def items_json():
    return 'Json API'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
