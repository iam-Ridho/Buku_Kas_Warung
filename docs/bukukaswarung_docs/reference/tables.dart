// tables.dart — skema lokal BukuKasWarung (Drift / SQLite)
// Aturan: uang = integer rupiah; kuantitas = integer "milli-unit" (1000 = 1 unit dasar).
// Belum dikompilasi: sesuaikan sintaks dengan versi Drift yang dipakai.
import 'package:drift/drift.dart';

enum MovementType { purchase, sale, adjustment, voidReversal }

/// Kolom bersama semua tabel yang disinkronkan.
mixin SyncColumns on Table {
  TextColumn get id => text()(); // UUID dari klien (disarankan v7)
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get updatedAt => dateTime()(); // jam klien, hanya informasi
  DateTimeColumn get deletedAt => dateTime().nullable()(); // soft delete
  BoolColumn get dirty => boolean().withDefault(const Constant(true))(); // belum terkirim
  IntColumn get serverSeq => integer().nullable()(); // nomor urut dari server

  @override
  Set<Column> get primaryKey => {id};
}

class Products extends Table with SyncColumns {
  TextColumn get barcode => text().nullable()(); // null = barang tanpa barcode
  TextColumn get name => text().withLength(min: 1, max: 120)();
  TextColumn get unit => text().withDefault(const Constant('pcs'))(); // satuan jual = satuan dasar
  IntColumn get sellPrice => integer()(); // rupiah per 1 unit
  IntColumn get costPrice => integer().nullable()(); // rupiah per 1 unit; null = modal belum diisi
  IntColumn get minStockMilli => integer().withDefault(const Constant(0))();
  TextColumn get bulkUnitName => text().nullable()(); // mis. "dus" (hanya untuk UI)
  IntColumn get bulkUnitSize => integer().nullable()(); // isi per dus, dalam unit dasar
}

/// Ledger stok. Stok produk = SUM(qtyMilli). Penjualan juga menulis baris di sini.
class StockMovements extends Table with SyncColumns {
  TextColumn get productId => text().references(Products, #id)();
  TextColumn get type => textEnum<MovementType>()();
  IntColumn get qtyMilli => integer()(); // + masuk, - keluar
  IntColumn get totalCost => integer().nullable()(); // rupiah, khusus purchase
  TextColumn get sourceId => text().nullable()(); // sale_id, atau id movement yang dibalik
  TextColumn get note => text().nullable()();
  DateTimeColumn get occurredAt => dateTime()();
}

class Sales extends Table with SyncColumns {
  DateTimeColumn get occurredAt => dateTime()();
  TextColumn get businessDate => text()(); // 'YYYY-MM-DD' waktu lokal saat transaksi
  IntColumn get revenueTotal => integer()(); // tidak berubah setelah dibuat
  DateTimeColumn get voidedAt => dateTime().nullable()(); // batal = buat movement pembalik
  TextColumn get note => text().nullable()();
}

class SaleItems extends Table with SyncColumns {
  TextColumn get saleId => text().references(Sales, #id)();
  TextColumn get productId => text().references(Products, #id)();
  TextColumn get productName => text()(); // snapshot
  IntColumn get qtyMilli => integer()();
  IntColumn get unitPrice => integer()(); // snapshot, rupiah per 1 unit
  IntColumn get revenueTotal => integer()(); // round(qtyMilli * unitPrice / 1000)
  IntColumn get costTotal => integer().nullable()(); // snapshot; null = modal belum diisi
}

class Expenses extends Table with SyncColumns {
  TextColumn get category => text()();
  IntColumn get amount => integer()();
  DateTimeColumn get occurredAt => dateTime()();
  TextColumn get businessDate => text()();
  TextColumn get note => text().nullable()();
}

/// LOKAL SAJA (tidak disinkronkan): cache hasil Open Food Facts / Open Prices.
class ProductReferences extends Table {
  TextColumn get barcode => text()();
  TextColumn get name => text().nullable()();
  IntColumn get refPrice => integer().nullable()(); // hanya simpan jika currency == IDR
  TextColumn get currency => text().nullable()();
  DateTimeColumn get priceDate => dateTime().nullable()();
  DateTimeColumn get fetchedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {barcode};
}

/// LOKAL SAJA: deviceId, lastPullCursor, ownerId.
class SyncMeta extends Table {
  TextColumn get key => text()();
  TextColumn get value => text()();

  @override
  Set<Column> get primaryKey => {key};
}

// Jalankan di onCreate / migrasi (customStatement):
//   CREATE UNIQUE INDEX uq_products_barcode ON products(barcode)
//     WHERE barcode IS NOT NULL AND deleted_at IS NULL;
//   CREATE INDEX ix_movements_product ON stock_movements(product_id);
//   CREATE INDEX ix_sales_date ON sales(business_date);
//   CREATE INDEX ix_sale_items_sale ON sale_items(sale_id);
//
// Stok per produk:
//   SELECT product_id, SUM(qty_milli) FROM stock_movements
//   WHERE deleted_at IS NULL GROUP BY product_id;
//
// Laba kotor per hari (baris tanpa modal dihitung terpisah, bukan sebagai 0):
//   SELECT s.business_date,
//          SUM(i.revenue_total - i.cost_total) AS gross_profit,
//          SUM(i.cost_total IS NULL)           AS items_without_cost
//   FROM sales s JOIN sale_items i ON i.sale_id = s.id
//   WHERE s.voided_at IS NULL AND s.deleted_at IS NULL
//   GROUP BY s.business_date;
