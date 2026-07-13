from pydantic import BaseModel


class AccountingSettingsIn(BaseModel):
    api_key: str


class AccountingSettingsOut(BaseModel):
    configured: bool
    api_key_preview: str | None = None
