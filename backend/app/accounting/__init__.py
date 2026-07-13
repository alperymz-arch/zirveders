from functools import lru_cache

from app.accounting.base import AccountingProvider
from app.accounting.mock import MockAccountingProvider
from app.core.config import get_settings


@lru_cache
def get_accounting_provider() -> AccountingProvider:
    settings = get_settings()
    if settings.ACCOUNTING_PROVIDER == "mock":
        return MockAccountingProvider()
    if settings.ACCOUNTING_PROVIDER == "zirve":
        from app.accounting.zirve import ZirveAccountingProvider

        return ZirveAccountingProvider()
    raise ValueError(f"Bilinmeyen ACCOUNTING_PROVIDER: {settings.ACCOUNTING_PROVIDER}")
