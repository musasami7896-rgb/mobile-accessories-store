from flask import Flask, session, redirect, url_for, request, render_template_string
import sqlite3
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "store123"

WHATSAPP_NUMBER = "923224440476"


# =========================
# BRANDS AND MODELS
# =========================

brands = {
    "Samsung": [
        "Galaxy S25", "Galaxy S24", "Galaxy S23",
        "Galaxy S22", "Galaxy S21", "Galaxy A56",
        "Galaxy A55", "Galaxy A54", "Galaxy A53",
        "Galaxy A52", "Galaxy A36", "Galaxy A35",
        "Galaxy A34", "Galaxy A33", "Galaxy A26",
        "Galaxy A25"
    ],
    "iPhone": [
        "iPhone 17", "iPhone 16", "iPhone 15",
        "iPhone 14", "iPhone 13", "iPhone 12",
        "iPhone 11", "iPhone SE"
    ],
    "Redmi": [
        "Redmi Note 14", "Redmi Note 13",
        "Redmi Note 12", "Redmi Note 11",
        "Redmi 14C", "Redmi 13C", "Redmi 12",
        "Redmi 10", "Redmi 9"
    ]
}


# =========================
# ACCESSORIES AND IMAGES
# =========================

accessories = [
    ("📱", "Mobile Cover / Pouch", "cover"),
    ("🛡️", "Screen Protector", "protector"),
    ("🔌", "Charger", "charger"),
    ("🔗", "Data Cable", "cable"),
    ("🎧", "Earpods / Earbuds", "earbuds")
]

images = {
    "Mobile Cover / Pouch":
        "https://images.unsplash.com/photo-1601593346740-925612772716?auto=format&fit=crop&w=800&q=80",
    "Screen Protector":
        "https://images.unsplash.com/photo-1556656793-08538906a9f8?auto=format&fit=crop&w=800&q=80",
    "Charger":
        "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80",
    "Data Cable":
        "https://images.unsplash.com/photo-1609592424811-5f1e8c8b6d9d?auto=format&fit=crop&w=800&q=80",
    "Earpods / Earbuds":
        "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?auto=format&fit=crop&w=800&q=80"
}

accessory_slugs = {
    slug: name for icon, name, slug in accessories
}


# =========================
# PRICE FUNCTION
# =========================

def get_price(model):
    if model.startswith("iPhone"):
        return 600
    elif model.startswith("Galaxy"):
        return 500
    elif model.startswith("Redmi"):
        return 400
    return 0


# =========================
# DATABASE
# =========================

def create_database():
    conn = sqlite3.connect("orders.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            address TEXT,
            product TEXT,
            total INTEGER
        )
    """)
    conn.commit()
    conn.close()


create_database()


# =========================
# CART HELPER
# =========================

def get_cart():
    cart = session.get("cart", {})

    # Convert an older list-style cart to a dictionary
    if isinstance(cart, list):
        new_cart = {}
        for item in cart:
            new_cart[item] = new_cart.get(item, 0) + 1
        cart = new_cart
        session["cart"] = cart

    return cart


# =========================
# COMMON PAGE STYLE
# =========================

STYLE = """
<style>
* { box-sizing: border-box; }

body {
    font-family: Arial, sans-serif;
    background: #f2f2f2;
    margin: 0;
    color: #222;
}

.header {
    background: #111;
    color: white;
    padding: 24px 15px;
    text-align: center;
}

.container {
    max-width: 850px;
    margin: auto;
    padding: 18px;
}

.search, input, textarea {
    width: 100%;
    padding: 14px;
    border: 1px solid #ccc;
    border-radius: 9px;
    font-size: 16px;
    margin-bottom: 15px;
}

.button, .model, .add, .checkout, .back,
.remove, .whatsapp {
    display: block;
    padding: 15px;
    margin: 12px 0;
    border-radius: 9px;
    text-align: center;
    text-decoration: none;
    font-weight: bold;
}

.button, .model {
    background: white;
    color: #111;
    box-shadow: 0 3px 8px #ddd;
}

.add, .checkout {
    background: #198754;
    color: white;
}

.whatsapp {
    background: #25D366;
    color: white;
}

.back {
    background: #444;
    color: white;
}

.remove {
    background: #dc3545;
    color: white;
}

.card, .item, .summary, .form-box {
    background: white;
    margin: 15px 0;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 3px 8px #ddd;
}

.card img {
    width: 100%;
    height: 210px;
    object-fit: cover;
    border-radius: 8px;
}

.info {
    text-align: center;
}

.price, .total {
    font-size: 22px;
    font-weight: bold;
}

.quantity {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 22px;
    margin: 15px;
}

.quantity a {
    background: #111;
    color: white;
    text-decoration: none;
    padding: 8px 14px;
    border-radius: 7px;
}

button {
    width: 100%;
    background: #198754;
    color: white;
    border: none;
    padding: 15px;
    border-radius: 9px;
    font-size: 18px;
    font-weight: bold;
}

.total {
    background: #198754;
    color: white;
    text-align: center;
    padding: 17px;
    border-radius: 9px;
}

