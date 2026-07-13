from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.db import get_db
from app.models.user import User
from app.schemas.accounting_settings import AccountingSettingsIn, AccountingSettingsOut
from app.services.accounting_settings_service import get_settings_row, save_api_key

router = APIRouter(prefix="/settings", tags=["settings"])


def _to_out(api_key: str | None) -> AccountingSettingsOut:
    if not api_key:
        return AccountingSettingsOut(configured=False)
    return AccountingSettingsOut(configured=True, api_key_preview=f"****{api_key[-4:]}")


@router.get("/accounting", response_model=AccountingSettingsOut)
def read_accounting_settings(
    db: Session = Depends(get_db), _: User = Depends(require_admin)
) -> AccountingSettingsOut:
    from app.core.security import decrypt_secret

    row = get_settings_row(db)
    if row is None or not row.api_key_encrypted:
        return AccountingSettingsOut(configured=False)
    return _to_out(decrypt_secret(row.api_key_encrypted))


@router.put("/accounting", response_model=AccountingSettingsOut)
def update_accounting_settings(
    payload: AccountingSettingsIn,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> AccountingSettingsOut:
    api_key = payload.api_key.strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="API key boş olamaz"
        )
    save_api_key(db, api_key)
    return _to_out(api_key)
