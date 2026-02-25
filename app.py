from flask import Flask, redirect, session
import sqlite3

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

    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    if count == 0:
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
    product = conn.execute(
        "SELECT * FROM products WHERE id=?", (product_id,)
    ).fetchone()
    conn.close()
    return product


# Initialize DB
init_db()


# ---------------- HTML TEMPLATE ----------------
def render_page(content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mini eCommerce</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                background: #f4f6f9;
            }}
            header {{
                background: #1f2937;
                color: white;
                padding: 15px;
                text-align: center;
            }}
            nav {{
                background: #111827;
                padding: 10px;
                text-align: center;
            }}
            nav a {{
                color: white;
                margin: 0 15px;
                text-decoration: none;
                font-weight: bold;
            }}
            .container {{
                width: 80%;
                margin: 30px auto;
            }}
            .product {{
                background: white;
                padding: 20px;
                margin: 15px 0;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .btn {{
                display: inline-block;
                padding: 8px 12px;
                background: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 10px;
            }}
            .btn:hover {{
                background: #1d4ed8;
            }}
            footer {{
                text-align: center;
                padding: 20px;
                background: #1f2937;
                color: white;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>🛒 Mini eCommerce Store</h1>
        </header>
        <nav>
            <a href="/">Home</a>
            <a href="/cart">Cart</a>
        </nav>
        <div class="container">
            {content}
        </div>
        <footer>
            © 2026 Mini eCommerce | DevOps Project
        </footer>
    </body>
    </html>
    """


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    products = get_products()
    content = "<h2>Available Products</h2>"

    for p in products:
        content += f"""
        <div class="product">
            <h3>{p['name']}</h3>
            <p><strong>Price:</strong> ${p['price']}</p>
            <a class="btn" href="/add/{p['id']}">Add to Cart</a>
        </div>
        """

    return render_page(content)


@app.route("/add/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True
    return redirect("/")


@app.route("/cart")
def cart():
    content = "<h2>Your Cart 🛍</h2>"
    total = 0

    if "cart" in session and session["cart"]:
        for item_id in session["cart"]:
            product = get_product(item_id)
            if product:
                total += product["price"]
                content += f"""
                <div class="product">
                    <h3>{product['name']}</h3>
                    <p>Price: ${product['price']}</p>
                </div>
                """
        content += f"<h3>Total: ${total}</h3>"
        content += '<a class="btn" href="/checkout">Checkout</a>'
    else:
        content += "<p>Your cart is empty.</p>"

    return render_page(content)


@app.route("/checkout")
def checkout():
    session.pop("cart", None)
    content = """
        <h2>🎉 Order Placed Successfully!</h2>
        <p>Thank you for shopping with us.</p>
        <a class="btn" href="/">Continue Shopping</a>
    """
    return render_page(content)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