textarea {
    min-height: 100px;
}
</style>
"""


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():
    cart_count = sum(get_cart().values())

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Mobile Accessories Store</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        {{ style|safe }}
    </head>
    <body>
        <div class="header">
            <h1>My Mobile Accessories Store</h1>
            <p>Quality Mobile Accessories</p>
        </div>

        <div class="container">
            <input class="search" id="search"
                   placeholder="Search Samsung, iPhone or Redmi..."
                   oninput="searchBrands()">

            <div id="brands">
                <a class="button" href="/brand/Samsung">📱 Samsung</a>
                <a class="button" href="/brand/iPhone">🍎 iPhone</a>
                <a class="button" href="/brand/Redmi">📱 Redmi</a>
            </div>

            <a class="button" href="/cart">
                🛒 Cart ({{ count }})
            </a>

            <a class="whatsapp"
               href="https://wa.me/923224440476"
               target="_blank">
                💬 Chat on WhatsApp
            </a>
        </div>

        <script>
        function searchBrands() {
            let value = document.getElementById("search")
                .value.toLowerCase();

            document.querySelectorAll("#brands a").forEach(
                function(item) {
                    item.style.display =
                        item.innerText.toLowerCase().includes(value)
                        ? "block" : "none";
                }
            );
        }
        </script>
    </body>
    </html>
    """, style=STYLE, count=cart_count)


# =========================
# BRAND PAGE
# =========================

@app.route("/brand/<brand>")
def brand_page(brand):
    if brand not in brands:
        return "Brand not found", 404

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ brand }} Models</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        {{ style|safe }}
    </head>
    <body>
        <div class="header">
            <h1>{{ brand }}</h1>
            <p>Select your mobile model</p>
        </div>

        <div class="container">
            <input class="search" id="search"
                   placeholder="Search model..."
                   oninput="searchModels()">

            <div id="models">
            {% for model in models %}
                <a class="model"
                   href="{{ url_for('product_page',
                                    model=model.replace(' ', '_')) }}">
                    📱 {{ model }}
                </a>
            {% endfor %}
            </div>

            <a class="back" href="/">⬅️ Back to Home</a>
        </div>

        <script>
        function searchModels() {
            let value = document.getElementById("search")
                .value.toLowerCase();

            document.querySelectorAll("#models a").forEach(
                function(item) {
                    item.style.display =
                        item.innerText.toLowerCase().includes(value)
                        ? "block" : "none";
                }
            );
        }
        </script>
    </body>
    </html>
    """, style=STYLE, brand=brand, models=brands[brand])


# =========================
# PRODUCT PAGE
# =========================

@app.route("/product/<model>")
def product_page(model):
    model = model.replace("_", " ")

    if not any(model in models for models in brands.values()):
        return "Model not found", 404

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ model }} Accessories</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        {{ style|safe }}
    </head>
    <body>
        <div class="header">
            <h1>{{ model }}</h1>
            <p>Available Accessories</p>
        </div>

        <div class="container">
        {% for icon, accessory, slug in accessories %}
            <div class="card">
                <img src="{{ images[accessory] }}"
                     alt="{{ accessory }}">

                <div class="info">
                    <h2>{{ icon }} {{ accessory }}</h2>
                    <p class="price">Rs. {{ price }}</p>

                    <a class="add"
                       href="{{ url_for('add_to_cart',
                                        model=model.replace(' ', '_'),
                                        accessory=slug) }}">
                        🛒 Add to Cart
                    </a>
                </div>
            </div>
        {% endfor %}

            <a class="button" href="/cart">🛒 View Cart</a>
            <a class="back" href="/">⬅️ Home</a>
        </div>
    </body>
    </html>
    """, style=STYLE, model=model, price=get_price(model),
       accessories=accessories, images=images)


# =========================
# ADD TO CART
# =========================

@app.route("/add/<model>/<accessory>")
def add_to_cart(model, accessory):
    model = model.replace("_", " ")

    if accessory not in accessory_slugs:
        return "Accessory not found", 404

    accessory_name = accessory_slugs[accessory]
    item = model + " - " + accessory_name

    cart = get_cart()
    cart[item] = cart.get(item, 0) + 1
    session["cart"] = cart

    return redirect(url_for("cart"))


# =========================
# CART QUANTITY CONTROLS
# =========================

@app.route("/increase/<path:item>")
def increase(item):
    cart = get_cart()

    if item in cart:
        cart[item] += 1

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/decrease/<path:item>")
def decrease(item):
    cart = get_cart()

    if item in cart:
        cart[item] -= 1

        if cart[item] <= 0:
            del cart[item]

    session["cart"] = cart
    return redirect(url_for("cart"))


@app.route("/remove/<path:item>")
def remove(item):
    cart = get_cart()

    if item in cart:
        del cart[item]

    session["cart"] = cart
    return redirect(url_for("cart"))


# =========================
# CART PAGE
# =========================

