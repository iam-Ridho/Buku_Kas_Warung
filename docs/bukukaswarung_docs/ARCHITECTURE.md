# BukuKasWarung — Arsitektur (ringkas)

Dokumen ini adalah acuan saat Anda bekerja sendiri. Kalau kode dan dokumen berbeda,
putuskan mana yang benar, lalu perbarui yang lain.

## Ringkasan
Aplikasi Android pembukuan warung: catat penjualan, pembelian stok, dan pengeluaran;
laba kotor dihitung otomatis; stok menipis ditandai. **Offline-first**: SQLite (Drift)
di HP adalah sumber kebenaran. Backend FastAPI + PostgreSQL (tahap 3) hanya untuk akun
dan sinkronisasi/backup. OFF Prices (Open Food Facts) dipanggil langsung dari aplikasi
sebagai pelengkap (bukan dependensi inti).

## Invarian (jangan dilanggar tanpa sengaja)
1. Uang = integer rupiah. Kuantitas = integer milli-unit (1000 = 1 unit).
2. Semua pembulatan lewat `divRound` (`core/money.dart`). Jangan membulatkan di tempat lain.
3. Stok tidak pernah disimpan sebagai angka. Stok = SUM(`stock_movements.qty_milli`).
4. Transaksi append-only: koreksi/pembatalan = catatan baru. Hapus = soft delete (`deleted_at`).
5. Penjualan menyimpan snapshot harga jual dan modal. Mengubah harga/modal tidak mengubah riwayat.
6. Modal kosong = `null`, bukan 0. Laporan memisahkan baris tanpa modal.
7. Jalur transaksi tidak menunggu jaringan. Tulis lokal dulu, sync belakangan.
8. ID = UUID dari klien, dibuat saat keranjang dibuka (tap ganda tidak membuat penjualan ganda).
9. Penulisan multi-tabel (sales + sale_items + stock_movements) dalam SATU `db.transaction`.
10. Setiap perubahan tabel sinkron harus mengisi `updatedAt` dan `dirty = true`, lewat satu helper.
11. `businessDate` dihitung saat transaksi dibuat (zona waktu perangkat) lalu disimpan.
12. Stok kurang saat menjual = peringatan + konfirmasi (default). Opsi "blokir stok" di Pengaturan.

## Struktur folder `app/lib/`
```
core/          money.dart, quantity.dart (+ clock.dart, id_generator.dart nanti)
domain/
  calculators/ fungsi murni: line_calculator, gross_profit, stock_calculator, business_date
  models/      entitas Dart biasa (nanti)
data/
  local/       database.dart, tables.dart, daos/
  remote/      off_client.dart (tahap 2), sync_api.dart (tahap 3)
  repositories/ product_, stock_, sale_, expense_repository.dart
features/      pos/ products/ stock/ reports/ settings/  (screens, widgets, notifiers Riverpod)
app/           router (go_router), theme, root providers
```
Aturan: `domain/` tidak mengimpor Flutter atau Drift. `features/` tidak memakai DAO langsung.
Transaksi multi-tabel hidup di repository. Interface abstrak hanya untuk yang berubah antar
lingkungan (klien OFF, Clock, IdGenerator); sisanya uji dengan Drift in-memory.

## Rumus
- Pendapatan baris = divRound(qtyMilli x hargaJual, 1000). Total transaksi = jumlah pendapatan baris.
- Modal baris = divRound(qtyMilli x costPrice, 1000), saat transaksi (snapshot); null jika modal kosong.
- Laba kotor = jumlah (pendapatan - modal) untuk baris yang modalnya ada, dari penjualan tidak batal.
  Omzet semua baris = omzet dengan modal + omzet tanpa modal (tampilkan selisihnya di Laporan).
- Status stok: habis jika stok <= 0; menipis jika 0 < stok <= minimum; selain itu aman.
- Notifikasi stok: sekali saat stok melewati batas (sebelumnya > minimum, sekarang <= minimum).
- Modal produk = harga beli terakhir = total biaya pembelian / jumlah.
- Kembalian = uang diterima - total (hanya tampilan, tidak disimpan).

## Keputusan (alasan singkat)
Disepakati: FastAPI (tujuan belajar backend); hosting gratis; stok negatif boleh (peringatan);
kuantitas pecahan; modal = harga beli terakhir; kasbon/multi-perangkat/harga bertingkat/diskon/QRIS
di luar v1; kembalian dan stok awal masuk; laporan cukup total; OFF tidak wajib tapi dianjurkan.
Usulan (belum dikonfirmasi eksplisit): Flutter + Drift offline-first; OFF dipanggil dari klien
(backend gratis bisa tidur 30-60 dtk); Render + Neon sebagai kandidat hosting.

## Sinkronisasi (tahap 3) — inti
- Push `POST /v1/sync/push` (maks 200 baris), pull `GET /v1/sync/pull?cursor=`; push dulu baru pull.
- Hasil per baris: applied / unchanged / stale / rejected. Retry idempoten (cek "isi identik" dulu).
- Tabel append-only: hanya `deleted_at`/`voided_at` null -> terisi yang boleh berubah.
  Produk: `base_seq` usang -> stale (versi server menang).
- `server_seq` dari counter per owner dengan row lock (bukan sequence global).
- `epoch` berubah (server direset) -> klien reset kursor dan unggah ulang semua baris.
- Server tanpa FK antar tabel sinkron dan tanpa UNIQUE barcode (hindari baris yang ditolak terus).
- Detail: `reference/sync_contract.py`, `diagrams/06_seq_sync.png`, `diagrams/08_erd_server_postgres.png`.

## Peta dokumen
- `diagrams/`: use case, arsitektur, ERD lokal, sequence penjualan/scan+OFF/sync, activity kasir, ERD server (PNG + sumber PlantUML).
- `reference/tables.dart`: skema Drift. `reference/sync_contract.py`: kontrak sync.
- PRD (Claude Doc): https://claude.ai/artifact/5HrGzVZ1BA98mr2o5TJ9US
- Wireframe: https://claude.ai/artifact/PfhTiKbN17oN7YpbLHoRfZ
