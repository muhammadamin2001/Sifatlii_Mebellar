import json
import os

DATA_FILE = "/tmp/orders.json"

class Database:
    def __init__(self):
        self.users = {}
        self.orders = []
        self.next_id = 1

    def connect(self):
        pass

    def add_user(self, user_id, full_name, username):
        self.users[user_id] = {"full_name": full_name, "username": username}

    def save_order(self, user_id, product, size, color, material, price):
        order = {
            "id": self.next_id,
            "user_id": user_id,
            "product": product,
            "size": size,
            "color": color,
            "material": material,
            "price": price,
            "status": "pending",
            "created_at": "2026-01-01"
        }
        self.orders.append(order)
        self.next_id += 1
        return order["id"]

    def get_user_orders(self, user_id):
        return [o for o in self.orders if o["user_id"] == user_id]

    def update_order_status(self, order_id, status):
        for o in self.orders:
            if o["id"] == order_id:
                o["status"] = status

    def get_all_orders(self, status=None):
        if status:
            return [o for o in self.orders if o["status"] == status]
        return self.orders

db = Database()
