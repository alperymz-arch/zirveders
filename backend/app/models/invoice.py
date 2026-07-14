from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Invoice(Base):
    """Webapp üzerinden girilip muhasebe programına gönderilen faturaların kaydı.

    reference_no idempotency anahtarıdır: aynı referansla ikinci kez
    gönderilirse muhasebe programına tekrar istek atılmaz, mevcut kayıt
    döner (bkz. app/services/invoice_service.py, CLAUDE.md -> Muhasebe
    Entegrasyon Kuralları).
    """

    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    reference_no: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    invoice_type: Mapped[str] = mapped_column(String(10), default="gelir")  # "gelir" | "gider"
    customer_external_id: Mapped[str] = mapped_column(String(100))
    customer_name: Mapped[str] = mapped_column(String(255))
    total_amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="TRY")
    lines_json: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20))  # "sent" | "failed" | "cancelled"
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    # Soft delete: silinen faturalar DB'den kaldırılmaz, "silinenler kutusu"na
    # taşınır (deleted_at doldurulur). Kalıcı silme sadece purge ile yapılır.
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
