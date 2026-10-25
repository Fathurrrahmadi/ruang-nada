# Transaksi sewa: ajukan sewa, daftar sewa, pengembalian, riwayat, dan dashboard
from datetime import date, datetime

from app.utils import ApiError, check, parse_date

MAX_UNITS = 2   # maksimal unit aktif per anggota
MAX_DAYS = 5    # durasi sewa standar maksimal (hari)


def get_rentals(db, where="", params=()):
    """Ambil transaksi beserta nama anggota dan unit-unitnya."""
    rows = db.execute(
        """
        SELECT r.*, u.name AS member_name, u.email AS member_email
        FROM rentals r
        JOIN users u ON u.id = r.user_id
        """ + where + " ORDER BY r.id DESC",
        params,
    ).fetchall()

    today = date.today()
    result = []
    for row in rows:
        items = db.execute(
            """
            SELECT un.id, un.unit_code, un.unit_name, ri.daily_rate_snapshot
            FROM rental_items ri
            JOIN units un ON un.id = ri.unit_id
            WHERE ri.rental_id = ?
            """,
            (row["id"],),
        ).fetchall()

        due = datetime.strptime(row["due_at"], "%Y-%m-%d").date()
        status_display = row["status"]
        days_late = 0
        if row["returned_at"] is None:
            # belum dikembalikan: terlambat kalau hari ini sudah lewat jatuh tempo
            if today > due:
                status_display = "terlambat"
                days_late = (today - due).days
        else:
            returned = datetime.strptime(row["returned_at"][:10], "%Y-%m-%d").date()
            days_late = max(0, (returned - due).days)

        result.append({
            "id": row["id"],
            "code": "TRX-%05d" % row["id"],
            "member_name": row["member_name"],
            "member_email": row["member_email"],
            "rented_at": row["rented_at"],
            "due_at": row["due_at"],
            "returned_at": row["returned_at"],
            "status": row["status"],
            "status_display": status_display,
            "days_late": days_late,
            "fine_amount": row["fine_amount"],
            "units": [dict(item) for item in items],
        })
    return result


def count_active_units(db, user_id):
    row = db.execute(
        """
        SELECT COUNT(*) FROM rental_items ri
        JOIN rentals r ON r.id = ri.rental_id
        WHERE r.user_id = ? AND r.returned_at IS NULL
        """,
        (user_id,),
    ).fetchone()
    return row[0]


# ---- anggota ----

def create(req):
    user = req.user
    body = req.body

    # urutan pengecekan sama seperti di flowchart
    check(user["is_member"],
          "Kamu belum terdaftar sebagai anggota. Hubungi Admin untuk menyelesaikan pendaftaran.",
          status=403, code="not_member")

    check(str(body.get("unit_id", "")).isdigit(), "Unit belum dipilih.", "unit_id")
    unit = req.db.execute("SELECT * FROM units WHERE id = ?", (int(body["unit_id"]),)).fetchone()
    check(unit, "Unit tidak ditemukan.", "unit_id", 404)
    check(unit["status"] != "disewa", "Unit sedang disewa dan tidak bisa dipilih.", "unit_id", 409, "unit_rented")
    check(unit["status"] != "maintenance", "Unit sedang maintenance dan tidak bisa dipilih.", "unit_id", 409, "unit_maintenance")

    active = count_active_units(req.db, user["id"])
    check(active + 1 <= MAX_UNITS,
          "Batas " + str(MAX_UNITS) + " unit aktif sudah tercapai. Kembalikan salah satu unit dulu.",
          status=409, code="limit_reached")

    rented_at = parse_date(body.get("rented_at") or date.today().isoformat(), "rented_at")
    due_at = parse_date(body.get("due_at"), "due_at")
    check(due_at > rented_at, "Tanggal jatuh tempo harus sesudah tanggal sewa.", "due_at")
    check((due_at - rented_at).days <= MAX_DAYS,
          "Durasi sewa standar maksimal " + str(MAX_DAYS) + " hari.", "due_at")

    # simpan dalam satu transaction supaya status unit dan transaksi selalu konsisten
    req.db.execute("BEGIN IMMEDIATE")
    try:
        # update hanya berhasil kalau unit masih 'tersedia' (cek ulang, siapa tahu baru diambil orang lain)
        changed = req.db.execute(
            "UPDATE units SET status = 'disewa' WHERE id = ? AND status = 'tersedia'", (unit["id"],)
        ).rowcount
        if changed != 1:
            raise ApiError(409, "Unit baru saja disewa anggota lain.", "unit_id", "unit_rented")

        cursor = req.db.execute(
            "INSERT INTO rentals (user_id, rented_at, due_at, status) VALUES (?, ?, ?, 'aktif')",
            (user["id"], rented_at.isoformat(), due_at.isoformat()),
        )
        req.db.execute(
            "INSERT INTO rental_items (rental_id, unit_id, daily_rate_snapshot) VALUES (?, ?, ?)",
            (cursor.lastrowid, unit["id"], unit["daily_rate"]),
        )
        req.db.execute("COMMIT")
    except Exception:
        req.db.execute("ROLLBACK")
        raise

    req.status_code = 201
    return {"ok": True, "code": "TRX-%05d" % cursor.lastrowid, "due_at": due_at.isoformat()}


