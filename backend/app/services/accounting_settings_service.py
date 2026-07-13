from sqlalchemy.orm import Session

from app.core.security import decrypt_secret, encrypt_secret
from app.models.accounting_settings import AccountingSettings

ZIRVE_PROVIDER = "zirve"


def get_settings_row(db: Session, provider: str = ZIRVE_PROVIDER) -> AccountingSettings | None:
    return db.query(AccountingSettings).filter(AccountingSettings.provider == provider).first()


def save_api_key(db: Session, api_key: str, provider: str = ZIRVE_PROVIDER) -> AccountingSettings:
    row = get_settings_row(db, provider)
    if row is None:
        row = AccountingSettings(provider=provider)
        db.add(row)
    row.api_key_encrypted = encrypt_secret(api_key)
    db.commit()
    db.refresh(row)
    return row


def get_decrypted_api_key(db: Session, provider: str = ZIRVE_PROVIDER) -> str | None:
    row = get_settings_row(db, provider)
    if row is None or not row.api_key_encrypted:
        return None
    return decrypt_secret(row.api_key_encrypted)
