from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'

db = SQLAlchemy(app)

#models
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    description = db.Column(db.String(200))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', cascade="all, delete-orphan")

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    quantity = db.Column(db.Integer)
    item = db.relationship('Item')

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20))


#routes

@app.route('/')
def home():
    return render_template('base.html')

# menu
@app.route('/menu')
def menu():
    items = Item.query.all()
    return render_template('menu.html', items=items)

@app.route('/menu/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        desc = request.form.get('description', '')
        new_item = Item(name=name, price=price, description=desc)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('menu'))
    return render_template('add_item.html')

@app.route("/menu/edit/<int:id>", methods=["GET", "POST"])
def edit_item(id):
    item = Item.query.get_or_404(id)
    if request.method == "POST":
        item.name = request.form["name"]
        item.price = request.form["price"]
        item.description = request.form["description"]
        db.session.commit()
        return redirect(url_for("menu"))
    return render_template("menu_edit.html", item=item)

@app.route('/menu/delete/<int:id>')
def delete_item(id):
    item = Item.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('menu'))

# orders
@app.route('/orders')
def orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)


# add order
@app.route("/orders/add", methods=["GET", "POST"])
def add_order():
    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        new_order = Order(customer_name=customer_name, phone=phone)
        db.session.add(new_order)
        db.session.commit()
        return redirect(url_for("order_add_items", order_id=new_order.id))
    return render_template("order_add.html")

@app.route('/orders/<int:order_id>/add_item', methods=['GET', 'POST'])
def order_add_items(order_id):
    order = Order.query.get_or_404(order_id)
    items = Item.query.all()

    if request.method == 'POST':
        item_id = request.form['item_id']
        quantity = int(request.form['quantity'])

        order_item = OrderItem(order_id=order.id, item_id=item_id, quantity=quantity)
        db.session.add(order_item)
        db.session.commit()

        return redirect(f'/orders/{order.id}')

    return render_template('order_add_items.html', order=order, items=items)

# order details
@app.route("/orders/<int:order_id>")
def order_details(order_id):
    order = Order.query.get_or_404(order_id)
    total = sum([oi.quantity * oi.item.price for oi in order.items])
    return render_template("order_details.html", order=order, total=total)

# edit oeder
@app.route("/orders/edit/<int:order_id>", methods=["GET", "POST"])
def edit_order(order_id):
    order = Order.query.get_or_404(order_id)
    if request.method == "POST":
        order.customer_name = request.form["customer_name"]
        order.phone = request.form["phone"]
        db.session.commit()
        return redirect(url_for("orders"))
    return render_template("order_edit.html", order=order)  

# delete order
@app.route("/orders/delete/<int:order_id>")
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for("orders"))

#customers
@app.route('/customers')
def list_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form.get('email')
        phone = request.form['phone']

        new_customer = Customer(name=name, email=email, phone=phone)
        db.session.add(new_customer)
        db.session.commit()
        return redirect('/customers')

    return render_template('add_customer.html')

@app.route('/customers/<int:customer_id>')
def customer_details(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return render_template('customer_details.html', customer=customer)

@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.email = request.form.get('email')
        customer.phone = request.form['phone']
        db.session.commit()
        return redirect('/customers')

    return render_template('customer_edit.html', customer=customer)

@app.route('/customers/delete/<int:customer_id>')
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return redirect('/customers')


#run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
