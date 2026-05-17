import pg8000
import os


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = pg8000.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            ssl_context=True,
        )
        self.conn.autocommit = True
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY,
                full_name TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                product TEXT,
                size TEXT,
                color TEXT,
                material TEXT,
                price BIGINT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)
        cur.close()

    def add_user(self, user_id, full_name, username):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO users (id, full_name, username)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO UPDATE
            SET full_name = EXCLUDED.full_name,
                username = EXCLUDED.username;
        """, (user_id, full_name, username))
        cur.close()

    def save_order(self, user_id, product, size, color, material, price):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO orders (user_id, product, size, color, material, price)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (user_id, product, size, color, material, price))
        order_id = cur.fetchone()[0]
        cur.close()
        return order_id

    def get_user_orders(self, user_id):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT id, product, size, color, material, price, status, created_at
            FROM orders WHERE user_id = %s
            ORDER BY created_at DESC LIMIT 10;
        """, (user_id,))
        rows = cur.fetchall()
        cur.close()
        keys = ["id", "product", "size", "color", "material", "price", "status", "created_at"]
        return [dict(zip(keys, row)) for row in rows]

    def update_order_status(self, order_id, status):
        cur = self.conn.cursor()
        cur.execute("UPDATE orders SET status = %s WHERE id = %s;", (status, order_id))
        cur.close()

    def get_all_orders(self, status=None):
        cur = self.conn.cursor()
        if status:
            cur.execute("""
                SELECT o.id, o.product, o.size, o.color, o.material, o.price,
                       o.status, o.created_at, u.full_name, u.username
                FROM orders o JOIN users u ON o.user_id = u.id
                WHERE o.status = %s ORDER BY o.created_at DESC;
            """, (status,))
        else:
            cur.execute("""
                SELECT o.id, o.product, o.size, o.color, o.material, o.price,
                       o.status, o.created_at, u.full_name, u.username
                FROM orders o JOIN users u ON o.user_id = u.id
                ORDER BY o.created_at DESC LIMIT 50;
            """)
        rows = cur.fetchall()
        cur.close()
        keys = ["id", "product", "size", "color", "material", "price", "status", "created_at", "full_name", "username"]
        return [dict(zip(keys, row)) for row in rows]


db = Database()
