from flask import Flask, request,jsonify
import requests
import os

from dotenv import load_dotenv
load_dotenv()

store_url=os.getenv("STORE_URL") 
access_token=os.getenv("SHOPIFY_ACCESS_TOKEN")

base_url =os.getenv("BASE_URL")
url = f"{store_url}/admin/api/2025-01/webhooks.json"

headers = {
    "X-Shopify-Access-Token": access_token,
    "Content-Type": "application/json"
}

payloads = [
    # Product Webhooks
    {
        "webhook": {
            "topic": "products/create",
            "address": f"{base_url}/webhook/products/create",
            "format": "json"
        }
    },
    {
        "webhook": {
            "topic": "products/update",
            "address": f"{base_url}/webhook/products/update",
            "format": "json"
        }
    },
    {
        "webhook": {
            "topic": "products/delete",
            "address": f"{base_url}/webhook/products/delete",
            "format": "json"
        }
    },

    # Customer Webhooks
    {
        "webhook": {
            "topic": "customers/create",
            "address": f"{base_url}/webhook/customers/create",
            "format": "json"
        }
    },
    {
        "webhook": {
            "topic": "customers/update",
            "address": f"{base_url}/webhook/customers/update",
            "format": "json"
        }
    },
    {
        "webhook": {
            "topic": "customers/delete",
            "address": f"{base_url}/webhook/customers/delete",
            "format": "json"
        }
    },

    # Order Webhooks
    {
        "webhook": {
            "topic": "orders/create",
            "address": f"{base_url}/webhook/orders/create",
            "format": "json"
        }
    },
    {
        "webhook": {
            "topic": "orders/updated",
            "address": f"{base_url}/webhook/orders/update",
            "format": "json"
        }
    },
    {
        "webhook": {
            "topic": "orders/cancelled",
            "address": f"{base_url}/webhook/orders/cancelled",
            "format": "json"
        }
    }
]

for payload in payloads:
    res = requests.post(url, json=payload, headers=headers)
    print("Webhook registration response:", res.json())