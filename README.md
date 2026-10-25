# Ruang Nada - Sistem Rental Alat Musik Mistis

Aplikasi web untuk mengelola penyewaan alat musik mistis. Ada dua peran: **Admin** dan **Anggota**.

## Identitas

- **Nama kelompok:** Kelompok Ruang Nada
- **Nama proyek:** Sistem Rental Alat Musik Mistis
- **Anggota tim:**
  
  |------|-----|
  | Fathur Rizki Rahmadi | 102022580007 |
  | Alvaritzy Maulidan Risnandar | 102022300308 |
  | isha alviandi | 102022300367 | 

## Daftar fitur

**Umum**
- Login dengan pembagian akses Admin dan Anggota
- Halaman internal tidak bisa dibuka tanpa login
- Kata sandi disimpan dalam bentuk hash

**Admin**
- Tambah, ubah, hapus data unit (kode unit unik, nama unit boleh sama, satu unit bisa punya beberapa kategori)
- Tambah, ubah, hapus kategori (nama kategori unik)
- Tambah, ubah, hapus anggota (email unik, satu profil per pengguna)
- Melihat daftar unit yang sedang disewa
- Memproses pengembalian unit (hanya Admin), termasuk penandaan keterlambatan
- Melihat dan mencetak riwayat peminjaman, bisa disaring per anggota

**Anggota**
- Melihat dan mengubah profil sendiri
- Mencari unit berdasarkan nama dan melihat detail unit
- Mengajukan penyewaan (hanya anggota terdaftar, maksimal 2 unit aktif, durasi standar maksimal 5 hari)
- Melihat daftar unit yang sedang dan pernah disewa (hanya miliknya sendiri)

**Aturan yang dijalankan sistem**
- Unit yang sedang disewa atau maintenance tidak bisa dipilih
- Penyewaan dan pembaruan status unit disimpan dalam satu database transaction untuk mencegah sewa ganda
- Tarif saat transaksi disimpan di `rental_items.daily_rate_snapshot`
- Data yang sudah dipakai transaksi tidak bisa dihapus (mekanisme nonaktif belum ditentukan)
- Nominal denda belum dihitung karena kebijakannya belum ditetapkan

## Skema database

![Skema database]

## Demo

Rekaman demo: 

## Cara menjalankan

1. Pastikan Python 3 terpasang (`python3 --version`).
2. Buka folder proyek di terminal, lalu jalankan:
   ```
   python3 server.py
   ```
3. Buka http://localhost:8000 di browser.
4. Berhenti dengan `Ctrl + C`.

Kalau port 8000 sedang dipakai: `PORT=8080 python3 server.py`

Database `ruangnada.db` dibuat otomatis saat pertama kali dijalankan, lengkap dengan data awal
(akun admin, kategori, dan unit). Tailwind CSS dimuat dari CDN, jadi perlu koneksi internet.

## Akun awal

| Peran | Email | Kata sandi |
|-------|-------|------------|
| Admin | admin@ruangnada.id | admin123 |
| Anggota | kalingga@email.com | anggota123 |
| Anggota | arya@email.com | anggota123 |
| Bukan anggota terdaftar | mustafa@email.com | anggota123 |

Akun ini hanya untuk demo.

## Teknologi

- Backend: Python 3 (`http.server`, `sqlite3`), tanpa library tambahan
- Database: SQLite
- Frontend: HTML, Tailwind CSS (CDN), JavaScript


