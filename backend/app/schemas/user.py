from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = ""


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
