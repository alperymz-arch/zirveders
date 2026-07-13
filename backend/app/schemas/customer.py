from pydantic import BaseModel, Field


class CustomerCreate(BaseModel):
    external_id: str | None = None
    name: str
    tax_number: str | None = Field(default=None, pattern=r"^\d{10,11}$")


class CustomerUpdate(BaseModel):
    name: str
    tax_number: str | None = Field(default=None, pattern=r"^\d{10,11}$")
