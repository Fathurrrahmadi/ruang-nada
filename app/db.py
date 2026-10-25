# Koneksi database SQLite, pembuatan tabel, dan data awal
import os
import sqlite3
from datetime import date, timedelta

from app.security import hash_password

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "ruangnada.db")


def connect():
    db = sqlite3.connect(DB_PATH, isolation_level=None, timeout=10)
    db.row_factory = sqlite3.Row            # hasil query bisa dibaca per nama kolom
    db.execute("PRAGMA foreign_keys = ON")  # aktifkan foreign key
    return db


# Tabel-tabel ini mengikuti ERD di dokumen
TABLES = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'anggota')),
    is_member INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id),
    phone TEXT,
    address TEXT
);

CREATE TABLE IF NOT EXISTS units (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_code TEXT NOT NULL UNIQUE,
    unit_name TEXT NOT NULL,
    description TEXT,
    daily_rate REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'tersedia'
        CHECK (status IN ('tersedia', 'disewa', 'maintenance'))
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS unit_category (
    unit_id INTEGER NOT NULL REFERENCES units(id),
    category_id INTEGER NOT NULL REFERENCES categories(id),
    PRIMARY KEY (unit_id, category_id)
);

CREATE TABLE IF NOT EXISTS rentals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    admin_id INTEGER REFERENCES users(id),
    rented_at TEXT NOT NULL,
    due_at TEXT NOT NULL,
    returned_at TEXT,
    status TEXT NOT NULL DEFAULT 'aktif'
        CHECK (status IN ('aktif', 'selesai', 'terlambat')),
    fine_amount REAL
);

CREATE TABLE IF NOT EXISTS rental_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rental_id INTEGER NOT NULL REFERENCES rentals(id),
    unit_id INTEGER NOT NULL REFERENCES units(id),
    daily_rate_snapshot REAL NOT NULL
);
"""


def setup_database():
    """Buat tabel, lalu isi data awal kalau database masih kosong."""
    db = connect()
    db.executescript(TABLES)
    total_users = db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if total_users == 0:
        insert_seed_data(db)
    db.close()


def insert_seed_data(db):
    today = date.today()

    def day(offset):
        return (today + timedelta(days=offset)).isoformat()

    db.execute("BEGIN")

    # akun awal: 1 admin dan 3 anggota
    users = [
        ("Ki Narendra Swara", "admin@ruangnada.id", "admin123", "admin", 1),
        ("Kalingga Wardhana", "kalingga@email.com", "anggota123", "anggota", 1),
        ("Arya Sena", "arya@email.com", "anggota123", "anggota", 1),
        ("Mustafa Kamal", "mustafa@email.com", "anggota123", "anggota", 0),
    ]
    for name, email, password, role, is_member in users:
        cursor = db.execute(
            "INSERT INTO users (name, email, password, role, is_member) VALUES (?, ?, ?, ?, ?)",
            (name, email, hash_password(password), role, is_member),
        )
        db.execute("INSERT INTO profiles (user_id, phone, address) VALUES (?, '', '')", (cursor.lastrowid,))

    categories = ["Ritual", "Meditasi", "Tradisional Kuno", "Resonansi Kayu",
                  "Logam Suci", "Tiup Bambu", "Dawai", "Frekuensi Langka"]
    for name in categories:
        db.execute("INSERT INTO categories (category_name) VALUES (?)", (name,))

    # (kode, nama, deskripsi, tarif, status, id kategori)
    units = [
        ("RN-GML-001", "Gamelan Supranatural Sekaten", "Perunggu kuno abad 17, laras pelog.", 1450000, "disewa", [1, 3]),
        ("RN-GML-002", "Gamelan Supranatural Sekaten", "Replika kembar dengan laras slendro.", 1450000, "tersedia", [1, 3]),
        ("RN-TIB-001", "Singing Bowl Tibet 432Hz", "Tujuh paduan logam suci dari Himalaya.", 650000, "tersedia", [2, 1, 5]),
        ("RN-SLG-001", "Suling Bambu Hitam Merapi", "Bambu hitam dari lereng Merapi.", 350000, "tersedia", [6, 2]),
        ("RN-GNG-001", "Gong Ageng Purbakala", "Gong besar peninggalan purbakala.", 1200000, "maintenance", [3, 5]),
        ("RN-KCP-001", "Kecapi Parahyangan Buhun", "Kecapi kayu dengan senar sutra.", 500000, "tersedia", [7, 4]),
        ("RN-REB-001", "Rebab Kencana Mangun", "Rebab berlapis kencana.", 700000, "tersedia", [7, 3]),
        ("RN-KDG-001", "Kendang Kalimosodo", "Kendang kulit sapi dari kayu nangka.", 450000, "disewa", [3, 4]),
    ]
    for code, name, description, rate, status, category_ids in units:
        cursor = db.execute(
            "INSERT INTO units (unit_code, unit_name, description, daily_rate, status) VALUES (?, ?, ?, ?, ?)",
            (code, name, description, rate, status),
        )
        for category_id in category_ids:
            db.execute("INSERT INTO unit_category (unit_id, category_id) VALUES (?, ?)",
                       (cursor.lastrowid, category_id))

    # tiga transaksi contoh: aktif, terlambat, dan sudah selesai
    def add_rental(user_id, rented, due, returned, status, unit_id, rate, admin_id=None):
        cursor = db.execute(
            "INSERT INTO rentals (user_id, admin_id, rented_at, due_at, returned_at, status) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, admin_id, rented, due, returned, status),
        )
        db.execute("INSERT INTO rental_items (rental_id, unit_id, daily_rate_snapshot) VALUES (?, ?, ?)",
                   (cursor.lastrowid, unit_id, rate))

    add_rental(2, day(-2), day(3), None, "aktif", 1, 1450000)
    add_rental(3, day(-9), day(-4), None, "aktif", 8, 450000)
    add_rental(2, day(-20), day(-15), day(-16) + " 10:00", "selesai", 3, 650000, admin_id=1)

    db.execute("COMMIT")
