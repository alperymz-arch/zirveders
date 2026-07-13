import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.accounting import get_accounting_provider
from app.accounting.base import AccountingProvider, CustomerDTO
from app.api.deps import get_current_user, require_admin
from app.core.db import get_db
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceLineOut, InvoiceOut
from app.services.invoice_service import (
    cancel_invoice_record,
    create_and_send_invoice,
    purge_invoice,
    restore_invoice,
    soft_delete_invoice,
)

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/customers", response_model=list[CustomerDTO])
def list_customers(
    provider: AccountingProvider = Depends(get_accounting_provider),
    _: User = Depends(get_current_user),
) -> list[CustomerDTO]:
    return provider.get_customers()


def _to_invoice_out(invoice: Invoice) -> InvoiceOut:
    return InvoiceOut(
        id=invoice.id,
        reference_no=invoice.reference_no,
        customer_external_id=invoice.customer_external_id,
        customer_name=invoice.customer_name,
        total_amount=invoice.total_amount,
        currency=invoice.currency,
        lines=[InvoiceLineOut(**line) for line in json.loads(invoice.lines_json)],
        status=invoice.status,
        external_id=invoice.external_id,
        error_message=invoice.error_message,
        created_at=invoice.created_at,
        deleted_at=invoice.deleted_at,
    )


def _get_invoice_or_404(db: Session, invoice_id: int) -> Invoice:
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Fatura bulunamadı")
    return invoice


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> list[InvoiceOut]:
    invoices = (
        db.query(Invoice)
        .filter(Invoice.deleted_at.is_(None))
        .order_by(Invoice.created_at.desc())
        .limit(50)
        .all()
    )
    return [_to_invoice_out(inv) for inv in invoices]


@router.get("/invoices/trash", response_model=list[InvoiceOut])
def list_deleted_invoices(
    db: Session = Depends(get_db), _: User = Depends(require_admin)
) -> list[InvoiceOut]:
    invoices = (
        db.query(Invoice)
        .filter(Invoice.deleted_at.is_not(None))
        .order_by(Invoice.deleted_at.desc())
        .limit(50)
        .all()
    )
    return [_to_invoice_out(inv) for inv in invoices]


@router.post("/invoices", response_model=InvoiceOut)
def create_invoice(
    payload: InvoiceCreate,
    provider: AccountingProvider = Depends(get_accounting_provider),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceOut:
    customer = provider.get_customer(payload.customer_external_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Müşteri bulunamadı")

    invoice = create_and_send_invoice(
        db=db,
        provider=provider,
        user=current_user,
        customer_external_id=payload.customer_external_id,
        customer_name=customer.name,
        currency=payload.currency,
        lines=[line.model_dump() for line in payload.lines],
        reference_no=payload.reference_no,
    )

    out = _to_invoice_out(invoice)
    if invoice.status == "failed":
        raise HTTPException(
            status_code=502,
            detail=(
                f"Fatura muhasebe programına gönderilemedi "
                f"(referans: {invoice.reference_no}): {invoice.error_message}"
            ),
        )
    return out


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceOut)
def cancel_invoice(
    invoice_id: int,
    provider: AccountingProvider = Depends(get_accounting_provider),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> InvoiceOut:
    invoice = _get_invoice_or_404(db, invoice_id)
    if invoice.deleted_at is not None:
        raise HTTPException(status_code=409, detail="Fatura silinenler kutusunda, önce geri yükleyin")
    if invoice.status == "cancelled":
        raise HTTPException(status_code=409, detail="Fatura zaten iptal edilmiş")

    invoice = cancel_invoice_record(db, provider, current_user, invoice)

    if invoice.status == "sent":  # iptal denendi ama başarısız oldu, durum değişmedi
        raise HTTPException(
            status_code=502,
            detail=f"Fatura iptal edilemedi (referans: {invoice.reference_no}): {invoice.error_message}",
        )
    return _to_invoice_out(invoice)


@router.delete("/invoices/{invoice_id}", status_code=204)
def delete_invoice(
    invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
) -> None:
    invoice = _get_invoice_or_404(db, invoice_id)
    if invoice.status == "sent":
        raise HTTPException(
            status_code=409, detail="Gönderilmiş bir fatura doğrudan silinemez, önce iptal edilmeli"
        )
    soft_delete_invoice(db, current_user, invoice)


@router.post("/invoices/{invoice_id}/restore", response_model=InvoiceOut)
def restore_invoice_route(
    invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
) -> InvoiceOut:
    invoice = _get_invoice_or_404(db, invoice_id)
    if invoice.deleted_at is None:
        raise HTTPException(status_code=409, detail="Fatura zaten silinenler kutusunda değil")
    return _to_invoice_out(restore_invoice(db, current_user, invoice))


@router.delete("/invoices/{invoice_id}/purge", status_code=204)
def purge_invoice_route(
    invoice_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_admin)
) -> None:
    invoice = _get_invoice_or_404(db, invoice_id)
    if invoice.deleted_at is None:
        raise HTTPException(status_code=409, detail="Önce silinenler kutusuna taşınmalı")
    purge_invoice(db, current_user, invoice)
