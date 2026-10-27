# Server Ruang Nada
# Jalankan dengan:  python3 server.py   lalu buka http://localhost:8000
import json
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

from app import auth, categories, members, rentals, security, units
from app.db import connect, setup_database
from app.utils import ApiError

PORT = int(os.environ.get("PORT", "8000"))
PUBLIC_DIR = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "public"))

# Daftar endpoint API.
# Kolom ketiga menentukan siapa yang boleh akses:
#   "public" = siapa saja, "login" = semua yang sudah login, "admin" / "anggota" = peran tertentu
# <id> di path akan diambil sebagai angka dan masuk ke req.ids
ROUTES = [
    ("POST",   "/api/login",                 "public",  auth.login),
    ("POST",   "/api/register",              "public",  auth.register),
    ("POST",   "/api/logout",                "login",   auth.logout),
    ("GET",    "/api/me",                    "login",   auth.me),

    ("GET",    "/api/dashboard",             "admin",   rentals.dashboard),
    ("GET",    "/api/categories",            "admin",   categories.list_all),
    ("POST",   "/api/categories",            "admin",   categories.create),
    ("PUT",    "/api/categories/<id>",       "admin",   categories.update),
    ("DELETE", "/api/categories/<id>",       "admin",   categories.delete),

    ("GET",    "/api/units",                 "admin",   units.list_all),
    ("POST",   "/api/units",                 "admin",   units.create),
    ("PUT",    "/api/units/<id>",            "admin",   units.update),
    ("DELETE", "/api/units/<id>",            "admin",   units.delete),

    ("GET",    "/api/members",               "admin",   members.list_all),
    ("POST",   "/api/members",               "admin",   members.create),
    ("PUT",    "/api/members/<id>",          "admin",   members.update),
    ("DELETE", "/api/members/<id>",          "admin",   members.delete),

    ("GET",    "/api/rentals/active",        "admin",   rentals.active_rentals),
    ("POST",   "/api/rentals/<id>/return",   "admin",   rentals.return_unit),
    ("GET",    "/api/history",               "admin",   rentals.history),

    ("GET",    "/api/catalog",               "anggota", units.catalog),
    ("GET",    "/api/catalog/<id>",          "anggota", units.detail),
    ("POST",   "/api/rentals",               "anggota", rentals.create),
    ("GET",    "/api/my/rentals",            "anggota", rentals.my_rentals),
    ("GET",    "/api/my/profile",            "anggota", members.get_my_profile),
    ("PUT",    "/api/my/profile",            "anggota", members.update_my_profile),
]

ADMIN_PAGES = ["admin-dashboard.html", "admin-unit.html", "admin-kategori.html",
               "admin-anggota.html", "admin-disewa.html", "admin-riwayat.html"]
MEMBER_PAGES = ["katalog.html", "detail-unit.html", "profil.html", "anggota-sewa.html"]

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


class Request:
    """Data satu permintaan, dikirim ke fungsi handler di folder app/."""

    def __init__(self, db, user, token, body, query, ids):
        self.db = db
        self.user = user
        self.token = token
        self.body = body
        self.query = query
        self.ids = ids
        self.status_code = 200
        self.cookie_to_set = None


def find_route(method, path):
    """Cari route yang cocok. Mengembalikan (role, fungsi, ids) atau None."""
    for route_method, route_path, role, function in ROUTES:
        if route_method != method:
            continue
        pattern = "^" + route_path.replace("<id>", "(\\d+)") + "$"
        match = re.match(pattern, path)
        if match:
            ids = [int(i) for i in match.groups()]
            return role, function, ids
    return None


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_PUT(self):
        self.handle_request("PUT")

    def do_DELETE(self):
        self.handle_request("DELETE")

    def log_message(self, format, *args):
        sys.stderr.write(self.address_string() + " - " + (format % args) + "\n")

    def handle_request(self, method):
        path = urlparse(self.path).path
        db = connect()
        try:
            if path.startswith("/api/"):
                self.handle_api(method, path, db)
            elif method == "GET":
                self.handle_static(path, db)
            else:
                self.send_json(405, {"error": "Metode tidak diizinkan."})
        except Exception as error:
            print("ERROR:", repr(error))
            self.send_json(500, {"error": "Terjadi kesalahan di server."})
        finally:
            db.close()

    # ---------- login / sesi ----------

    def get_token(self):
        cookie = self.headers.get("Cookie", "")
        match = re.search(r"sid=([A-Za-z0-9_\-]+)", cookie)
        return match.group(1) if match else None

    def get_logged_in_user(self, db):
        token = self.get_token()
        user_id = security.get_user_id(token) if token else None
        if user_id is None:
            return None
        return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    # ---------- API ----------

    def handle_api(self, method, path, db):
        route = find_route(method, path)
        if route is None:
            return self.send_json(404, {"error": "Endpoint tidak ditemukan."})
        role, function, ids = route

        user = self.get_logged_in_user(db)
        if role != "public" and user is None:
            return self.send_json(401, {"error": "Silakan login dulu."})
        if role in ("admin", "anggota") and user["role"] != role:
            return self.send_json(403, {"error": "Kamu tidak punya akses ke fungsi ini."})

        req = Request(db, user, self.get_token(), self.read_body(), parse_qs(urlparse(self.path).query), ids)
        try:
            result = function(req)
        except ApiError as error:
            data = {"error": error.message}
            if error.field:
                data["field"] = error.field
            if error.code:
                data["code"] = error.code
            return self.send_json(error.status, data)

        headers = {}
        if req.cookie_to_set:
            headers["Set-Cookie"] = req.cookie_to_set
        self.send_json(req.status_code, result, headers)

    def read_body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}

    def send_json(self, status, data, headers=None):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    # ---------- file statis (html, css, js) ----------

    def handle_static(self, path, db):
        name = "index.html" if path == "/" else path.lstrip("/")
        full_path = os.path.realpath(os.path.join(PUBLIC_DIR, name))

        # file harus ada di dalam folder public dan berekstensi yang diizinkan
        extension = os.path.splitext(full_path)[1]
        if not full_path.startswith(PUBLIC_DIR + os.sep) or extension not in CONTENT_TYPES or not os.path.isfile(full_path):
            return self.send_error(404)

        if name in ADMIN_PAGES or name in MEMBER_PAGES or name == "index.html":
            redirect_to = self.check_page_access(name, db)
            if redirect_to:
                self.send_response(302)
                self.send_header("Location", redirect_to)
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return

        with open(full_path, "rb") as f:
            content = f.read()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES[extension])
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def check_page_access(self, name, db):
        """Kalau halaman tidak boleh dibuka, kembalikan alamat tujuan redirect. Kalau boleh, None."""
        user = self.get_logged_in_user(db)

        if name == "index.html":
            # sudah login? langsung ke halaman utama masing-masing
            if user is None:
                return None
            return "admin-dashboard.html" if user["role"] == "admin" else "katalog.html"

        if user is None:
            return "index.html"                       # belum login -> ke halaman login
        if name in ADMIN_PAGES and user["role"] != "admin":
            return "katalog.html"                     # anggota coba buka halaman admin
        if name in MEMBER_PAGES and user["role"] != "anggota":
            return "admin-dashboard.html"             # admin coba buka halaman anggota
        return None



def main():
    setup_database()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print("Ruang Nada jalan di http://localhost:" + str(PORT))
    print("Admin   : admin@ruangnada.id / admin123")
    print("Anggota : kalingga@email.com / anggota123")
    print("Tekan Ctrl+C untuk berhenti")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer berhenti.")


if __name__ == "__main__":
    main()
