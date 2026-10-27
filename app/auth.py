# Login, logout, dan cek siapa yang sedang login
from app import security
from app.utils import check, clean_text, is_valid_email, ApiError


def login(req):
    email = clean_text(req.body.get("email"))
    password = req.body.get("password") or ""

    check(email, "Email wajib diisi.", "email")
    check(is_valid_email(email), "Format email tidak valid.", "email")
    check(password, "Kata sandi wajib diisi.", "password")

    user = req.db.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
    if user is None or not security.check_password(password, user["password"]):
        raise ApiError(401, "Email atau kata sandi salah.")

    token = security.create_session(user["id"])
    if user["role"] == "admin":
        home = "admin-dashboard.html"
    else:
        home = "katalog.html"

    req.cookie_to_set = "sid=" + token + "; Path=/; HttpOnly; SameSite=Lax"
    return {"role": user["role"], "name": user["name"], "home": home}

def register(req):
    name = clean_text(req.body.get("name"))
    email = clean_text(req.body.get("email"))
    password = req.body.get("password") or ""

    check(name, "Nama wajib diisi.", "name")
    check(email, "Email wajib diisi.", "email")
    check(is_valid_email(email), "Format email tidak valid.", "email")
    check(len(password) >= 6, "Kata sandi minimal 6 karakter.", "password")

    same_email = req.db.execute(
        "SELECT id FROM users WHERE lower(email) = lower(?)", (email,)
    ).fetchone()
    check(same_email is None, "Email sudah terdaftar.", "email", 409)

    req.db.execute(
        "INSERT INTO users (name, email, password, role, is_member) VALUES (?, ?, ?, ?, ?)",
        (name, email, security.hash_password(password), "anggota", 1),
    )
    return login(req)


def logout(req):
    security.delete_session(req.token)
    req.cookie_to_set = "sid=; Path=/; Max-Age=0"
    return {"ok": True}


def me(req):
    user = req.user
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
        "is_member": bool(user["is_member"]),
    }
