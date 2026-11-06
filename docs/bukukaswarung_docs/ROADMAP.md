# BukuKasWarung — Roadmap dan daftar tugas

Tenggat: pertengahan Desember 2026. Aturan potong bila terlambat: tahap 3 dulu, lalu tahap 2.
Play Store ditunda (lihat bagian akhir). Kerjakan berurutan, satu tugas satu commit kecil.

## Aturan kerja
- Logika dulu pakai tes (`flutter test`), baru UI. Jalankan `flutter analyze` sebelum commit.
- Satu tugas = satu cabang/commit. Pesan commit: apa yang berubah dan kenapa.
- Mengubah invarian di `ARCHITECTURE.md` = keputusan sadar: ubah dokumennya sekalian.
- Mentok > 30 menit: kecilkan masalahnya jadi contoh minimal sebelum bertanya ke siapa pun.

## Tahap 0 — Fondasi
- [x] `flutter doctor` bersih untuk Android; HP terdeteksi.
- [x] `core/` dan `domain/calculators/` beserta tes (47 tes).
- [ ] `flutter create`, `flutter pub add ...`, commit pertama, `pubspec.lock` ikut di-commit.
- [ ] `flutter test` hijau di laptop Anda.

## Tahap 1 — Aplikasi lokal (target: akhir November)
Selesai jika: semua item bercentang DAN `flutter test` hijau.
- [ ] 1.1 Drift: `database.dart` dari `reference/tables.dart`, indeks parsial, `schemaVersion = 1`, schema dump + tes migrasi.
- [ ] 1.2 Helper: `Clock`, `IdGenerator` (UUID), helper upsert (set `updatedAt` dan `dirty`) + tes.
- [ ] 1.3 `ProductRepository`: tambah/ubah/soft delete, barcode unik hanya untuk produk aktif + tes.
- [ ] 1.4 `StockRepository`: stok per produk, pembelian (perbarui modal), koreksi stok, stok awal + tes.
- [ ] 1.5 `SaleRepository.recordSale`: atomik (uji gagal paksa), snapshot, ID ganda diabaikan, stok negatif boleh + tes.
- [ ] 1.6 Void penjualan: `voidedAt` + movement pembalik, tidak bisa dua kali + tes.
- [ ] 1.7 Query laporan hari/minggu/bulan via `businessDate` + `computeGrossProfit` + tes (termasuk baris tanpa modal).
- [ ] 1.8 UI: kerangka navigasi + layar Kasir (keranjang, peringatan stok).
- [ ] 1.9 UI: Bayar (uang diterima, kembalian).
- [ ] 1.10 UI: Produk (daftar, form, stok awal).
- [ ] 1.11 UI: Stok (habis/menipis, Beli, Koreksi).
- [ ] 1.12 UI: Laporan (total + rekonsiliasi baris tanpa modal), Pengeluaran, Riwayat + batalkan.
- [ ] 1.13 Notifikasi stok menipis (`crossedLowThreshold`) + penanganan izin ditolak.
- [ ] 1.14 Ekspor/impor backup (JSON) tanpa duplikasi.
- [ ] 1.15 Pengaturan (blokir stok, halaman Tentang + atribusi OFF).
- [ ] 1.16 Uji manual di HP: mode pesawat, 2.000 produk, tap ganda, matikan paksa saat transaksi.

## Tahap 2 — OFF Prices (pelengkap)
- [ ] 2.1 Uji ~20 barcode produk warung di OFF; catat hasilnya.
- [ ] 2.2 `OffClient` (timeout pendek, cek IDR, cache `product_references`) + tes dengan klien palsu.
- [ ] 2.3 Scan barcode di form produk: prefill, label "estimasi", fallback manual. Atribusi ODbL.

## Tahap 3 — Backend FastAPI (tujuan belajar)
- [ ] 3.1 Proyek `backend/`: struktur, Pydantic settings, Docker, koneksi Postgres.
- [ ] 3.2 Model/tabel dari `diagrams/08_erd_server_postgres.png`; migrasi (Alembic).
- [ ] 3.3 Auth: register/login/refresh (hash argon2/bcrypt), isolasi `owner_id`.
- [ ] 3.4 `push` dan `pull` sesuai `reference/sync_contract.py` + tes (retry, stale, epoch, rejected).
- [ ] 3.5 Klien sync di Flutter: loop push/pull, timeout 60-90 dtk, tahan server tidur.
- [ ] 3.6 Deploy ke hosting gratis; verifikasi syarat free tier saat itu.

## Play Store (ditunda)
- [ ] Cek status akun Play Console kampus dan mekanisme akses.
- [ ] Tentukan `applicationId` (permanen), privacy policy, Data Safety, signing key (Play App Signing).