@app.route("/cart")
def cart():
    cart_items = []
    total = 0

    for item, quantity in get_cart().items():
        model = item.split(" - ")[0]
        price = get_price(model)
        subtotal = price * quantity
        total += subtotal

        cart_items.append({
            "name": item,
            "quantity": quantity,
            "price": price,
            "subtotal": subtotal
        })

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Shopping Cart</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        {{ style|safe }}
    </head>
    <body>
        <div class="header"><h1>🛒 Shopping Cart</h1></div>

        <div class="container">
        {% if items %}
            {% for item in items %}
                <div class="item">
                    <h3>{{ item.name }}</h3>
                    <p>Price: Rs. {{ item.price }}</p>

                    <div class="quantity">
                        <a href="{{ url_for('decrease',
                                            item=item.name) }}">➖</a>
                        <strong>{{ item.quantity }}</strong>
                        <a href="{{ url_for('increase',
                                            item=item.name) }}">➕</a>
                    </div>

                    <p>Subtotal: <b>Rs. {{ item.subtotal }}</b></p>

                    <a class="remove"
                       href="{{ url_for('remove',
                                        item=item.name) }}">
                        🗑️ Remove
                    </a>
                </div>
            {% endfor %}

            <div class="total">Total: Rs. {{ total }}</div>

            <a class="checkout" href="/order">✅ Checkout</a>
        {% else %}
            <div class="item">
                <h2>Your cart is empty 🛒</h2>
            </div>
        {% endif %}

            <a class="back" href="/">⬅️ Continue Shopping</a>
        </div>
    </body>
    </html>
    """, style=STYLE, items=cart_items, total=total)


# =========================
# CHECKOUT AND ORDER
# =========================

@app.route("/order", methods=["GET", "POST"])
def order():
    cart = get_cart()

    if not cart:
        return """
        <h2 style="text-align:center">Your cart is empty.</h2>
        <p style="text-align:center"><a href="/">Back to store</a></p>
        """

    total = 0
    order_items = []

    for item, quantity in cart.items():
        model = item.split(" - ")[0]
        subtotal = get_price(model) * quantity
        total += subtotal

        order_items.append({
            "name": item,
            "quantity": quantity,
            "subtotal": subtotal
        })

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not phone or not address:
            return "Please fill in all fields.", 400

        product_text = "\n".join(
            item + " x " + str(quantity)
            for item, quantity in cart.items()
        )

        conn = sqlite3.connect("orders.db")
        conn.execute(
            "INSERT INTO orders "
            "(name, phone, address, product, total) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, phone, address, product_text, total)
        )
        conn.commit()
        conn.close()

        whatsapp_message = (
            "New Order\n\n"
            + "Name: " + name + "\n"
            + "Phone: " + phone + "\n"
            + "Address: " + address + "\n\n"
            + "Products:\n" + product_text + "\n\n"
            + "Total: Rs. " + str(total)
        )

        whatsapp_link = (
            "https://wa.me/" + WHATSAPP_NUMBER
            + "?text=" + quote(whatsapp_message)
        )

        session["cart"] = {}

        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Order Received</title>
            <meta name="viewport"
                  content="width=device-width, initial-scale=1">
            {{ style|safe }}
        </head>
        <body>
            <div class="container">
                <div class="item" style="text-align:center">
                    <h1>✅ Order Received!</h1>
                    <h2>Thank you, {{ name }}!</h2>
                    <p>Your order has been saved.</p>
                    <p class="price">Total: Rs. {{ total }}</p>

                    <a class="whatsapp"
                       href="{{ whatsapp_link }}"
                       target="_blank">
                        💬 Send Order on WhatsApp
                    </a>

                    <a class="back" href="/">🏠 Back to Store</a>
                </div>
            </div>
        </body>
        </html>
        """, style=STYLE, name=name, total=total,
           whatsapp_link=whatsapp_link)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Checkout</title>
        <meta name="viewport"
              content="width=device-width, initial-scale=1">
        {{ style|safe }}
    </head>
    <body>
        <div class="header">
            <h1>🛍️ Checkout</h1>
            <p>Review your order</p>
        </div>

        <div class="container">
            <div class="summary">
                <h2>Order Summary</h2>

                <ul>
                {% for item in items %}
                    <li>
                        {{ item.name }} × {{ item.quantity }}
                        = Rs. {{ item.subtotal }}
                    </li>
                {% endfor %}
                </ul>

                <div class="total">Total: Rs. {{ total }}</div>
            </div>

            <div class="form-box">
                <form method="POST">
                    <label><b>Your Name</b></label>
                    <input type="text" name="name"
                           placeholder="Enter your name" required>

                    <label><b>Phone Number</b></label>
                    <input type="tel" name="phone"
                           placeholder="03XXXXXXXXX" required>

                    <label><b>Delivery Address</b></label>
                    <textarea name="address"
                              placeholder="Enter complete delivery address"
                              required></textarea>

                    <button type="submit">✅ Place Order</button>
                </form>
            </div>

            <a class="back" href="/cart">⬅️ Back to Cart</a>
        </div>
    </body>
    </html>
    """, style=STYLE, items=order_items, total=total)


# =========================
# RUN WEBSITE
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )