# Fungsi-fungsi kecil yang dipakai di banyak file
import re
from datetime import datetime


class ApiError(Exception):
    """Error yang akan dikirim ke browser sebagai JSON."""

    def __init__(self, status, message, field=None, code=None):
        super().__init__(message)
        self.status = status
        self.message = message
        self.field = field    # nama input yang salah (kalau ada)
        self.code = code      # kode singkat, misalnya "not_member"


def check(condition, message, field=None, status=400, code=None):
    """Kalau condition False, langsung lempar error."""
    if not condition:
        raise ApiError(status, message, field, code)


def clean_text(value):
    """Hapus spasi di awal/akhir. Kalau bukan teks, jadikan string kosong."""
    if isinstance(value, str):
        return value.strip()
    return ""


def is_valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def parse_date(text, field):
    """Ubah teks 'YYYY-MM-DD' jadi objek date."""
    try:
        return datetime.strptime(clean_text(text), "%Y-%m-%d").date()
    except ValueError:
        raise ApiError(400, "Format tanggal tidak valid.", field)
