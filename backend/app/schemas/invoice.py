from datetime import datetime

from pydantic import BaseModel, Field


class InvoiceLineIn(BaseModel):
    aciklama: str
    tutar: float = Field(gt=0)


class InvoiceCreate(BaseModel):
    customer_external_id: str
    reference_no: str | None = None
    currency: str = "TRY"
    lines: list[InvoiceLineIn] = Field(min_length=1)


class InvoiceLinesUpdate(BaseModel):
    lines: list[InvoiceLineIn] = Field(min_length=1)


class InvoiceLineOut(BaseModel):
    aciklama: str
    tutar: float


class InvoiceOut(BaseModel):
    id: int
    reference_no: str
    customer_external_id: str
    customer_name: str
    total_amount: float
    currency: str
    lines: list[InvoiceLineOut]
    status: str
    external_id: str | None
    error_message: str | None
    created_at: datetime
    deleted_at: datetime | None
