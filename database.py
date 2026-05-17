import asyncpg
import os
from datetime import datetime


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", 5432)),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            database=os.getenv("DB_NAME", "mebelbot"),
        )
        await self.create_tables()

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id         BIGINT PRIMARY KEY,
                    full_name  TEXT,
                    username   TEXT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id         SERIAL PRIMARY KEY,
                    user_id    BIGINT REFERENCES users(id),
                    product    TEXT NOT NULL,
                    size       TEXT NOT NULL,
                    color      TEXT NOT NULL,
                    material   TEXT NOT NULL,
                    price      BIGINT NOT NULL,
                    status     TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    async def add_user(self, user_id, full_name, username):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (id, full_name, username)
                VALUES ($1, $2, $3)
                ON CONFLICT (id) DO UPDATE
                SET full_name = $2, username = $3;
            """, user_id, full_name, username)

    async def save_order(self, user_id, product, size, color, material, price):
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                INSERT INTO orders (user_id, product, size, color, material, price)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id;
            """, user_id, product, size, color, material, price)
            return row["id"]

    async def get_user_orders(self, user_id):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT id, product, size, color, material, price, status, created_at
                FROM orders WHERE user_id = $1
                ORDER BY created_at DESC LIMIT 10;
            """, user_id)
            return [dict(r) for r in rows]

    async def update_order_status(self, order_id, status):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE orders SET status = $1 WHERE id = $2;
            """, status, order_id)

    async def get_all_orders(self, status=None):
        async with self.pool.acquire() as conn:
            if status:
                rows = await conn.fetch("""
                    SELECT o.*, u.full_name, u.username
                    FROM orders o JOIN users u ON o.user_id = u.id
                    WHERE o.status = $1
                    ORDER BY o.created_at DESC;
                """, status)
            else:
                rows = await conn.fetch("""
                    SELECT o.*, u.full_name, u.username
                    FROM orders o JOIN users u ON o.user_id = u.id
                    ORDER BY o.created_at DESC LIMIT 50;
                """)
            return [dict(r) for r in rows]


db = Database()
