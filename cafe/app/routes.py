import os
import uuid
from functools import wraps
from decimal import Decimal
from flask import (
    Blueprint, render_template, request, redirect, url_for, session,
    flash, jsonify, current_app, abort, send_from_directory
)
from werkzeug.utils import secure_filename
import bcrypt
from . import mysql



bp = Blueprint("main", __name__)


# ---------- helpers ----------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return wrapper


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


def save_image(file_storage):
    if not file_storage or file_storage.filename == "":
        return None
    if not allowed_file(file_storage.filename):
        return None
    ext = file_storage.filename.rsplit(".", 1)[1].lower()
    name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], name)
    file_storage.save(path)
    return name


def query(sql, params=None, fetch=None, commit=False):
    cur = mysql.connection.cursor()
    cur.execute(sql, params or ())
    result = None
    if fetch == "one":
        result = cur.fetchone()
    elif fetch == "all":
        result = cur.fetchall()
    if commit:
        mysql.connection.commit()
    last_id = cur.lastrowid
    cur.close()
    return result, last_id


# ---------- auth ----------
@bp.route("/", methods=["GET"])
def root():
    if "admin_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").encode()
        if not username or not password:
            return render_template("login_error.html",
                                   message="Username and password are required.")
        admin, _ = query("SELECT * FROM admins WHERE username=%s",
                         (username,), fetch="one")
        if not admin or not bcrypt.checkpw(password, admin["password_hash"].encode()):
            return render_template("login_error.html",
                                   message="Invalid username or password.")
        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["full_name"] or admin["username"]
        flash(f"Welcome back, {session['admin_name']}!", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("login.html")




@bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        full_name = (request.form.get("full_name") or "").strip()
        password = (request.form.get("password") or "")
        confirm = (request.form.get("confirm") or "")
        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("main.signup"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("main.signup"))
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.signup"))
        existing, _ = query("SELECT id FROM admins WHERE username=%s", (username,), fetch="one")
        if existing:
            flash("Username already taken. Please pick another.", "danger")
            return redirect(url_for("main.signup"))
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        query("INSERT INTO admins (username, password_hash, full_name) VALUES (%s,%s,%s)",
              (username, pw_hash, full_name or username), commit=True)
        flash("Account created. Please log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("signup.html")


@bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.login"))


# ---------- dashboard ----------
@bp.route("/dashboard")
@login_required
def dashboard():
    stats, _ = query("""
        SELECT
          (SELECT COUNT(*) FROM orders) AS total_orders,
          (SELECT COALESCE(SUM(total),0) FROM orders WHERE status<>'Cancelled') AS total_revenue,
          (SELECT COUNT(*) FROM menu_items) AS total_items,
          (SELECT COUNT(*) FROM orders WHERE status='Pending') AS pending_orders
    """, fetch="one")
    recent, _ = query("""SELECT id, customer_name, total, status, created_at
                          FROM orders ORDER BY id DESC LIMIT 8""", fetch="all")
    chart, _ = query("""SELECT DATE(created_at) d, COALESCE(SUM(total),0) total
                         FROM orders WHERE status<>'Cancelled'
                         GROUP BY DATE(created_at) ORDER BY d DESC LIMIT 7""", fetch="all")
    chart = list(reversed(chart or []))
    return render_template("dashboard.html",
                           stats=stats, recent=recent,
                           chart_labels=[str(r["d"]) for r in chart],
                           chart_values=[float(r["total"]) for r in chart])


# ---------- menu ----------
@bp.route("/menu")
@login_required
def menu():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "").strip()
    sql = "SELECT * FROM menu_items WHERE 1=1"
    params = []
    if q:
        sql += " AND name LIKE %s"; params.append(f"%{q}%")
    if cat:
        sql += " AND category=%s"; params.append(cat)
    sql += " ORDER BY id DESC"
    items, _ = query(sql, params, fetch="all")
    cats, _ = query("SELECT DISTINCT category FROM menu_items ORDER BY category", fetch="all")
    return render_template("menu.html", items=items, categories=cats, q=q, cat=cat)


@bp.route("/menu/new", methods=["GET", "POST"])
@login_required
def menu_new():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category = (request.form.get("category") or "").strip()
        price = request.form.get("price") or "0"
        description = (request.form.get("description") or "").strip()
        if not name or not category or not price:
            flash("Name, category and price are required.", "danger")
            return redirect(url_for("main.menu_new"))
        image = save_image(request.files.get("image")) or (request.form.get("image_url") or "").strip() or None
        query("""INSERT INTO menu_items (name, category, price, description, image)
                 VALUES (%s,%s,%s,%s,%s)""",
              (name, category, Decimal(price), description, image), commit=True)
        flash("Menu item added.", "success")
        return redirect(url_for("main.menu"))
    return render_template("menu_form.html", item=None)


@bp.route("/menu/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
def menu_edit(item_id):
    item, _ = query("SELECT * FROM menu_items WHERE id=%s", (item_id,), fetch="one")
    if not item:
        abort(404)
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        category = (request.form.get("category") or "").strip()
        price = request.form.get("price") or "0"
        description = (request.form.get("description") or "").strip()
        available = 1 if request.form.get("available") == "on" else 0
        image = save_image(request.files.get("image")) or (request.form.get("image_url") or "").strip() or item["image"]
        query("""UPDATE menu_items SET name=%s, category=%s, price=%s,
                 description=%s, image=%s, available=%s WHERE id=%s""",
              (name, category, Decimal(price), description, image, available, item_id),
              commit=True)
        flash("Menu item updated.", "success")
        return redirect(url_for("main.menu"))
    return render_template("menu_form.html", item=item)


@bp.route("/menu/<int:item_id>/delete", methods=["POST"])
@login_required
def menu_delete(item_id):
    query("DELETE FROM menu_items WHERE id=%s", (item_id,), commit=True)
    flash("Menu item deleted.", "info")
    return redirect(url_for("main.menu"))


# ---------- orders ----------
@bp.route("/orders")
@login_required
def orders():
    status = request.args.get("status", "").strip()
    q = request.args.get("q", "").strip()
    sql = "SELECT * FROM orders WHERE 1=1"
    params = []
    if status:
        sql += " AND status=%s"; params.append(status)
    if q:
        sql += " AND customer_name LIKE %s"; params.append(f"%{q}%")
    sql += " ORDER BY id DESC"
    rows, _ = query(sql, params, fetch="all")
    return render_template("orders.html", orders=rows, status=status, q=q)


@bp.route("/orders/new", methods=["GET", "POST"])
@login_required
def order_new():
    if request.method == "POST":
        customer_name = (request.form.get("customer_name") or "Walk-in").strip()
        ids = request.form.getlist("item_id[]")
        qtys = request.form.getlist("qty[]")
        if not ids:
            flash("Add at least one item.", "danger")
            return redirect(url_for("main.order_new"))
        total = Decimal("0")
        line_items = []
        for iid, qty in zip(ids, qtys):
            try:
                qty = int(qty)
            except ValueError:
                qty = 0
            if qty <= 0:
                continue
            it, _ = query("SELECT * FROM menu_items WHERE id=%s", (iid,), fetch="one")
            if not it:
                continue
            sub = Decimal(str(it["price"])) * qty
            total += sub
            line_items.append((it, qty, sub))
        if not line_items:
            flash("Add at least one item with quantity > 0.", "danger")
            return redirect(url_for("main.order_new"))
        _, order_id = query(
            "INSERT INTO orders (customer_name, total, source) VALUES (%s,%s,'admin')",
            (customer_name, total), commit=True)
        for it, qty, sub in line_items:
            query("""INSERT INTO order_details
                     (order_id, menu_item_id, item_name, price, quantity, subtotal)
                     VALUES (%s,%s,%s,%s,%s,%s)""",
                  (order_id, it["id"], it["name"], it["price"], qty, sub), commit=True)
        flash("Order created.", "success")
        return redirect(url_for("main.order_view", order_id=order_id))
    items, _ = query("SELECT * FROM menu_items WHERE available=1 ORDER BY category, name",
                     fetch="all")
    return render_template("order_new.html", items=items)


@bp.route("/orders/<int:order_id>")
@login_required
def order_view(order_id):
    order, _ = query("SELECT * FROM orders WHERE id=%s", (order_id,), fetch="one")
    if not order:
        abort(404)
    details, _ = query("SELECT * FROM order_details WHERE order_id=%s", (order_id,), fetch="all")
    return render_template("order_view.html", order=order, details=details)


@bp.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
def order_status(order_id):
    status = request.form.get("status")
    if status not in ("Pending", "Preparing", "Served", "Completed", "Cancelled"):
        flash("Invalid status.", "danger")
        return redirect(url_for("main.order_view", order_id=order_id))
    query("UPDATE orders SET status=%s WHERE id=%s", (status, order_id), commit=True)
    flash(f"Order #{order_id} marked {status}.", "success")
    return redirect(url_for("main.order_view", order_id=order_id))


@bp.route("/orders/<int:order_id>/delete", methods=["POST"])
@login_required
def order_delete(order_id):
    query("DELETE FROM orders WHERE id=%s", (order_id,), commit=True)
    flash("Order deleted.", "info")
    return redirect(url_for("main.orders"))


# ---------- customer (public) ----------
@bp.route("/cafe")
def customer():
    items, _ = query("SELECT * FROM menu_items WHERE available=1 ORDER BY category, name",
                     fetch="all")
    return render_template("customer.html", items=items)


@bp.route("/api/place_order", methods=["POST"])
def api_place_order():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "Guest").strip()[:100]
    cart = data.get("cart") or []
    if not cart:
        return jsonify({"ok": False, "error": "Cart is empty"}), 400
    total = Decimal("0")
    valid = []
    for c in cart:
        it, _ = query("SELECT * FROM menu_items WHERE id=%s AND available=1",
                      (c.get("id"),), fetch="one")
        if not it:
            continue
        qty = max(1, int(c.get("qty", 1)))
        sub = Decimal(str(it["price"])) * qty
        total += sub
        valid.append((it, qty, sub))
    if not valid:
        return jsonify({"ok": False, "error": "No valid items"}), 400
    _, order_id = query(
        "INSERT INTO orders (customer_name, total, source) VALUES (%s,%s,'customer')",
        (name, total), commit=True)
    for it, qty, sub in valid:
        query("""INSERT INTO order_details
                 (order_id, menu_item_id, item_name, price, quantity, subtotal)
                 VALUES (%s,%s,%s,%s,%s,%s)""",
              (order_id, it["id"], it["name"], it["price"], qty, sub), commit=True)
    return jsonify({"ok": True, "order_id": order_id, "total": float(total)})


@bp.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
