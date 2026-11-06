"""sync_contract.py — kontrak sync BukuKasWarung (FastAPI + Pydantic v2).

Belum dijalankan: sesuaikan dengan versi library yang dipakai.

Skema Postgres (ringkas):
  owner_sync_state(owner_id PK, epoch uuid, next_seq bigint)
  setiap tabel sync: PRIMARY KEY (owner_id, id), server_seq bigint NOT NULL,
                     INDEX (owner_id, server_seq); TANPA FK antar tabel sync.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal, Union

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict, Field

router = APIRouter(prefix="/v1/sync", tags=["sync"])

MAX_PUSH_ROWS = 200
MAX_PULL_ROWS = 500
MIN_APP_VERSION = 1  # klien lebih lama -> HTTP 426

Money = Annotated[int, Field(ge=0)]  # rupiah, integer
UUIDStr = Annotated[str, Field(min_length=32, max_length=36)]
BusinessDate = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]


class SyncRow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUIDStr
    created_at: datetime
    updated_at: datetime  # jam klien, hanya informasi (bukan untuk urutan)
    deleted_at: datetime | None = None
    base_seq: int | None = None  # server_seq terakhir yang dilihat klien (dipakai products)


class ProductRow(SyncRow):
    table: Literal["products"] = "products"
    barcode: str | None = None
    name: Annotated[str, Field(min_length=1, max_length=120)]
    unit: str = "pcs"
    sell_price: Money
    cost_price: Money | None = None
    min_stock_milli: Annotated[int, Field(ge=0)] = 0
    bulk_unit_name: str | None = None
    bulk_unit_size: Annotated[int, Field(gt=0)] | None = None


class StockMovementRow(SyncRow):
    table: Literal["stock_movements"] = "stock_movements"
    product_id: UUIDStr
    # string mengikuti Drift textEnum (nama enum): voidReversal, bukan void_reversal
    type: Literal["purchase", "sale", "adjustment", "voidReversal"]
    qty_milli: int  # + masuk, - keluar
    total_cost: Money | None = None
    source_id: UUIDStr | None = None
    note: str | None = None
    occurred_at: datetime


class SaleRow(SyncRow):
    table: Literal["sales"] = "sales"
    occurred_at: datetime
    business_date: BusinessDate
    revenue_total: Money
    voided_at: datetime | None = None
    note: str | None = None


class SaleItemRow(SyncRow):
    table: Literal["sale_items"] = "sale_items"
    sale_id: UUIDStr
    product_id: UUIDStr
    product_name: str
    qty_milli: Annotated[int, Field(gt=0)]
    unit_price: Money
    revenue_total: Money
    cost_total: Money | None = None  # null = modal belum diisi


class ExpenseRow(SyncRow):
    table: Literal["expenses"] = "expenses"
    category: str
    amount: Annotated[int, Field(gt=0)]
    occurred_at: datetime
    business_date: BusinessDate
    note: str | None = None


Row = Annotated[
    Union[ProductRow, StockMovementRow, SaleRow, SaleItemRow, ExpenseRow],
    Field(discriminator="table"),
]
APPEND_ONLY = {"stock_movements", "sales", "sale_items", "expenses"}


class PushRequest(BaseModel):
    device_id: UUIDStr
    epoch: str | None = None  # epoch server terakhir yang dilihat klien
    rows: Annotated[list[Row], Field(max_length=MAX_PUSH_ROWS)]


class RowStatus(str, Enum):
    applied = "applied"  # baru/berubah -> server_seq baru
    unchanged = "unchanged"  # identik (retry idempoten) -> seq lama
    stale = "stale"  # base_seq usang (products): ambil versi server lewat pull
    rejected = "rejected"  # gagal aturan/validasi: jangan retry tanpa batas


class RowResult(BaseModel):
    table: str
    id: str
    status: RowStatus
    server_seq: int | None = None
    error: str | None = None


class PushResponse(BaseModel):
    epoch: str
    results: list[RowResult]


class PullChange(BaseModel):
    seq: int
    row: Row


class PullResponse(BaseModel):
    epoch: str
    changes: list[PullChange]  # urut seq naik, campuran semua tabel
    next_cursor: int
    has_more: bool


async def current_owner() -> str:
    """Ambil owner_id dari JWT. owner_id TIDAK PERNAH dari body request."""
    raise NotImplementedError


@router.post("/push", response_model=PushResponse)
async def push(
    body: PushRequest,
    x_app_version: int = Header(...),
    owner: str = Depends(current_owner),
) -> PushResponse:
    """
    1. x_app_version < MIN_APP_VERSION -> 426.
    2. Satu transaksi DB. Kunci baris owner_sync_state (SELECT ... FOR UPDATE):
       push per owner berurutan, jadi seq tidak pernah "melompat" saat commit.
    3. Per baris (owner_id, id), urutan pengecekan:
       a. belum ada            -> insert, seq = ++next_seq, applied
       b. ada & isi identik    -> unchanged (seq lama)      <- sebelum cek stale!
       c. tabel APPEND_ONLY    -> hanya deleted_at / voided_at null->terisi
                                  yang boleh berubah; selain itu rejected
       d. products             -> base_seq != seq server saat ini -> stale
                                  selain itu update, seq baru, applied
    4. Validasi gagal = rejected untuk baris itu saja (bukan 422 satu batch).
    """
    raise NotImplementedError


@router.get("/pull", response_model=PullResponse)
async def pull(
    cursor: int = 0,
    limit: int = MAX_PULL_ROWS,
    epoch: str | None = None,
    owner: str = Depends(current_owner),
) -> PullResponse:
    """
    Baris milik owner dengan seq > cursor, urut seq, maks MAX_PULL_ROWS.
    Selalu kembalikan epoch server. Jika epoch klien != epoch server, klien WAJIB:
    reset cursor = 0, tandai semua baris lokal dirty = true, lalu push ulang.
    """
    raise NotImplementedError


# ---- Algoritma sisi klien (Flutter) ----------------------------------------
# loop sync (background, timeout pertama >= 60 dtk karena cold start):
#   1. push: kirim baris dirty (maks 200) -> untuk applied/unchanged: dirty=false,
#      simpan serverSeq; stale: biarkan, akan diganti hasil pull; rejected: catat error.
#   2. ulangi sampai tidak ada baris dirty yang bisa dikirim.
#   3. pull dari cursor tersimpan, terapkan SATU transaksi lokal dengan
#      PRAGMA defer_foreign_keys = ON; lewati baris lokal yang masih dirty.
#   4. simpan next_cursor + epoch di SyncMeta; ulangi selama has_more.
#   5. jika epoch berubah: reset cursor, semua baris dirty = true, kembali ke 1.
