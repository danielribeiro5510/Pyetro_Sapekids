import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = (os.environ.get("DATABASE_URL") or "").strip()
USING_PG = bool(DATABASE_URL)
SQLITE_PATH = os.environ.get("DATABASE_PATH") or os.path.join(BASE_DIR, "loja.db")

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'admin'
);
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT,
    color TEXT,
    size TEXT,
    price REAL NOT NULL DEFAULT 0,
    stock INTEGER NOT NULL DEFAULT 0,
    min_stock INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(product_id) REFERENCES products(id)
);
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    total REAL NOT NULL DEFAULT 0,
    payment_method TEXT NOT NULL,
    username TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    subtotal REAL NOT NULL,
    FOREIGN KEY(sale_id) REFERENCES sales(id),
    FOREIGN KEY(product_id) REFERENCES products(id)
);
"""

PG_SCHEMA = [
    """CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'admin'
    )""",
    """CREATE TABLE IF NOT EXISTS products (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        brand TEXT,
        color TEXT,
        size TEXT,
        price DOUBLE PRECISION NOT NULL DEFAULT 0,
        stock INTEGER NOT NULL DEFAULT 0,
        min_stock INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS movements (
        id SERIAL PRIMARY KEY,
        product_id INTEGER NOT NULL REFERENCES products(id),
        type TEXT NOT NULL,
        quantity INTEGER NOT NULL,
        note TEXT,
        created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS sales (
        id SERIAL PRIMARY KEY,
        total DOUBLE PRECISION NOT NULL DEFAULT 0,
        payment_method TEXT NOT NULL,
        username TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""",
    """CREATE TABLE IF NOT EXISTS sale_items (
        id SERIAL PRIMARY KEY,
        sale_id INTEGER NOT NULL REFERENCES sales(id),
        product_id INTEGER NOT NULL REFERENCES products(id),
        quantity INTEGER NOT NULL,
        unit_price DOUBLE PRECISION NOT NULL,
        subtotal DOUBLE PRECISION NOT NULL
    )""",
]


class Result:
    def __init__(self, cursor, lastrowid=None):
        self._cursor = cursor
        self.lastrowid = lastrowid

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()


class Connection:
    def __init__(self, raw, postgres):
        self._raw = raw
        self._postgres = postgres

    def execute(self, sql, params=()):
        if self._postgres:
            pg_sql = sql.replace("?", "%s")
            stripped = pg_sql.lstrip().upper()
            returning = "RETURNING" in stripped
            if stripped.startswith("INSERT") and not returning:
                pg_sql = pg_sql.rstrip().rstrip(";") + " RETURNING id"
                returning = True
            cur = self._raw.execute(pg_sql, params)
            lastrowid = None
            if returning and stripped.startswith("INSERT"):
                row = cur.fetchone()
                if row:
                    lastrowid = row["id"]
            return Result(cur, lastrowid)
        cur = self._raw.execute(sql, params)
        return Result(cur, cur.lastrowid)

    def commit(self):
        self._raw.commit()

    def rollback(self):
        self._raw.rollback()

    def close(self):
        self._raw.close()


def _pg_url():
    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    return url


def db():
    if USING_PG:
        import psycopg
        from psycopg.rows import dict_row

        raw = psycopg.connect(
            _pg_url(),
            row_factory=dict_row,
            connect_timeout=15,
        )
        return Connection(raw, True)

    os.makedirs(os.path.dirname(os.path.abspath(SQLITE_PATH)) or ".", exist_ok=True)
    raw = sqlite3.connect(SQLITE_PATH, check_same_thread=False, timeout=30)
    raw.row_factory = sqlite3.Row
    raw.execute("PRAGMA journal_mode=WAL")
    raw.execute("PRAGMA foreign_keys=ON")
    return Connection(raw, False)


def init_schema(conn):
    if USING_PG:
        for statement in PG_SCHEMA:
            conn.execute(statement)
        return
    conn._raw.executescript(SQLITE_SCHEMA)
