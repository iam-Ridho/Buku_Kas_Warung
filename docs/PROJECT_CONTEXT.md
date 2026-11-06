# BukuKasWarung: konteks proyek (handoff)

Terakhir diperbarui: 1 November 2026. Simpan file ini di root repo dan perbarui setiap selesai satu tahap.

## 1. Apa ini

Aplikasi Android untuk pembukuan warung: catat penjualan, pembelian stok, dan pengeluaran; laba kotor dihitung otomatis; produk yang menipis ditandai. Offline-first (data di HP). Tugas akhir semester, tenggat **pertengahan Desember 2026** (tanggal pasti belum diketahui).

- OFF Prices (Open Food Facts) **tidak wajib**, tapi dianjurkan: dipakai untuk mengisi nama dan harga referensi dari barcode.
- Backend FastAPI adalah **tujuan belajar** (auth + sync), bukan syarat dosen.
- Play Store (akun kampus) **ditunda dulu**.

## 2. Keputusan

**Disepakati (ditetapkan Ridho):**
- Kuantitas pecahan (milli-unit); modal = harga beli terakhir.
- Stok kurang saat jual = peringatan + konfirmasi (default); opsi "blokir stok" di pengaturan.
- Di luar versi 1: kasbon, multi-perangkat, harga bertingkat, diskon, QRIS.
- Kasir: uang diterima + kembalian (P1, tidak disimpan). Stok awal lewat koreksi stok di form produk.
- Laporan cukup total (tanpa rincian per produk).
- Hosting backend: layanan gratis. Penamaan kode Inggris, antarmuka Indonesia. Satu repo: `app/` dan `backend/`.
- Dokumen tidak dinilai; dipakai sebagai bahan belajar.

**Usulan (belum dikonfirmasi eksplisit):**
- Flutter + Drift (SQLite) offline-first; Riverpod; go_router.
- OFF dipanggil langsung dari aplikasi (backend gratis bisa tidur, cold start 30-60 dtk).
- Render (FastAPI) + Neon (Postgres) sebagai kandidat hosting.
- Transaksi append-only, ID UUID dari klien, mekanisme `epoch` pada sync.

## 3. Aturan yang tidak boleh dilanggar

1. Uang = integer rupiah. Tidak ada float.
2. Kuantitas = integer milli-unit (1000 = 1 unit dasar).
3. Semua pembulatan lewat `divRound` (`lib/core/money.dart`), setengah dibulatkan menjauhi nol.
4. Stok = jumlah `stock_movements.qty_milli`. Tidak ada kolom stok yang diedit.
5. Penjualan menyimpan snapshot (nama, harga jual, modal). Mengubah harga tidak mengubah riwayat.
6. Koreksi dan pembatalan = menambah catatan. Transaksi tidak diedit atau dihapus.
7. Modal kosong = `null`, bukan 0. Laba kotor tidak menghitung baris tanpa modal.
8. Setiap tulis ke tabel sinkron harus mengisi `dirty = true` dan `updatedAt` lewat satu helper.
9. `recordSale` = satu transaksi database. ID penjualan dibuat saat keranjang dibuka (tap ganda aman).
10. Jalur transaksi tidak pernah menunggu jaringan.
11. Hapus = soft delete (`deletedAt`).
12. Harga OFF hanya saran; tidak menimpa input pemilik, dan kegagalan OFF tidak memblokir apa pun.
13. Laporan: jika ada baris tanpa modal, "omzet - modal" tidak sama dengan laba kotor. Tampilkan `revenueWithoutCost` agar angkanya bisa direkonsiliasi.

## 4. Struktur proyek

```
bukukaswarung/
  app/                      Flutter (project name: bukukaswarung)
    lib/
      core/                 money.dart, quantity.dart   (clock/id menyusul)
      domain/calculators/   line_calculator, gross_profit, stock_calculator, business_date
      data/                 local (Drift), remote (OFF client), repositories
      features/             pos, products, stock, reports, settings
      app/                  router, theme, root providers
    test/
  backend/                  FastAPI (tahap 3)
  docs/                     PRD, UML, ERD, wireframe, tables.dart, sync_contract.py
  PROJECT_CONTEXT.md
```

## 5. Artefak desain (salin ke `docs/`)

