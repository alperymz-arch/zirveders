from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AccountingSettings(Base):
    """ZirAPI gibi üçüncü parti muhasebe API anahtarlarının şifreli saklandığı ayar satırı.

    API key .env üzerinden değil, admin panelindeki Muhasebe Ayarları
    ekranından girilir; bu yüzden DB'de tutulur (bkz. CLAUDE.md).
    """

    __tablename__ = "accounting_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(50), unique=True)
    api_key_encrypted: Mapped[str | None] = mapped_column(String(500), nullable=True)
