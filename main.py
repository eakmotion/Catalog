from flask import Flask
app = Flask(__name__)

from flask import render_template

@app.route('/')
def main_page():
    return render_template('base.html')

@app.route('/order')
def order_page():
    our_fruits = ['Apple', 'Lemon', 'Orange']
    return render_template('order.html', foods = our_fruits)

@app.route('/about')
def about_page():
    return 'About Page'

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
