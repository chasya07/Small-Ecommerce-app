from flask import Flask, redirect, session
import sqlite3
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"

DB_NAME = "store.db"


# Generate simple SVG product image
def generate_image(text):
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="500" height="400">
        <rect width="100%" height="100%" fill="#2563eb"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
              font-size="40" fill="white" font-family="Arial">
            {text}
        </text>
    </svg>
    """
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


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
            ("T-Shirt", 20, generate_image("T-Shirt")),
            ("Running Shoes", 75, generate_image("Shoes")),
            ("Luxury Watch", 199, generate_image("Watch")),
            ("Leather Wallet", 45, generate_image("Wallet")),
            ("Wireless Headphones", 120, generate_image("Headphones")),
            ("Smartphone", 699, generate_image("Phone")),
            ("Backpack", 60, generate_image("Backpack")),
            ("Sunglasses", 35, generate_image("Sunglasses")),
            ("Gaming Mouse", 55, generate_image("Mouse")),
            ("Bluetooth Speaker", 85, generate_image("Speaker"))
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


init_db()


# ---------------- TEMPLATE ----------------
def render_page(content):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Modern eCommerce</title>
        <style>
            body {{ margin:0; font-family:Arial; background:#f4f6f9; }}
            header {{ background:#111827; color:white; padding:20px; text-align:center; }}
            nav {{ background:#1f2937; padding:12px; text-align:center; }}
            nav a {{ color:white; margin:0 15px; text-decoration:none; }}
            .container {{ width:90%; margin:30px auto; }}
            .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:25px; }}
            .card {{ background:white; border-radius:10px; box-shadow:0 6px 15px rgba(0,0,0,0.08); overflow:hidden; }}
            .card img {{ width:100%; height:220px; object-fit:cover; }}
            .card-content {{ padding:15px; text-align:center; }}
            .btn {{ background:#2563eb; color:white; padding:8px 14px; border-radius:6px; text-decoration:none; display:inline-block; margin-top:8px; }}
            .total {{ margin-top:20px; font-size:22px; font-weight:bold; }}
            footer {{ background:#111827; color:white; text-align:center; padding:20px; margin-top:40px; }}
        </style>
    </head>
    <body>
        <header><h1>🛒 Modern eCommerce Store</h1></header>
        <nav>
            <a href="/">Home</a>
            <a href="/cart">Cart</a>
        </nav>
        <div class="container">{content}</div>
        <footer>© 2026 DevOps CI/CD Project</footer>
    </body>
    </html>
    """


# ---------------- ROUTES ----------------
@app.route("/")
def home():
    products = get_products()
    content = "<h2>Featured Products</h2><div class='grid'>"

    for p in products:
        content += f"""
        <div class="card">
            <img src="{p['image']}">
            <div class="card-content">
                <h3>{p['name']}</h3>
                <p><strong>${p['price']}</strong></p>
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
    content = "<h2>Your Cart</h2>"
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
                        <p>${product['price']}</p>
                    </div>
                </div>
                """
        content += "</div>"
        content += f"<div class='total'>Total: ${total}</div>"
        content += "<a class='btn' href='/checkout'>Checkout</a>"
    else:
        content += "<p>Your cart is empty.</p>"

    return render_page(content)


@app.route("/checkout")
def checkout():
    session.pop("cart", None)
    return render_page("""
        <h2>🎉 Order Confirmed!</h2>
        <a class="btn" href="/">Continue Shopping</a>
    """)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
