from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
from zoneinfo import ZoneInfo
import os

from database import db, init_schema, USING_PG, BASE_DIR

ON_RENDER = bool(os.environ.get("RENDER"))
if ON_RENDER and not USING_PG:
    raise RuntimeError("Defina a variável de ambiente DATABASE_URL (Neon) no Render.")

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
TZ = ZoneInfo("America/Sao_Paulo")

secret = os.environ.get("SECRET_KEY")
if not secret:
    if ON_RENDER:
        raise RuntimeError("Defina a variável de ambiente SECRET_KEY no Render.")
    secret = "dev-only-change-this-secret"
app.secret_key = secret
app.config["SESSION_COOKIE_SECURE"] = ON_RENDER
app.config["PREFERRED_URL_SCHEME"] = "https" if ON_RENDER else "http"


def seed_users(conn):
    """Cria usuários iniciais a partir de SEED_USERS=user:senha,user:senha"""
    raw = os.environ.get("SEED_USERS", "").strip()
    if not raw:
        return

    for item in raw.split(","):
        item = item.strip()
        if ":" not in item:
            continue
        username, senha = item.split(":", 1)
        username = username.strip()
        senha = senha.strip()
        if not username or not senha:
            continue
        existente = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        if not existente:
            conn.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(senha), "admin")
            )


def init_db():
    conn = db()
    init_schema(conn)
    seed_users(conn)
    conn.commit()
    conn.close()


