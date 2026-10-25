# CRUD anggota (hanya admin)
from app.security import hash_password
from app.utils import check, clean_text, is_valid_email


def list_all(req):
    rows = req.db.execute(
        """
        SELECT u.id, u.name, u.email, u.is_member, p.phone, p.address
        FROM users u
        LEFT JOIN profiles p ON p.user_id = u.id
        WHERE u.role = 'anggota'
        ORDER BY u.name
        """
    ).fetchall()

    members = []
    for row in rows:
        member = dict(row)
        member["is_member"] = bool(row["is_member"])
        member["active_units"] = req.db.execute(
            """
            SELECT COUNT(*) FROM rental_items ri
            JOIN rentals r ON r.id = ri.rental_id
            WHERE r.user_id = ? AND r.returned_at IS NULL
            """,
            (row["id"],),
        ).fetchone()[0]
        members.append(member)
    return members


def read_form(req, old_member=None):
    body = req.body
    name = clean_text(body.get("name"))
    email = clean_text(body.get("email"))
    password = body.get("password") or ""

    check(name, "Nama wajib diisi.", "name")
    check(email, "Email wajib diisi.", "email")
    check(is_valid_email(email), "Format email tidak valid.", "email")
    if old_member is None:
        check(password, "Kata sandi wajib diisi.", "password")

    # email harus unik
    same_email = req.db.execute("SELECT id FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
    if same_email is not None:
        is_itself = old_member is not None and same_email["id"] == old_member["id"]
        check(is_itself, "Email sudah digunakan pengguna lain.", "email", 409)

    return {
        "name": name,
        "email": email,
        "password": password,
        "phone": clean_text(body.get("phone")),
        "address": clean_text(body.get("address")),
        "is_member": 1 if body.get("is_member") else 0,
    }


def save_profile(db, user_id, phone, address):
    # satu user hanya boleh punya satu profil (profiles.user_id UNIQUE)
    db.execute(
        """
        INSERT INTO profiles (user_id, phone, address) VALUES (?, ?, ?)
        ON CONFLICT (user_id) DO UPDATE SET phone = excluded.phone, address = excluded.address
        """,
        (user_id, phone, address),
    )


def create(req):
    data = read_form(req)
    req.db.execute("BEGIN")
    cursor = req.db.execute(
        "INSERT INTO users (name, email, password, role, is_member) VALUES (?, ?, ?, 'anggota', ?)",
        (data["name"], data["email"], hash_password(data["password"]), data["is_member"]),
    )
    save_profile(req.db, cursor.lastrowid, data["phone"], data["address"])
    req.db.execute("COMMIT")
    return {"ok": True}


def update(req):
    member_id = req.ids[0]
    old_member = req.db.execute("SELECT * FROM users WHERE id = ? AND role = 'anggota'", (member_id,)).fetchone()
    check(old_member, "Anggota tidak ditemukan.", status=404)

    data = read_form(req, old_member)
    req.db.execute("BEGIN")
    req.db.execute("UPDATE users SET name = ?, email = ?, is_member = ? WHERE id = ?",
                   (data["name"], data["email"], data["is_member"], member_id))
    if data["password"]:   # kata sandi hanya diganti kalau diisi
        req.db.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(data["password"]), member_id))
    save_profile(req.db, member_id, data["phone"], data["address"])
    req.db.execute("COMMIT")
    return {"ok": True}


def delete(req):
    member_id = req.ids[0]
    member = req.db.execute("SELECT id FROM users WHERE id = ? AND role = 'anggota'", (member_id,)).fetchone()
    check(member, "Anggota tidak ditemukan.", status=404)

    total = req.db.execute("SELECT COUNT(*) FROM rentals WHERE user_id = ?", (member_id,)).fetchone()[0]
    check(total == 0,
          "Anggota sudah punya transaksi, jadi belum bisa dihapus "
          "(mekanisme nonaktif belum ditentukan).",
          status=409)

    req.db.execute("BEGIN")
    req.db.execute("DELETE FROM profiles WHERE user_id = ?", (member_id,))
    req.db.execute("DELETE FROM users WHERE id = ?", (member_id,))
    req.db.execute("COMMIT")
    return {"ok": True}


# ---- profil milik sendiri (anggota) ----

def get_my_profile(req):
    return profile_data(req.db, req.user["id"])


def update_my_profile(req):
    name = clean_text(req.body.get("name"))
    check(name, "Nama wajib diisi.", "name")

    req.db.execute("BEGIN")
    req.db.execute("UPDATE users SET name = ? WHERE id = ?", (name, req.user["id"]))
    save_profile(req.db, req.user["id"], clean_text(req.body.get("phone")), clean_text(req.body.get("address")))
    req.db.execute("COMMIT")
    return profile_data(req.db, req.user["id"])


def profile_data(db, user_id):
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    profile = db.execute("SELECT phone, address FROM profiles WHERE user_id = ?", (user_id,)).fetchone()
    return {
        "name": user["name"],
        "email": user["email"],
        "is_member": bool(user["is_member"]),
        "phone": profile["phone"] if profile else "",
        "address": profile["address"] if profile else "",
    }
