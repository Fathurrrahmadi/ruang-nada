# CRUD unit (admin) dan katalog unit (anggota)
import re
from app.utils import ApiError, check, clean_text


def unit_with_categories(db, row):
    """Ubah satu baris unit jadi dict, lalu tambahkan daftar kategorinya."""
    categories = db.execute(
        """
        SELECT c.id, c.category_name AS name
        FROM categories c
        JOIN unit_category uc ON uc.category_id = c.id
        WHERE uc.unit_id = ?
        ORDER BY c.category_name
        """,
        (row["id"],),
    ).fetchall()
    unit = dict(row)
    unit["categories"] = [dict(c) for c in categories]
    return unit


def list_all(req):
    rows = req.db.execute("SELECT * FROM units ORDER BY unit_code").fetchall()
    return [unit_with_categories(req.db, row) for row in rows]


def read_form(req, old_unit=None):
   
    body = req.body

    name = clean_text(body.get("unit_name"))
    status = clean_text(body.get("status")) or "tersedia"
    # check(code, "Kode unit wajib diisi.", "unit_code")
    check(name, "Nama unit wajib diisi.", "unit_name")

    try:
        rate = float(body.get("daily_rate"))
    except (TypeError, ValueError):
        check(False, "Tarif harian harus berupa angka.", "daily_rate")
    check(rate >= 0, "Tarif harian tidak boleh negatif.", "daily_rate")

    check(status in ("tersedia", "maintenance", "disewa"), "Status unit tidak valid.", "status")
    if old_unit is None:
        check(status != "disewa", "Status 'disewa' diatur otomatis oleh transaksi.", "status")
    elif status != old_unit["status"]:
        check(old_unit["status"] != "disewa", "Unit sedang disewa, statusnya tidak bisa diubah manual.", "status", 409)
        check(status != "disewa", "Status 'disewa' diatur otomatis oleh transaksi.", "status")

    # kode unit tidak boleh sama dengan unit lain (nama unit boleh sama)
    #same_code = req.db.execute("SELECT id FROM units WHERE unit_code = ?", (code,)).fetchone()
    #if same_code is not None:
     #   is_itself = old_unit is not None and same_code["id"] == old_unit["id"]
      #  check(is_itself, "Kode unit '" + code + "' sudah digunakan unit lain.", "unit_code", 409)

    category_ids = body.get("category_ids") or []
    for category_id in category_ids:
        found = req.db.execute("SELECT id FROM categories WHERE id = ?", (category_id,)).fetchone()
        check(found, "Kategori tidak ditemukan.", "category_ids")

    return {
        
        "name": name,
        "description": clean_text(body.get("description")),
        "rate": rate,
        "status": status,
        "category_ids": set(category_ids),
    }


def save_categories(db, unit_id, category_ids):
    db.execute("DELETE FROM unit_category WHERE unit_id = ?", (unit_id,))
    for category_id in category_ids:
        db.execute("INSERT INTO unit_category (unit_id, category_id) VALUES (?, ?)", (unit_id, category_id))

def create(req):
    data = read_form(req)
    req.db.execute("BEGIN IMMEDIATE")
    try:
        kode = fathur(req.db, data["name"])
        cursor = req.db.execute(
            "INSERT INTO units (unit_code, unit_name, description, daily_rate, status) VALUES (?, ?, ?, ?, ?)",
            (kode, data["name"], data["description"], data["rate"], data["status"]),
        )
        save_categories(req.db, cursor.lastrowid, data["category_ids"])
        req.db.execute("COMMIT")
    except Exception:
        req.db.execute("ROLLBACK")
        raise
    return {"ok": True, "code": kode}


def update(req):
    unit_id = req.ids[0]
    old_unit = req.db.execute("SELECT * FROM units WHERE id = ?", (unit_id,)).fetchone()
    check(old_unit, "Unit tidak ditemukan.", status=404)

    data = read_form(req, old_unit)
    req.db.execute("BEGIN IMMEDIATE")
    try:
        req.db.execute(
            "UPDATE units SET unit_name = ?, description = ?, daily_rate = ?, status = ? WHERE id = ?",
            (data["name"], data["description"], data["rate"], data["status"], unit_id),
        )
        save_categories(req.db, unit_id, data["category_ids"])
        req.db.execute("COMMIT")
    except Exception:
        req.db.execute("ROLLBACK")
        raise
    return {"ok": True}

