import psycopg2
import psycopg2.extras
import os


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", 5432),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
        )
        self.conn.autocommit = True
        self.create_tables()

    def create_tables(self):
        with self.conn.cursor() as cur:
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

    def add_user(self, user_id, full_name, username):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (id, full_name, username)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET full_name = %s, username = %s;
            """, (user_id, full_name, username, full_name, username))

    def save_order(self, user_id, product, size, color, material, price):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO orders (user_id, product, size, color, material, price)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (user_id, product, size, color, material, price))
            return cur.fetchone()[0]

    def get_user_orders(self, user_id):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, product, size, color, material, price, status, created_at
                FROM orders WHERE user_id = %s
                ORDER BY created_at DESC LIMIT 10;
            """, (user_id,))
            return cur.fetchall()

    def update_order_status(self, order_id, status):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE orders SET status = %s WHERE id = %s;", (status, order_id))

    def get_all_orders(self, status=None):
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if status:
                cur.execute("""
                    SELECT o.*, u.full_name, u.username
                    FROM orders o JOIN users u ON o.user_id = u.id
                    WHERE o.status = %s ORDER BY o.created_at DESC;
                """, (status,))
            else:
                cur.execute("""
                    SELECT o.*, u.full_name, u.username
                    FROM orders o JOIN users u ON o.user_id = u.id
                    ORDER BY o.created_at DESC LIMIT 50;
                """)
            return cur.fetchall()


db = Database()
