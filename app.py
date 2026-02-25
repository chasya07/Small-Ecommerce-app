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
            price REAL NOT NULL,
            image TEXT NOT NULL
        )
    """)

    count = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]

    if count == 0:
        products = [
            ("T-Shirt", 20, "https://source.unsplash.com/500x500/?tshirt"),
            ("Running Shoes", 75, "https://source.unsplash.com/500x500/?running-shoes"),
            ("Luxury Watch", 199, "https://source.unsplash.com/500x500/?luxury-watch"),
            ("Leather Wallet", 45, "https://source.unsplash.com/500x500/?leather-wallet"),
            ("Wireless Headphones", 120, "https://source.unsplash.com/500x500/?wireless-headphones"),
            ("Smartphone", 699, "https://source.unsplash.com/500x500/?smartphone"),
            ("Backpack", 60, "https://source.unsplash.com/500x500/?backpack"),
            ("Sunglasses", 35, "https://source.unsplash.com/500x500/?sunglasses"),
            ("Gaming Mouse", 55, "https://source.unsplash.com/500x500/?gaming-mouse"),
            ("Bluetooth Speaker", 85, "https://source.unsplash.com/500x500/?bluetooth-speaker")
        ]

        conn.executemany(
            "INSERT INTO products (name, price, image) VALUES (?, ?, ?)",
            products
        )

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


# ---------------- TEMPLATE ----------------
def render_page(content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Modern eCommerce</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                font-family: 'Segoe UI', sans-serif;
                background: #f3f4f6;
            }}
            header {{
                background: #111827;
                color: white;
                padding: 20px;
                text-align: center;
            }}
            nav {{
                background: #1f2937;
                padding: 12px;
                text-align: center;
            }}
            nav a {{
                color: white;
                margin: 0 20px;
                text-decoration: none;
                font-weight: bold;
            }}
            .container {{
                width: 90%;
                margin: 30px auto;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
            }}
            .card {{
                background: white;
                border-radius: 12px;
                box-shadow: 0 6px 15px rgba(0,0,0,0.08);
                overflow: hidden;
                transition: transform 0.2s ease;
            }}
            .card:hover {{
                transform: translateY(-5px);
            }}
            .card img {{
                width: 100%;
                height: 220px;
                object-fit: cover;
            }}
            .card-content {{
                padding: 15px;
                text-align: center;
            }}
            .price {{
                font-size: 18px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .btn {{
                display: inline-block;
                padding: 8px 14px;
                background: #2563eb;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 8px;
            }}
            .btn:hover {{
                background: #1d4ed8;
            }}
            .total {{
                margin-top: 20px;
                font-size: 22px;
                font-weight: bold;
            }}
            footer {{
                text-align: center;
                padding: 20px;
                background: #111827;
                color: white;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>🛒 Modern eCommerce Store</h1>
        </header>
        <nav>
            <a href="/">Home</a>
            <a href="/cart">Cart</a>
        </nav>
        <div class="container">
            {content}
        </div>
        <footer>
            © 2026 DevOps CI/CD Project
        </footer>
    </body>
    </html>
    """


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    products = get_products()

    content = "<h2>Featured Products</h2>"
    content += "<div class='grid'>"

    for p in products:
        content += f"""
        <div class="card">
            <img src="{p['image']}">
            <div class="card-content">
                <h3>{p['name']}</h3>
                <div class="price">${p['price']}</div>
                <a class="btn" href="/add/{p['id']}">Add to Cart</a>
            </div>
        </div>
        """

    content += "</div>"
    return render_page(content)


@app.route("/add/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True
    return redirect("/cart")


@app.route("/cart")
def cart():
    content = "<h2>Your Shopping Cart 🛍</h2>"
    total = 0

    if "cart" in session and session["cart"]:
        content += "<div class='grid'>"

        for item_id in session["cart"]:
            product = get_product(item_id)
            if product:
                total += product["price"]
                content += f"""
                <div class="card">
                    <img src="{product['image']}">
                    <div class="card-content">
                        <h3>{product['name']}</h3>
                        <div class="price">${product['price']}</div>
                    </div>
                </div>
                """

        content += "</div>"
        content += f"<div class='total'>Total: ${total}</div>"
        content += "<br><a class='btn' href='/checkout'>Checkout</a>"
    else:
        content += "<p>Your cart is empty.</p>"

    return render_page(content)


@app.route("/checkout")
def checkout():
    session.pop("cart", None)
    content = """
        <h2>🎉 Order Confirmed!</h2>
        <p>Thank you for shopping with us.</p>
        <a class="btn" href="/">Continue Shopping</a>
    """
    return render_page(content)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
