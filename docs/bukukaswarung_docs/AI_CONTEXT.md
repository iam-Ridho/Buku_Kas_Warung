# Memakai AI secukupnya (dan tetap mandiri)

## Prinsip
- Dokumen di folder ini adalah memori proyek Anda. AI hanya membantu potongan kecil.
- Sumber utama belajar: dokumentasi resmi (docs.flutter.dev, drift.simonbinder.eu, riverpod.dev,
  fastapi.tiangolo.com, pub.dev untuk nama dan versi paket). Cek di sana dulu untuk API yang spesifik.
- Jangan percaya kode AI sebelum `flutter analyze` dan `flutter test` lolos. Cek nama paket dan
  versi di pub.dev; jawaban AI bisa usang.

## Header yang ditempel di awal chat baru
```
Proyek: BukuKasWarung (Flutter 3.44.6, Android saja; Drift/SQLite offline-first; Riverpod; go_router).
Backend (tahap 3): FastAPI + PostgreSQL. Bahasa kode: Inggris, UI: Indonesia.
Invarian: uang = int rupiah; kuantitas = milli-unit (1000 = 1); stok = SUM(stock_movements);
transaksi append-only; snapshot harga/modal di sale_items; modal kosong = null; ID = UUID klien.
Pembulatan hanya lewat divRound. Struktur: core/, domain/calculators/ (murni), data/, features/.
Saya mengerjakan sendiri; jelaskan alasan singkat, jangan tulis ulang seluruh file.
```

## Cara bertanya agar jawabannya langsung berguna
1. Tujuan dalam satu kalimat ("repository ini harus ...").
2. Kode relevan saja (satu fungsi/kelas), bukan seluruh proyek.
3. Error lengkap (teks, bukan tangkapan layar) dan perintah yang menghasilkannya.
4. Yang sudah dicoba.
5. Hasil yang diharapkan vs yang terjadi.
6. Bila ingin belajar: minta penjelasan konsep dan satu contoh kecil, lalu tulis sendiri.

Contoh baik: "Drift: query SUM(qty_milli) per product_id hanya untuk deleted_at IS NULL. Ini kode saya
(...), hasilnya map kosong padahal ada baris. Apa yang kurang?"
Contoh kurang baik: "Buatkan seluruh layar Kasir."

## Hemat limit
- Satu pertanyaan fokus per pesan; hindari menempel file besar.
- Selesaikan masalah kecil lewat tes: tulis tes yang gagal, perbaiki sampai hijau.
- Catat jawaban yang berguna ke `docs/` (catatan keputusan), jangan mengandalkan riwayat chat.

## Kapan tidak perlu AI
Sintaks Dart/Flutter dasar, widget umum (cek api.flutter.dev), konfigurasi Gradle standar,
perintah git, dan error yang jelas di dokumentasi paket.
