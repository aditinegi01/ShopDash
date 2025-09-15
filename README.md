# 🛍️ ShopDash  

**ShopDash** is a **multi-tenant analytics and synchronization dashboard** for Shopify stores.  
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
   git clone https://github.com/aditinegi01/ShopDash.git
   cd shopdash
   ```

2. Create and activate a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. Set environment variables in `.env`:  
   ```env
   SECRET_KEY=your_flask_secret
   SQLALCHEMY_DATABASE_URI=mysql+pymysql://user:password@localhost/db-name
   SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
   STORE_URL=https://your-shopify-store-url
   BASE_URL=https://your-tunnel-or-vercel-url
   ```

5. Run database migrations:  
   ```bash
   flask db upgrade
   ```

6. Register Shopify webhooks (update `.env` with correct `BASE_URL` first):  
   ```bash
   python register_webhooks.py
   ```

7. Start the app:  
   ```bash
   python app.py
   ```

---

## 🏗️ Architecture Diagram  

```mermaid
flowchart TD
    A[Shopify<br>Products, Orders, ...] -->|Webhooks| B[Flask App<br>ShopDash]
    B -->|SQLAlchemy ORM| C[(MySQL DB)]
    B -->|REST APIs + Templates| D[Browser<br>Dashboard]
    C --> D
```

---

## 📡 API Endpoints  

### Authentication  
- `POST /login` → Login as tenant  
- `POST /register` → Register new tenant  
- `GET /logout` → Logout  

### Webhooks  
- `POST /webhook/products/create`  
- `POST /webhook/products/update`  
- `POST /webhook/products/delete`  
- `POST /webhook/customers/create`  
- `POST /webhook/customers/update`  
- `POST /webhook/customers/delete`  
- `POST /webhook/orders/create`  
- `POST /webhook/orders/update`  
- `POST /webhook/orders/cancelled`  

### Dashboard / Sync  
- `GET /dashboard/<tenant_id>` → Overview with metrics + charts  
- `GET /sync/<tenant_id>` → Manual Shopify sync  
- `GET /products/<tenant_id>` → View all products  
- `GET /customers/<tenant_id>` → View all customers  
- `GET /orders/<tenant_id>` → View all orders  

---

## 🗄️ Database Schema  

### Tenants  
| Field         | Type        | Notes              |  
|---------------|------------|--------------------|  
| tenant_id     | INT (PK)   | Auto increment     |  
| store_name    | VARCHAR    | Unique per tenant  |  
| email         | VARCHAR    | Unique             |  
| password      | VARCHAR    | Hashed password    |  
| api_key       | VARCHAR    | Shopify API key    |  
| api_secret    | VARCHAR    | Shopify API secret |  
| access_token  | VARCHAR    | Shopify access     |  

### Products  
| Field               | Type        | Notes             |  
|---------------------|------------|-------------------|  
| product_id          | BIGINT (PK)| Shopify product ID|  
| tenant_id           | INT (FK)   | Linked to tenant  |  
| title               | VARCHAR    | Product title     |  
| price               | DECIMAL    | Product price     |  
| inventory_quantity  | INT        | Stock level       |  
| created_at          | DATETIME   | Created timestamp |  

### Customers  
| Field        | Type        | Notes             |  
|--------------|------------|-------------------|  
| customer_id  | BIGINT (PK)| Shopify customer ID|  
| tenant_id    | INT (FK)   | Linked to tenant  |  
| first_name   | VARCHAR    | First name        |  
| last_name    | VARCHAR    | Last name         |  
| email        | VARCHAR    | Customer email    |  
| total_spent  | DECIMAL    | Lifetime spend    |  
| created_at   | DATETIME   | Created timestamp |  

### Orders  
| Field        | Type        | Notes             |  
|--------------|------------|-------------------|  
| order_id     | BIGINT (PK)| Shopify order ID  |  
| tenant_id    | INT (FK)   | Linked to tenant  |  
| customer_id  | BIGINT     | Customer reference|  
| product_id   | BIGINT     | Product reference |  
| quantity     | INT        | Quantity ordered  |  
| total_price  | DECIMAL    | Order total       |  
| created_at   | DATETIME   | Created timestamp |  

---

## 🚀 Future Improvements  
- Add pagination & search in product/order views  
- Support multiple product variants  
- Advanced analytics (sales trends, best-selling products)  
- Role-based access (admin, staff)  
