from flask import jsonify
from datetime import datetime
from models import Product, db  

def handle_product_webhook(data, action):
    print(f"Product {action.capitalize()} Webhook Received:", data)

    try:
        product_id = data.get("id")
        product_title = data.get("title")
        product_price = float(data["variants"][0].get("price", 0) or 0)
        inventory_qty = int(data["variants"][0].get("inventory_quantity", 0) or 0)

        created_at_raw = data.get("created_at")
        created_at = None
        if created_at_raw:
            try:
                created_at = datetime.fromisoformat(created_at_raw.replace("Z", "+00:00"))
            except Exception:
                created_at = None  

        product = Product.query.filter_by(product_id=product_id, tenant_id=data.tenant_id).first()

        if product:
            # update existing product
            product.title = product_title
            product.price = product_price
            product.inventory_quantity = inventory_qty
            print(f"Updated product: {product_id}")
        else:
            # create new product
            product = Product(
                product_id=product_id,
                tenant_id=1,  
                title=product_title,
                price=product_price,
                inventory_quantity=inventory_qty,
                created_at=created_at
            )
            db.session.add(product)
            print(f"Inserted product: {product_id}")

        db.session.commit()

        return jsonify({"message": f"Product {action} synced: {product_title}"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error processing {action} webhook:", str(e))
        return jsonify({"error": str(e)}), 500


def handle_product_delete_webhook(data):
    print("Product Delete Webhook Received:", data)

    try:
        product_id = data.get("id")

        product = Product.query.filter_by(product_id=product_id, tenant_id=1).first()
        if product:
            db.session.delete(product)
            db.session.commit()
            return jsonify({"message": f"Product {product_id} deleted from DB"}), 200
        else:
            return jsonify({"message": f"Product {product_id} not found in DB"}), 404

    except Exception as e:
        db.session.rollback()
        print("Error deleting product:", str(e))
        return jsonify({"error": str(e)}), 500
