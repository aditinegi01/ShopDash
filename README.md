# 🛍️ ShopDash

**ShopDash** is a multi-tenant analytics and synchronization dashboard for Shopify stores.  
It provides **real-time insights** into products, orders, customers, and revenue using **Shopify Webhooks** and manual sync services.  

Built with **Flask (Python)**, **MySQL (SQLAlchemy ORM)**, and **Chart.js**, the app allows each tenant (store owner) to log in, view their data, and track growth through interactive charts.

---

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL server
- A Shopify store (with Admin API access token)

### Installation
1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/shopdash.git
   cd shopdash

2. Create and activate virtual environment:
python -m venv venv
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate       # Windows

3. Install dependencies:
pip install -r requirements.txt

4. Set environment variables in .env:
SECRET_KEY=your_flask_secret
DB_URI=mysql+pymysql://user:password@localhost/xeno_db
SHOPIFY_API_KEY=your_api_key
SHOPIFY_API_SECRET=your_api_secret

5. Run database migrations:
flask db upgrade

6. Expose your app for Shopify webhooks using BASE_URL:
Update BASE_URL in .env to run this app locally

7. Start the app:
run register_webhooks.py
once all the webhooks get registered, run app.py

🏗️ Architecture Diagram
        ┌─────────────┐
        │   Shopify   │
        │  (Products, │
        │ Orders, ... )  
        └───────┬─────┘
                │ Webhooks
                ▼
        ┌─────────────┐
        │   Flask     │
        │  ShopDash   │
        └───────┬─────┘
                │ SQLAlchemy ORM
                ▼
        ┌─────────────┐
        │   MySQL DB  │
        └─────────────┘
                ▲
                │ REST APIs + Templates
                ▼
        ┌─────────────┐
        │   Browser   │
        │ Dashboard   │
        └─────────────┘

📡 API Endpoints

Authentication
POST /login → Login as tenant
POST /register → Register new tenant
GET /logout → Logout

Webhooks
POST /webhook/products/create
POST /webhook/products/update
POST /webhook/products/delete
POST /webhook/customers/create
POST /webhook/customers/update
POST /webhook/customers/delete
POST /webhook/orders/create
POST /webhook/orders/update
POST /webhook/orders/cancelled

Dashboard / Sync
GET /dashboard/<tenant_id> → Overview with metrics + charts
GET /sync/<tenant_id> → Manual Shopify sync
GET /products/<tenant_id> → View all products
GET /customers/<tenant_id> → View all customers
GET /orders/<tenant_id> → View all orders

🗄️ Database Schema

Tenants
tenant_id   INT PK
store_name  VARCHAR
email       VARCHAR UNIQUE
password    VARCHAR (hashed)
api_key     VARCHAR
api_secret  VARCHAR
access_token VARCHAR

Products
product_id   BIGINT PK
tenant_id    INT FK
title        VARCHAR
price        DECIMAL
inventory_quantity INT
created_at   DATETIME

Customers
customer_id  BIGINT PK
tenant_id    INT FK
first_name   VARCHAR
last_name    VARCHAR
email        VARCHAR
total_spent  DECIMAL
created_at   DATETIME

Orders
order_id     BIGINT PK
tenant_id    INT FK
customer_id  BIGINT
product_id   BIGINT
quantity     INT
total_price  DECIMAL
created_at   DATETIME

🚀 Future improvements:
Add pagination & search in product/order views
Support multiple product variants
Advanced analytics (sales trends, best-selling products)
Role-based access (admin, staff)