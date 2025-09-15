from flask import jsonify
from datetime import datetime
from models import Customer, Tenant, db

def handle_customer_webhook(request, action):
    try:
        shop_domain = request.headers.get("X-Shopify-Shop-Domain")
        tenant = Tenant.query.filter_by(store_name=shop_domain.replace(".myshopify.com", "")).first()
        data = request.json
        customer_id = data.get("id")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        total_spent = float(data.get("total_spent", 0) or 0)
        created_at_raw = data.get("created_at")

        created_at = None
        if created_at_raw:
            try:
                created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
            except Exception:
                created_at = None

        customer = Customer.query.get(customer_id)
        if not customer:
            customer = Customer(
                customer_id=customer_id,
                tenant_id=tenant.tenant_id,  
                first_name=first_name,
                last_name=last_name,
                email=email,
                total_spent=total_spent,
                created_at=created_at
            )
            db.session.add(customer)
        else:
            customer.first_name = first_name
            customer.last_name = last_name
            customer.email = email
            customer.total_spent = total_spent

        db.session.commit()
        return jsonify({"message": f"Customer {action} synced"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error processing customer {action} webhook:", str(e))
        return jsonify({"error": str(e)}), 500


def handle_customer_delete_webhook(request):
    try:
        data = request.json
        customer_id = data.get("id")
        customer = Customer.query.get(customer_id)

        if customer:
            db.session.delete(customer)
            db.session.commit()
            return jsonify({"message": f"Customer {customer_id} deleted"}), 200
        else:
            return jsonify({"message": f"Customer {customer_id} not found"}), 404

    except Exception as e:
        db.session.rollback()
        print("Error deleting customer:", str(e))
        return jsonify({"error": str(e)}), 500
