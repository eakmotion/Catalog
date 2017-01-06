from flask import Flask, request, flash, make_response, redirect, url_for, \
                  jsonify, render_template
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import User, Base, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import json
import random
import string
import requests
import httplib2

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog Application"

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
    categories = session.query(Category).order_by(Category.name)
    recent_items = session.query(Item).order_by(
                   desc(Item.created_date)).limit(10)
    return render_template('main.html',
                            categories=categories, items=recent_items)

@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('main_page'))
    else:
        flash("You were not logged in")
        return redirect(url_for('login'))

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % credentials
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/item/new', methods=['GET', 'POST'])
def new_category_item():
    if 'username' not in login_session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       price=request.form['price'],
                       category_id=request.form['category'],
                       picture=request.form['picture'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        category_id = request.form['category']
        category = session.query(Category).filter_by(id=category_id).one()
        return redirect(url_for('view_category_item',
                                category_name=newItem.category.name,
                                item_name=newItem.name))
    else:
        categories = session.query(Category)
        return render_template('new_item.html', categories=categories)

@app.route('/catalog/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def edit_category_item(category_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('login'))
    itemToEdit = session.query(Item).filter_by(name=item_name).one()
    cat = session.query(Category).filter_by(name=category_name).one()
    categories = session.query(Category).all()
    if login_session['user_id'] != itemToEdit.user.id:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        itemToEdit.name = request.form['name']
        itemToEdit.description = request.form['description']
        itemToEdit.price = request.form['price']
        itemToEdit.category_id = request.form['category']
        session.merge(itemToEdit)
        session.commit()
        return redirect(url_for('view_category_item',
                                category_name=itemToEdit.category.name,
                                item_name=itemToEdit.name))
    else:
        return render_template('edit_item.html',
                               categories=categories,
                               item=itemToEdit)

@app.route('/catalog/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def delete_category_item(category_name, item_name):
    if 'username' not in login_session:
        return redirect(url_for('login'))
    itemToDelete = session.query(Item).filter_by(name=item_name).one()
    cat = session.query(Category).filter_by(
          name=itemToDelete.category.name).one()
    if login_session['user_id'] != itemToDelete.user.id:
        return redirect(url_for('login'))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('main_page'))
    else:
        return render_template('delete_item.html', item=itemToDelete)

@app.route('/catalog/<string:category_name>/items')
def show_items(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    selected_category = session.query(Category).filter_by(
        name=category_name).one()
    return render_template('main.html', categories=categories,
                           category=selected_category)

@app.route('/catalog/<string:category_name>/<string:item_name>')
def view_category_item(category_name, item_name):
    selected_item = session.query(Item).join(Category).filter(
                    Item.name == item_name).filter(
                    Category.name == category_name).one()
    return render_template('item.html', item = selected_item)

@app.route('/catalog.json')
def items_json():
    categories = session.query(Category).all()
    return jsonify(Category=[i.serialize for i in categories])

def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0')
