# CRUD kategori (hanya admin)
from app.utils import check, clean_text


def list_all(req):
    rows = req.db.execute(
        """
        SELECT c.id, c.category_name AS name,
               (SELECT COUNT(*) FROM unit_category uc WHERE uc.category_id = c.id) AS units
        FROM categories c
        ORDER BY c.category_name
        """
    ).fetchall()
    return [dict(row) for row in rows]


def check_name(req, name, current_id=None):
    """Nama wajib diisi dan tidak boleh sama dengan kategori lain."""
    check(name, "Nama kategori wajib diisi.", "name")
    rows = req.db.execute("SELECT id FROM categories WHERE lower(category_name) = lower(?)", (name,)).fetchall()
    for row in rows:
        check(row["id"] == current_id, "Nama kategori sudah digunakan. Nama kategori harus unik.", "name", 409)


def create(req):
    name = clean_text(req.body.get("name"))
    check_name(req, name)
    req.db.execute("INSERT INTO categories (category_name) VALUES (?)", (name,))
    return {"ok": True}


def update(req):
    category_id = req.ids[0]
    name = clean_text(req.body.get("name"))
    row = req.db.execute("SELECT id FROM categories WHERE id = ?", (category_id,)).fetchone()
    check(row, "Kategori tidak ditemukan.", status=404)
    check_name(req, name, category_id)
    req.db.execute("UPDATE categories SET category_name = ? WHERE id = ?", (name, category_id))
    return {"ok": True}


def delete(req):
    category_id = req.ids[0]
    row = req.db.execute("SELECT id FROM categories WHERE id = ?", (category_id,)).fetchone()
    check(row, "Kategori tidak ditemukan.", status=404)

    # kategori yang masih dipakai unit tidak boleh dihapus
    used = req.db.execute("SELECT COUNT(*) FROM unit_category WHERE category_id = ?", (category_id,)).fetchone()[0]
    check(used == 0,
          "Kategori masih dipakai " + str(used) + " unit, jadi belum bisa dihapus "
          "(mekanisme nonaktif belum ditentukan).",
          status=409)

    req.db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    return {"ok": True}