def my_rentals(req):
    # selalu pakai id user yang login, jadi anggota tidak bisa melihat transaksi orang lain
    return get_rentals(req.db, "WHERE r.user_id = ?", (req.user["id"],))


# ---- admin ----

def active_rentals(req):
    rows = get_rentals(req.db, "WHERE r.returned_at IS NULL")
    rows.sort(key=lambda r: r["due_at"])
    return rows


def history(req):
    user_id = req.query.get("user_id", [""])[0]
    if user_id.isdigit():
        return get_rentals(req.db, "WHERE r.user_id = ?", (int(user_id),))
    return get_rentals(req.db)


def return_unit(req):
    rental_id = req.ids[0]

    req.db.execute("BEGIN IMMEDIATE")
    try:
        rental = req.db.execute("SELECT * FROM rentals WHERE id = ?", (rental_id,)).fetchone()
        check(rental, "Transaksi tidak ditemukan.", status=404)
        check(rental["returned_at"] is None, "Transaksi ini sudah dikembalikan.", status=409)

        due = datetime.strptime(rental["due_at"], "%Y-%m-%d").date()
        days_late = max(0, (date.today() - due).days)
        is_late = days_late > 0
        new_status = "terlambat" if is_late else "selesai"

        # nominal denda belum ditentukan di dokumen, jadi fine_amount tidak diisi
        req.db.execute(
            "UPDATE rentals SET returned_at = ?, status = ?, admin_id = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M"), new_status, req.user["id"], rental_id),
        )
        req.db.execute(
            """
            UPDATE units SET status = 'tersedia'
            WHERE status = 'disewa'
              AND id IN (SELECT unit_id FROM rental_items WHERE rental_id = ?)
            """,
            (rental_id,),
        )
        req.db.execute("COMMIT")
    except Exception:
        req.db.execute("ROLLBACK")
        raise

    message = "Pengembalian dicatat."
    if is_late:
        message = ("Pengembalian dicatat. Terlambat " + str(days_late) + " hari, denda dicatat sesuai "
                   "kebijakan yang dikonfirmasi (nominal belum ditetapkan).")
    return {"ok": True, "late": is_late, "days_late": days_late, "message": message}


def dashboard(req):
    db = req.db

    def count(sql):
        return db.execute(sql).fetchone()[0]

    active = active_rentals(req)
    late = [r for r in active if r["status_display"] == "terlambat"]
    return {
        "units": count("SELECT COUNT(*) FROM units"),
        "tersedia": count("SELECT COUNT(*) FROM units WHERE status = 'tersedia'"),
        "disewa": count("SELECT COUNT(*) FROM units WHERE status = 'disewa'"),
        "maintenance": count("SELECT COUNT(*) FROM units WHERE status = 'maintenance'"),
        "members": count("SELECT COUNT(*) FROM users WHERE role = 'anggota' AND is_member = 1"),
        "late": len(late),
        "upcoming": active[:5],
    }
