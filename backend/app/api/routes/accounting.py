import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.accounting import get_accounting_provider
from app.accounting.base import AccountingProvider, CustomerDTO
from app.api.deps import get_current_user
from app.core.db import get_db
from app.models.invoice import Invoice
from app.models.user import User
from app.schemas.invoice import InvoiceCreate, InvoiceLineOut, InvoiceOut
from app.services.invoice_service import create_and_send_invoice

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
    )


@router.get("/invoices", response_model=list[InvoiceOut])
def list_invoices(
    db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> list[InvoiceOut]:
    invoices = db.query(Invoice).order_by(Invoice.created_at.desc()).limit(50).all()
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
