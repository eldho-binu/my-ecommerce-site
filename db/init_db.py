import sqlite3

# Connect to SQLite DB (creates the file if it doesn't exist)
connection = sqlite3.connect("products.db")

# Read and execute the SQL schema file
with open("schema.sql") as f:
    connection.executescript(f.read())

# Get a cursor to run SQL commands
cur = connection.cursor()

# Insert sample product data
cur.execute("INSERT INTO products (name, price, image_url) VALUES (?, ?, ?)",
            ("Electric Toothbrush", 1299, "static/images/tooth.jpeg"))

cur.execute("INSERT INTO products (name, price, image_url) VALUES (?, ?, ?)",
            ("Herbal Face Cream", 499, "static/images/face.png"))

cur.execute("INSERT INTO products (name, price, image_url) VALUES (?, ?, ?)",
            ("Running Shoes", 999, "static/images/shoe.jpg"))

# Save changes and close the connection
connection.commit()
connection.close()