init_db()


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        conn = db()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Usuário ou senha inválidos.", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    conn = db()

    total_products = conn.execute(
        "SELECT COUNT(*) c FROM products"
    ).fetchone()["c"]

    total_stock = conn.execute(
        "SELECT COALESCE(SUM(stock), 0) s FROM products"
    ).fetchone()["s"]

    low_stock = conn.execute(
        "SELECT COUNT(*) c FROM products WHERE stock <= min_stock"
    ).fetchone()["c"]

    movements = conn.execute("""
        SELECT m.*, p.name
        FROM movements m
        JOIN products p ON p.id = m.product_id
        ORDER BY m.id DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_products=total_products,
        total_stock=total_stock,
        low_stock=low_stock,
        movements=movements
    )


@app.route("/products")
@login_required
def products():
    search = request.args.get("search", "").strip()
    conn = db()

    if search:
        term = f"%{search}%"
        rows = conn.execute("""
            SELECT * FROM products
            WHERE name LIKE ?
               OR brand LIKE ?
               OR color LIKE ?
               OR size LIKE ?
            ORDER BY id DESC
        """, (term, term, term, term)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM products ORDER BY id DESC"
        ).fetchall()

    conn.close()
    return render_template("products.html", products=rows, search=search)


@app.route("/products/new", methods=["GET", "POST"])
@login_required
def new_product():
    if request.method == "POST":
        stock = int(request.form.get("stock") or 0)

        data = (
            request.form["name"].strip(),
            request.form["category"],
            request.form.get("brand", "").strip(),
            request.form.get("color", "").strip(),
            request.form.get("size", "").strip(),
            float(request.form.get("price") or 0),
            stock,
            int(request.form.get("min_stock") or 0),
            datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
        )

        conn = db()

        cur = conn.execute("""
            INSERT INTO products
            (name, category, brand, color, size, price, stock, min_stock, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)

        product_id = cur.lastrowid

        if stock > 0:
            conn.execute("""
                INSERT INTO movements
                (product_id, type, quantity, note, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_id,
                "ENTRADA",
                stock,
                "Estoque inicial",
                datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
            ))

        conn.commit()
        conn.close()

        flash("Produto cadastrado com sucesso.", "success")
        return redirect(url_for("products"))

    return render_template("product_form.html", product=None)


@app.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    conn = db()
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return "Produto não encontrado", 404

    if request.method == "POST":
        conn.execute("""
            UPDATE products
            SET name = ?, category = ?, brand = ?, color = ?, size = ?,
                price = ?, min_stock = ?
            WHERE id = ?
        """, (
            request.form["name"].strip(),
            request.form["category"],
            request.form.get("brand", "").strip(),
            request.form.get("color", "").strip(),
            request.form.get("size", "").strip(),
            float(request.form.get("price") or 0),
            int(request.form.get("min_stock") or 0),
            product_id
        ))

        conn.commit()
        conn.close()

        flash("Produto atualizado.", "success")
        return redirect(url_for("products"))

    conn.close()
    return render_template("product_form.html", product=product)


@app.post("/products/<int:product_id>/delete")
@login_required
def delete_product(product_id):
    conn = db()
    used = conn.execute(
        "SELECT 1 FROM sale_items WHERE product_id = ? LIMIT 1",
        (product_id,)
    ).fetchone()
    if used:
        conn.close()
        flash("Não é possível excluir um produto que já entrou em uma venda.", "danger")
        return redirect(url_for("products"))

    conn.execute(
        "DELETE FROM movements WHERE product_id = ?",
        (product_id,)
    )
    conn.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )
    conn.commit()
    conn.close()

    flash("Produto removido.", "success")
    return redirect(url_for("products"))


@app.route("/stock/<int:product_id>", methods=["GET", "POST"])
@login_required
def stock(product_id):
    conn = db()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return "Produto não encontrado", 404

    if request.method == "POST":
        movement_type = request.form["type"]
        quantity = int(request.form["quantity"])
        note = request.form.get("note", "").strip()

        if quantity <= 0:
            flash("A quantidade deve ser maior que zero.", "danger")

        elif movement_type == "SAIDA" and quantity > product["stock"]:
            flash("Estoque insuficiente para essa saída.", "danger")

        else:
            if movement_type == "ENTRADA":
                new_stock = product["stock"] + quantity
            else:
                new_stock = product["stock"] - quantity

            conn.execute(
                "UPDATE products SET stock = ? WHERE id = ?",
                (new_stock, product_id)
            )

            conn.execute("""
                INSERT INTO movements
                (product_id, type, quantity, note, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                product_id,
                movement_type,
                quantity,
                note,
                datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()
            conn.close()

            flash(f"{movement_type.title()} registrada com sucesso.", "success")
            return redirect(url_for("stock", product_id=product_id))

    movements = conn.execute("""
        SELECT * FROM movements
        WHERE product_id = ?
        ORDER BY id DESC
    """, (product_id,)).fetchall()

    conn.close()

    return render_template(
        "stock.html",
        product=product,
        movements=movements
    )


@app.route("/movements")
@login_required
def movements():
    conn = db()

    rows = conn.execute("""
        SELECT m.*, p.name
        FROM movements m
        JOIN products p ON p.id = m.product_id
        ORDER BY m.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        "movements.html",
        movements=rows
    )




@app.route("/sales")
@login_required
def sales():
    conn = db()
    rows = conn.execute("""
        SELECT s.*,
               (SELECT COUNT(*) FROM sale_items si WHERE si.sale_id = s.id) AS item_count
        FROM sales s
        ORDER BY s.id DESC
    """).fetchall()
    conn.close()
    return render_template("sales.html", sales=rows)


@app.route("/sales/new", methods=["GET", "POST"])
@login_required
def new_sale():
    cart = session.get("sale_cart", [])

    if request.method == "POST":
        action = request.form.get("action")

        if action == "clear":
            session.pop("sale_cart", None)
            flash("Venda limpa.", "info")
            return redirect(url_for("new_sale"))

        if action == "add":
            try:
                product_id = int(request.form["product_id"])
                quantity = int(request.form.get("quantity") or 0)
            except (ValueError, TypeError):
                flash("Selecione um produto e informe uma quantidade válida.", "danger")
                return redirect(url_for("new_sale"))

            if quantity <= 0:
                flash("A quantidade deve ser maior que zero.", "danger")
                return redirect(url_for("new_sale"))

            conn = db()
            product = conn.execute(
                "SELECT * FROM products WHERE id = ?", (product_id,)
            ).fetchone()
            conn.close()

            if not product:
                flash("Produto não encontrado.", "danger")
                return redirect(url_for("new_sale"))

            existing_qty = next((i["quantity"] for i in cart if i["product_id"] == product_id), 0)
            if existing_qty + quantity > product["stock"]:
                flash(f"Estoque insuficiente. Disponível: {product['stock']}.", "danger")
                return redirect(url_for("new_sale"))

            found = False
            for item in cart:
                if item["product_id"] == product_id:
                    item["quantity"] += quantity
                    found = True
                    break

            if not found:
                cart.append({
                    "product_id": product["id"],
                    "name": product["name"],
                    "category": product["category"],
                    "brand": product["brand"] or "",
                    "color": product["color"] or "",
                    "size": product["size"] or "",
                    "quantity": quantity,
                    "unit_price": float(product["price"])
                })

            session["sale_cart"] = cart
            return redirect(url_for("new_sale"))

        if action == "remove":
            try:
                product_id = int(request.form["product_id"])
                cart = [i for i in cart if i["product_id"] != product_id]
                session["sale_cart"] = cart
            except (ValueError, TypeError):
                pass
            return redirect(url_for("new_sale"))

        if action == "finish":
            if not cart:
                flash("Adicione pelo menos um produto à venda.", "danger")
                return redirect(url_for("new_sale"))

            payment_method = request.form.get("payment_method", "").strip()
            allowed = {"PIX", "Dinheiro", "Cartão de débito", "Cartão de crédito"}
            if payment_method not in allowed:
                flash("Selecione uma forma de pagamento.", "danger")
                return redirect(url_for("new_sale"))

            conn = db()
            try:
                checked = []
                total = 0.0

                for item in cart:
                    product = conn.execute(
                        "SELECT * FROM products WHERE id = ?", (item["product_id"],)
                    ).fetchone()
                    if not product:
                        raise ValueError(f"Produto '{item['name']}' não existe mais.")
                    if item["quantity"] > product["stock"]:
                        raise ValueError(
                            f"Estoque insuficiente para '{product['name']}'. "
                            f"Disponível: {product['stock']}."
                        )
                    unit_price = float(product["price"])
                    subtotal = unit_price * item["quantity"]
                    total += subtotal
                    checked.append((product, item["quantity"], unit_price, subtotal))

                now = datetime.now(TZ).strftime("%Y-%m-%d %H:%M:%S")
                cur = conn.execute(
                    """INSERT INTO sales (total, payment_method, username, created_at)
                       VALUES (?, ?, ?, ?)""",
                    (total, payment_method, session.get("username", "admin"), now)
                )
                sale_id = cur.lastrowid

                for product, quantity, unit_price, subtotal in checked:
                    conn.execute(
                        """INSERT INTO sale_items
                           (sale_id, product_id, quantity, unit_price, subtotal)
                           VALUES (?, ?, ?, ?, ?)""",
                        (sale_id, product["id"], quantity, unit_price, subtotal)
                    )
                    conn.execute(
                        "UPDATE products SET stock = ? WHERE id = ?",
                        (product["stock"] - quantity, product["id"])
                    )
                    conn.execute(
                        """INSERT INTO movements
                           (product_id, type, quantity, note, created_at)
                           VALUES (?, ?, ?, ?, ?)""",
                        (product["id"], "SAIDA", quantity, f"Venda #{sale_id}", now)
                    )

                conn.commit()
                session.pop("sale_cart", None)
                flash(f"Venda #{sale_id} finalizada com sucesso.", "success")
                return redirect(url_for("sale_detail", sale_id=sale_id))
            except Exception as exc:
                conn.rollback()
                flash(str(exc), "danger")
                return redirect(url_for("new_sale"))
            finally:
                conn.close()

    conn = db()
    products = conn.execute(
        """SELECT * FROM products WHERE stock > 0
           ORDER BY name, brand, color, size"""
    ).fetchall()
    conn.close()

    total = sum(i["quantity"] * i["unit_price"] for i in cart)
    return render_template("new_sale.html", products=products, cart=cart, total=total)


@app.route("/sales/<int:sale_id>")
@login_required
def sale_detail(sale_id):
    conn = db()
    sale = conn.execute("SELECT * FROM sales WHERE id = ?", (sale_id,)).fetchone()
    if not sale:
        conn.close()
        return "Venda não encontrada", 404

    items = conn.execute("""
        SELECT si.*, p.name, p.category, p.brand, p.color, p.size
        FROM sale_items si
        JOIN products p ON p.id = si.product_id
        WHERE si.sale_id = ?
        ORDER BY si.id
    """, (sale_id,)).fetchall()
    conn.close()
    return render_template("sale_detail.html", sale=sale, items=items)


@app.route("/reports", methods=["GET"])
@login_required
def reports():
    try:
        month = int(request.args.get("month") or datetime.now(TZ).month)
        year = int(request.args.get("year") or datetime.now(TZ).year)
    except ValueError:
        month, year = datetime.now(TZ).month, datetime.now(TZ).year

    if not 1 <= month <= 12:
        month = datetime.now(TZ).month
    if not 2000 <= year <= 2100:
        year = datetime.now(TZ).year

    period = f"{year:04d}-{month:02d}"
    conn = db()

    summary = conn.execute("""
        SELECT COUNT(*) AS sales_count, COALESCE(SUM(total), 0) AS revenue
        FROM sales WHERE substr(created_at, 1, 7) = ?
    """, (period,)).fetchone()

    items = conn.execute("""
        SELECT COALESCE(SUM(quantity), 0) AS items_sold
        FROM sale_items si JOIN sales s ON s.id = si.sale_id
        WHERE substr(s.created_at, 1, 7) = ?
    """, (period,)).fetchone()

    payments = conn.execute("""
        SELECT payment_method, COUNT(*) AS sales_count, COALESCE(SUM(total), 0) AS total
        FROM sales WHERE substr(created_at, 1, 7) = ?
        GROUP BY payment_method ORDER BY total DESC
    """, (period,)).fetchall()

    top_products = conn.execute("""
        SELECT p.name, COALESCE(p.brand,'') brand, COALESCE(p.color,'') color,
               COALESCE(p.size,'') size, SUM(si.quantity) quantity,
               SUM(si.subtotal) total
        FROM sale_items si
        JOIN sales s ON s.id = si.sale_id
        JOIN products p ON p.id = si.product_id
        WHERE substr(s.created_at, 1, 7) = ?
        GROUP BY p.id, p.name, p.brand, p.color, p.size
        ORDER BY quantity DESC, total DESC LIMIT 10
    """, (period,)).fetchall()

    monthly = conn.execute("""
        SELECT substr(created_at,1,7) period, COUNT(*) sales_count,
               COALESCE(SUM(total),0) total
        FROM sales WHERE substr(created_at,1,4) = ?
        GROUP BY substr(created_at,1,7) ORDER BY period
    """, (str(year),)).fetchall()
    conn.close()

    revenue = float(summary["revenue"] or 0)
    sales_count = int(summary["sales_count"] or 0)
    items_sold = int(items["items_sold"] or 0)
    ticket_average = revenue / sales_count if sales_count else 0

    months = [(1,"Janeiro"),(2,"Fevereiro"),(3,"Março"),(4,"Abril"),
              (5,"Maio"),(6,"Junho"),(7,"Julho"),(8,"Agosto"),
              (9,"Setembro"),(10,"Outubro"),(11,"Novembro"),(12,"Dezembro")]
    years = list(range(datetime.now(TZ).year - 5, datetime.now(TZ).year + 1))

    return render_template(
        "reports.html", month=month, year=year, months=months, years=years,
        revenue=revenue, sales_count=sales_count, items_sold=items_sold,
        ticket_average=ticket_average, payments=payments,
        top_products=top_products, monthly=monthly
    )


@app.route("/logo.jpg")
def logo():
    logo_path = os.path.join(BASE_DIR, "static", "logo.jpg")
    if not os.path.isfile(logo_path):
        return "Logo não encontrado: " + logo_path, 404
    return send_file(logo_path, mimetype="image/jpeg")


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=not ON_RENDER)
