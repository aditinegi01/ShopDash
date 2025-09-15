from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
import os
from models import db, Tenant, Customer, Product, Order

from webhooks.products import handle_product_webhook, handle_product_delete_webhook
from webhooks.customers import handle_customer_webhook, handle_customer_delete_webhook
from webhooks.orders import handle_order_webhook, handle_order_delete_webhook

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

# --- SQLAlchemy Config ---
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

access_token= os.getenv("SECRET_KEY")

# Product created
@app.route('/webhook/products/create', methods=['POST'])
def webhook_product_create():
    data = request.json
    return handle_product_webhook(data, action="create")

# Product updated
@app.route('/webhook/products/update', methods=['POST'])
def webhook_product_update():
    data = request.json
    return handle_product_webhook(data, action="update")

# Product deleted
@app.route('/webhook/products/delete', methods=['POST'])
def webhook_product_delete():
    data = request.json
    return handle_product_delete_webhook(data)


# Customer created
@app.route('/webhook/customers/create', methods=['POST'])
def webhook_customer_create():
    data = request.json
    return handle_customer_webhook(data, action="create")

# Customer updated
@app.route('/webhook/customers/update', methods=['POST'])
def webhook_customer_update():
    data = request.json
    return handle_customer_webhook(data, action="update")

# Customer deleted
@app.route('/webhook/customers/delete', methods=['POST'])
def webhook_customer_delete():
    data = request.json
    return handle_customer_delete_webhook(data)


# Order created
@app.route('/webhook/orders/create', methods=['POST'])
def webhook_order_create():
    data = request.json
    return handle_order_webhook(data, action="create")

# Order updated
@app.route('/webhook/orders/update', methods=['POST'])
def webhook_order_update():
    data = request.json
    return handle_order_webhook(data, action="update")

# Order cancelled
@app.route('/webhook/orders/cancelled', methods=['POST'])
def webhook_order_cancelled():
    data = request.json
    return handle_order_delete_webhook(data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        store_name = request.form['store_name']
        access_token = request.form['access_token']
        api_key = request.form['api_key']
        api_secret = request.form['api_secret']

        existing_tenant = Tenant.query.filter_by(email=email).first()
        if existing_tenant:
            flash("Tenant with this email already exists!", "danger")
            return redirect(url_for("register"))

        # new tenant
        new_tenant = Tenant(
            email=email,
            password=generate_password_hash(password),
            store_name=store_name,
            access_token=access_token,
            api_key=api_key,
            api_secret=api_secret
        )

        db.session.add(new_tenant)
        db.session.commit()

        flash("Tenant registered successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'tenant_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/dashboard/<int:tenant_id>', methods=['GET'])
@login_required
def dashboard(tenant_id):
    # Totals for cards
    total_customers = Customer.query.filter_by(tenant_id=tenant_id).count()
    total_products = Product.query.filter_by(tenant_id=tenant_id).count()
    total_orders = Order.query.filter_by(tenant_id=tenant_id).count()
    total_revenue = db.session.query(func.sum(Order.total_price)).filter_by(tenant_id=tenant_id).scalar() or 0

    # Last 7 days
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=6)

    # Orders per day
    orders_data = (
        db.session.query(func.date(Order.created_at), func.count(Order.order_id))
        .filter(Order.tenant_id == tenant_id, Order.created_at >= start_date)
        .group_by(func.date(Order.created_at))
        .all()
    )

    # Products per day
    products_data = (
        db.session.query(func.date(Product.created_at), func.count(Product.product_id))
        .filter(Product.tenant_id == tenant_id, Product.created_at >= start_date)
        .group_by(func.date(Product.created_at))
        .all()
    )

    # Customers per day
    customers_data = (
        db.session.query(func.date(Customer.created_at), func.count(Customer.customer_id))
        .filter(Customer.tenant_id == tenant_id, Customer.created_at >= start_date)
        .group_by(func.date(Customer.created_at))
        .all()
    )

    # Revenue per day
    revenue_data = (
        db.session.query(func.date(Order.created_at), func.sum(Order.total_price))
        .filter(Order.tenant_id == tenant_id, Order.created_at >= start_date)
        .group_by(func.date(Order.created_at))
        .all()
    )

    # Convert to dicts
    orders_dict = {str(date): count for date, count in orders_data}
    products_dict = {str(date): count for date, count in products_data}
    customers_dict = {str(date): count for date, count in customers_data}
    revenue_dict = {str(date): float(total or 0) for date, total in revenue_data}

    # Labels(last 7 days)
    labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    orders_chart = [orders_dict.get(day, 0) for day in labels]
    products_chart = [products_dict.get(day, 0) for day in labels]
    customers_chart = [customers_dict.get(day, 0) for day in labels]
    revenue_chart = [revenue_dict.get(day, 0) for day in labels]

    return render_template(
        "dashboard.html",
        tenant_id=tenant_id,
        total_products=total_products,
        total_customers=total_customers,
        total_orders=total_orders,
        total_revenue=total_revenue,
        chart_labels=labels,
        orders_chart=orders_chart,
        products_chart=products_chart,
        customers_chart=customers_chart,
        revenue_chart=revenue_chart
    )
     
@app.route('/orders/<int:tenant_id>')
@login_required
def view_orders(tenant_id):
    orders = Order.query.filter_by(tenant_id=tenant_id).all()
    print(orders)
    return render_template('orders.html', tenant_id=tenant_id, orders=orders)

@app.route('/products/<int:tenant_id>')
@login_required
def view_products(tenant_id):
    products = Product.query.filter_by(tenant_id=tenant_id).all()
    print(products)
    return render_template('products.html', tenant_id=tenant_id, products=products)

@app.route('/customers/<int:tenant_id>')
@login_required
def view_customers(tenant_id):
    customers = Customer.query.filter_by(tenant_id=tenant_id).all()
    print(customers)
    return render_template('customers.html', tenant_id=tenant_id, customers=customers)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        # fetch tenant by email
        tenant = Tenant.query.filter_by(email=email).first()

        if tenant and check_password_hash(tenant.password, password):
            session['tenant_id'] = tenant.tenant_id
            flash("Login successful!", "success")
            return redirect(url_for('dashboard', tenant_id=tenant.tenant_id))
        else:
            flash("You don't have an account. Create an account here!", "warning")
            return redirect(url_for('register'))

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

if __name__=="__main__":
    print("connecting to DB...")
    app.run(debug=True)