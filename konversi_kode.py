
#   python3 konversi_kode.py             -> hanya simulasi, database tidak berubah
#   python3 konversi_kode.py --terapkan  -> mengubah database (backup dibuat otomatis)
import shutil
import sys
import traceback
from datetime import datetime

from app import db as database
from app.units import fathur

terapkan = "--terapkan" in sys.argv
db = database.connect()

units = db.execute("SELECT id, unit_code, unit_name FROM units ORDER BY id").fetchall()

if terapkan:
    cadangan = database.DB_PATH + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy(database.DB_PATH, cadangan)
    print("Backup dibuat:", cadangan)

db.execute("BEGIN IMMEDIATE")
try:
    # tahap 1: kode lama diganti sementara supaya tidak bentrok
    db.execute("UPDATE units SET unit_code = 'TMP-' || id")

    # tahap 2: buat kode baru untuk tiap unit
    for u in units:
        kode_baru = fathur(db, u["unit_name"])
        db.execute("UPDATE units SET unit_code = ? WHERE id = ?", (kode_baru, u["id"]))
        print(u["unit_code"], "->", kode_baru, "  ", u["unit_name"])

    if terapkan:
        db.execute("COMMIT")
        print("Selesai. Kode unit sudah diubah.")
    else:
        db.execute("ROLLBACK")
        print("Hanya simulasi, belum ada yang diubah. Tambahkan --terapkan untuk menyimpan.")
except Exception:
    db.execute("ROLLBACK")
    traceback.print_exc()
    print("Gagal, semua perubahan dibatalkan.")
