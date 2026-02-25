from flask import Flask, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "store.db"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL
    )
    """)
    
    products = conn.execute("SELECT * FROM products").fetchall()
    
    if not products:
        conn.execute("INSERT INTO products (name, price) VALUES ('T-Shirt', 20)")
        conn.execute("INSERT INTO products (name, price) VALUES ('Shoes', 50)")
        conn.execute("INSERT INTO products (name, price) VALUES ('Watch', 100)")
        conn.commit()
    
    conn.close()

def get_products():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return products

def get_product(product_id):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    product = conn.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
    conn.close()
    return product

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    products = get_products()

    html = """
    <h1>Mini eCommerce Store 🛒</h1>
    <a href='/cart'>View Cart</a>
    <hr>
    """

    for p in products:
        html += f"""
        <h3>{p['name']}</h3>
        <p>Price: ${p['price']}</p>
        <a href='/add/{p['id']}'>Add to Cart</a>
        <hr>
        """

    return html


@app.route("/add/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True
    return redirect("/")


@app.route("/cart")
def cart():
    html = "<h1>Your Cart 🛍</h1><a href='/'>Continue Shopping</a><hr>"
    total = 0

    if "cart" in session:
        for item_id in session["cart"]:
            product = get_product(item_id)
            if product:
                total += product["price"]
                html += f"<p>{product['name']} - ${product['price']}</p>"

    html += f"<h3>Total: ${total}</h3>"
    html += "<br><a href='/checkout'>Checkout</a>"

    return html


@app.route("/checkout")
def checkout():
    session.pop("cart", None)
    return """
    <h1>Order Placed Successfully! 🎉</h1>
    <a href='/'>Back to Home</a>
    """

# Initialize database when module loads
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
