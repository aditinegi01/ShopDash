from flask import jsonify
from datetime import datetime
from models import Order, Tenant, db

def handle_order_webhook(request, action):
    try:
        shop_domain = request.headers.get("X-Shopify-Shop-Domain")
        tenant = Tenant.query.filter_by(store_name=shop_domain.replace(".myshopify.com", "")).first()
        data = request.json
        order_id = data.get("id")
        customer_id = data.get("customer", {}).get("id")
        total_price = float(data.get("total_price", 0) or 0)
        created_at_raw = data.get("created_at")

        # Convert created_at to datetime if present
        created_at = None
        if created_at_raw:
            try:
                created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
            except Exception:
                created_at = None

        product_id = None
        quantity = 1
        if data.get("line_items"):
            product_id = data["line_items"][0].get("product_id")
            quantity = data["line_items"][0].get("quantity", 1)

        # Upsert order
        order = Order.query.get(order_id)
        if not order:
            order = Order(
                order_id=order_id,
                tenant_id=tenant.tenant_id,
                customer_id=customer_id,
                product_id=product_id,
                quantity=quantity,
                total_price=total_price,
                created_at=created_at
            )
            db.session.add(order)
        else:
            order.customer_id = customer_id
            order.product_id = product_id
            order.quantity = quantity
            order.total_price = total_price

        db.session.commit()
        return jsonify({"message": f"Order {action} synced"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error processing order {action} webhook:", str(e))
        return jsonify({"error": str(e)}), 500


def handle_order_delete_webhook(request):
    try:
        data = request.json
        order_id = data.get("id")
        order = Order.query.get(order_id)

        if order:
            db.session.delete(order)
            db.session.commit()
            return jsonify({"message": f"Order {order_id} cancelled"}), 200
        else:
            return jsonify({"message": f"Order {order_id} not found"}), 404

    except Exception as e:
        db.session.rollback()
        print("Error deleting order:", str(e))
        return jsonify({"error": str(e)}), 500
