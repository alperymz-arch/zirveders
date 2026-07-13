import json
import uuid

from sqlalchemy.orm import Session

from app.accounting.base import AccountingProvider, InvoiceDTO
from app.models.audit_log import AuditLog
from app.models.invoice import Invoice
from app.models.user import User


def create_and_send_invoice(
    db: Session,
    provider: AccountingProvider,
    user: User,
    customer_external_id: str,
    customer_name: str,
    currency: str,
    lines: list[dict],
    reference_no: str | None,
) -> Invoice:
    """Faturayı kaydeder ve muhasebe programına gönderir.

    reference_no idempotency anahtarıdır: aynı referansla daha önce başarıyla
    gönderilmiş bir fatura varsa tekrar provider'a istek atılmaz, mevcut kayıt
    döner (bkz. CLAUDE.md -> Muhasebe Entegrasyon Kuralları).
    """
    if not reference_no:
        reference_no = f"WEB-{uuid.uuid4().hex[:12]}"

    existing = db.query(Invoice).filter(Invoice.reference_no == reference_no).first()
    if existing is not None and existing.status == "sent":
        return existing

    total_amount = sum(line["tutar"] for line in lines)

    if existing is None:
        invoice = Invoice(
            reference_no=reference_no,
            customer_external_id=customer_external_id,
            customer_name=customer_name,
            total_amount=total_amount,
            currency=currency,
            lines_json=json.dumps(lines),
            status="pending",
            created_by_user_id=user.id,
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
    else:
        invoice = existing

    dto = InvoiceDTO(
        reference_no=reference_no,
        customer_external_id=customer_external_id,
        total_amount=total_amount,
        currency=currency,
        lines=lines,
    )

    try:
        external_id = provider.push_invoice(dto)
        invoice.status = "sent"
        invoice.external_id = external_id
        invoice.error_message = None
        result = "success"
    except Exception as exc:  # noqa: BLE001 -- harici muhasebe programı hatası kullanıcıya net gösterilmeli
        invoice.status = "failed"
        invoice.error_message = str(exc)
        result = "failure"

    db.add(
        AuditLog(
            user_id=user.id,
            action="push_invoice",
            target=reference_no,
            payload=json.dumps(lines),
            result=result,
        )
    )
    db.commit()
    db.refresh(invoice)
    return invoice
