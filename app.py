from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "transitmanager.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True) if os.path.dirname(DB_PATH) else None
app = Flask(__name__, static_folder=BASE_DIR)


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            text TEXT NOT NULL,
            author TEXT NOT NULL,
            media TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            method TEXT NOT NULL,
            status TEXT DEFAULT 'en_attente',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT
        );
        CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT
        );
        CREATE TABLE IF NOT EXISTS trucks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT UNIQUE NOT NULL,
            model TEXT,
            driver TEXT
        );
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            employee TEXT,
            site TEXT,
            client TEXT,
            plate TEXT,
            driver TEXT,
            packaging TEXT,
            status TEXT DEFAULT 'En attente'
        );
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            plate TEXT,
            type TEXT,
            amount REAL,
            description TEXT,
            status TEXT DEFAULT 'En attente'
        );
    """)

    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.executemany("INSERT INTO users(name, role, login, password) VALUES(?,?,?,?)", (
            ("Sage Kiwala", "admin", "admin", "Admin@2026"),
            ("Marie Finance", "secondary", "finance", "Finance@2026"),
            ("Patrick Employé", "employee", "employe", "Employe@2026"),
        ))
    db.commit()
    db.close()


def rows(table):
    db = get_db()
    result = [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()]
    db.close()
    return result


@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/<path:path>")
def public_files(path):
    file_path = os.path.join(BASE_DIR, path)
    if os.path.isfile(file_path):
        return send_from_directory(BASE_DIR, path)
    return jsonify(error="Not found"), 404


@app.route("/api/health")
def health():
    return jsonify(status="ok", database=os.path.basename(DB_PATH))


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    db = get_db()
    user = db.execute(
        "SELECT id, name, role, login FROM users WHERE login=? AND password=?",
        (data.get("login", ""), data.get("password", "")),
    ).fetchone()
    db.close()
    if not user:
        return jsonify(error="Identifiant ou mot de passe incorrect"), 401
    return jsonify(dict(user))


@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    if request.method == "GET":
        return jsonify(rows("posts"))
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify(error="Le texte est obligatoire"), 400
    db = get_db()
    cursor = db.execute(
        "INSERT INTO posts(title, text, author, media) VALUES(?,?,?,?)",
        (data.get("title"), text, data.get("author", "Utilisateur"), data.get("media")),
    )
    db.commit()
    post_id = cursor.lastrowid
    post = db.execute("SELECT * FROM posts WHERE id=?", (post_id,)).fetchone()
    db.close()
    return jsonify(dict(post)), 201


@app.route("/api/donations", methods=["GET", "POST"])
def donations():
    if request.method == "GET":
        return jsonify(rows("donations"))
    data = request.get_json(silent=True) or {}
    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify(error="Montant invalide"), 400
    if amount <= 0:
        return jsonify(error="Montant invalide"), 400
    db = get_db()
    cursor = db.execute(
        "INSERT INTO donations(amount, method, status) VALUES(?,?,?)",
        (amount, data.get("method", "Mobile Money"), "en_attente"),
    )
    db.commit()
    donation_id = cursor.lastrowid
    donation = db.execute("SELECT * FROM donations WHERE id=?", (donation_id,)).fetchone()
    db.close()
    return jsonify(dict(donation)), 201


@app.route("/api/<table>", methods=["GET", "POST"])
def collection(table):
    allowed = {"users": ("name", "role", "login", "password", "phone"), "clients": ("name", "phone"), "sites": ("name", "location"), "trucks": ("plate", "model", "driver")}
    if table not in allowed:
        return jsonify(error="Collection inconnue"), 404
    if request.method == "GET":
        return jsonify(rows(table))
    data = request.get_json(silent=True) or {}
    fields = allowed[table]
    if table == "users":
        required = ("name", "role", "login", "password")
    elif table == "clients":
        required = ("name",)
    elif table == "sites":
        required = ("name",)
    else:
        required = ("plate",)
    if any(not data.get(field) for field in required):
        return jsonify(error="Champs obligatoires manquants"), 400
    placeholders = ", ".join("?" for _ in fields if field in data)
    names = [field for field in fields if field in data]
    values = [data[field] for field in names]
    db = get_db()
    try:
        cursor = db.execute(f"INSERT INTO {table}({', '.join(names)}) VALUES({placeholders})", values)
        db.commit()
        item_id = cursor.lastrowid
        item = db.execute(f"SELECT * FROM {table} WHERE id=?", (item_id,)).fetchone()
    except sqlite3.IntegrityError as exc:
        db.close()
        return jsonify(error=str(exc)), 409
    db.close()
    return jsonify(dict(item)), 201


@app.route("/api/registrations", methods=["GET", "POST"])
def registrations():
    if request.method == "GET":
        return jsonify(rows("registrations"))
    data = request.get_json(silent=True) or {}
    fields = ("date", "employee", "site", "client", "plate", "driver", "packaging", "status")
    names = [f for f in fields if f in data]
    values = [data[f] for f in names]
    db = get_db()
    cursor = db.execute(f"INSERT INTO registrations({', '.join(names)}) VALUES({', '.join('?' for _ in names)})", values)
    db.commit()
    item = db.execute("SELECT * FROM registrations WHERE id=?", (cursor.lastrowid,)).fetchone()
    db.close()
    return jsonify(dict(item)), 201


@app.route("/api/transactions", methods=["GET", "POST"])
def transactions():
    if request.method == "GET":
        return jsonify(rows("transactions"))
    data = request.get_json(silent=True) or {}
    fields = ("date", "plate", "type", "amount", "description", "status")
    names = [f for f in fields if f in data]
    values = [data[f] for f in names]
    db = get_db()
    cursor = db.execute(f"INSERT INTO transactions({', '.join(names)}) VALUES({', '.join('?' for _ in names)})", values)
    db.commit()
    item = db.execute("SELECT * FROM transactions WHERE id=?", (cursor.lastrowid,)).fetchone()
    db.close()
    return jsonify(dict(item)), 201


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