- PRD (v0.2): dokumen di Claude; ekspor ke Markdown/PDF/Word lalu simpan di `docs/`.
- UML: `01_use_case`, `02_arsitektur`, `03_erd` (lokal), `04_seq_penjualan`, `05_seq_scan_produk_off`, `06_seq_sync`, `07_activity_kasir`, `08_erd_server_postgres` (PNG + sumber `.puml`).
- `tables.dart`: skema Drift (sumber kebenaran skema lokal).
- `sync_contract.py`: kontrak sync FastAPI + Pydantic (belum diimplementasikan).
- Wireframe (kanvas desain, 5 layar: Kasir, Bayar, Form Produk, Stok, Laporan): https://claude.ai/artifact/PfhTiKbN17oN7YpbLHoRfZ

## 6. Status

- [x] Desain: PRD, UML, ERD, wireframe, kontrak sync
- [x] Setup proyek Flutter (Android saja), perangkat terdeteksi
- [x] `core/` dan `domain/calculators/` + tes (47 tes lulus di Dart VM sandbox)
- [ ] Konfirmasi `flutter test` hijau di laptop, lalu commit
- [ ] Skema Drift + tes migrasi
- [ ] Repository + layar UI
- [ ] OFF client
- [ ] Backend FastAPI (auth + sync)

## 7. Langkah berikutnya (urut)

1. `flutter test` hijau di laptop; commit.
2. Database Drift dari `tables.dart`: indeks parsial barcode unik, `schemaVersion`, `drift_dev schema dump`, tes migrasi (`SchemaVerifier`).
3. Helper `upsert` (dirty/updatedAt), `IdGenerator`, `Clock`.
4. Repository: produk, penjualan (`recordSale` atomik + peringatan stok), stok (movement, pembelian, koreksi, stok awal), pengeluaran. Uji dengan Drift in-memory.
5. UI sesuai wireframe: Kasir -> Bayar -> Produk/Form -> Stok -> Laporan.
6. Notifikasi stok menipis (`crossedLowThreshold`), ekspor/impor backup.
7. OFF client + cache lokal.
8. Backend FastAPI: auth, lalu `push` dan `pull` sesuai `sync_contract.py`.

Aturan potong jika waktu habis: backend dulu, lalu OFF. Aplikasi lokal yang lengkap adalah batas minimum.

## 8. Perintah yang sering dipakai (dari folder `app/`)

```
flutter test
flutter analyze
flutter run
dart run build_runner build --delete-conflicting-outputs
```

## 9. Sumber belajar resmi

- Flutter: https://docs.flutter.dev
- Drift: https://drift.simonbinder.eu
- Riverpod: https://riverpod.dev
- FastAPI: https://fastapi.tiangolo.com
- Open Food Facts / Open Prices: https://openfoodfacts.github.io/openfoodfacts-documentation

## 10. Yang belum pasti (verifikasi sebelum dipakai)

- Nama dan versi paket `flutter pub add` (berdasarkan pengetahuan sampai pertengahan 2026). Biarkan `flutter pub add` memilih versi; commit `pubspec.lock`.
- Syarat free tier hosting (Render, Neon, dan lainnya) sering berubah.
- Aturan Play Store untuk akun organisasi, closed testing, dan penghapusan akun.
- Cakupan data OFF untuk produk Indonesia dan kebutuhan User-Agent.
- Tanggal pasti tenggat, dan cara dosen memeriksa hasil (rilis produksi atau jalur testing).
- `applicationId` saat ini `id.ridho.bukukaswarung`; permanen setelah rilis.

## 11. Memulai sesi baru dengan AI (template)

> Saya melanjutkan proyek BukuKasWarung. Baca `PROJECT_CONTEXT.md` terlampir dan patuhi aturan di bagian 3. Status: <salin bagian 6 yang terbaru>. Tugas sesi ini: <satu tugas kecil>. File relevan: <tempel hanya file yang menyangkut tugas>. Jika ragu soal keputusan desain, tanyakan dulu, jangan menebak.

Tips hemat: kirim satu tugas kecil per sesi, tempel hanya file dan pesan error yang relevan, dan minta perubahan dalam bentuk potongan kode, bukan menulis ulang seluruh file.