def delete(req):
    unit_id = req.ids[0]
    unit = req.db.execute("SELECT id FROM units WHERE id = ?", (unit_id,)).fetchone()
    check(unit, "Unit tidak ditemukan.", status=404)

    # unit yang sudah pernah disewa tidak dihapus supaya riwayat tetap utuh
    used = req.db.execute("SELECT COUNT(*) FROM rental_items WHERE unit_id = ?", (unit_id,)).fetchone()[0]
    check(used == 0,
          "Unit sudah punya riwayat transaksi, jadi belum bisa dihapus "
          "(mekanisme nonaktif belum ditentukan).",
          status=409)

    req.db.execute("BEGIN")
    req.db.execute("DELETE FROM unit_category WHERE unit_id = ?", (unit_id,))
    req.db.execute("DELETE FROM units WHERE id = ?", (unit_id,))
    req.db.execute("COMMIT")
    return {"ok": True}


# ---- bagian untuk anggota ----

def catalog(req):
    """Daftar unit untuk anggota. Bisa dicari berdasarkan nama (?q=...)."""
    keyword = clean_text(req.query.get("q", [""])[0])
    rows = req.db.execute(
        "SELECT * FROM units WHERE unit_name LIKE ? ORDER BY unit_name, unit_code",
        ("%" + keyword + "%",),
    ).fetchall()
    return [unit_with_categories(req.db, row) for row in rows]


def detail(req):
    row = req.db.execute("SELECT * FROM units WHERE id = ?", (req.ids[0],)).fetchone()
    check(row, "Unit tidak ditemukan.", status=404)
    return unit_with_categories(req.db, row)

KATA_SAMBUNG = ("dan","di","ke","dari","yang","untuk","dengan")

def ambil_kata(nama):
    kata = []
    for k in nama.split():
        if k[0].isalpha() and k.lower() not in KATA_SAMBUNG:
            kata.append(k)
    return kata

#def dipakai_nama_lain(db, awalan, nama):
 #   ada = db.execute(
  #      "SELECT 1 FROM units WHERE unit_code LIKE ? AND  lower(unit_name) <> lower(?) LIMIT 1",
   #     ("RN-" + awalan + "-%", nama),
    #).fetchone()
    #return ada is not None

#def buat_awalan(db, nama):
    kata = ambil_kata(nama)
    inisial = "".join(k[0] for k in kata).upper()        
    akhir = re.sub(r"[^A-Za-z]", "", kata[-1] if kata else "").upper()

    dasar = (inisial + akhir[-2:]).ljust(3, "X")
    if not dipakai_nama_lain(db, dasar, nama):
        return dasar

    for jumlah in range(3, len(akhir) + 1):
        calon = inisial + akhir[-jumlah:]
        if not dipakai_nama_lain(db, calon, nama):
            return calon

    for i in range(2, 1000):                               
        calon = dasar + str(i)
        if not dipakai_nama_lain(db, calon, nama):
            return calon

    check(False, "Gagal membuat kode unik untuk nama ini.", "unit_name", 409)



def buat_awalan(db, nama):
    kata = ambil_kata(nama)
    inisial = "".join(k[0] for k in kata).upper()[:3]
    akhir = re.sub(r"[^A-Za-z]", "", kata[-1] if kata else "").upper()
    return (inisial + akhir[-2:]).ljust(3, "X")[:5]

def nomor_berikutnya(db, awalan):
    kepala = "RN-" + awalan + "-"
    baris = db.execute(
        "SELECT MAX(CAST(SUBSTR(unit_code, ? )AS INTEGER)) FROM units WHERE unit_code LIKE ?",
        (len(kepala) + 1, kepala + "%")
    ).fetchone()
    return (baris[0] or 0) + 1

def fathur(db, nama_unit):
    nama = " ".join(clean_text(nama_unit).split())
    check(nama, "Nama Unit Wajib Diisi.", "unit_name")
    awalan = buat_awalan(db, nama)
    return "RN-" + awalan + "-" + str(nomor_berikutnya(db, awalan)).zfill(3)

        