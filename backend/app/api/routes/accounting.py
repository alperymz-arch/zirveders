from fastapi import APIRouter, Depends

from app.accounting import get_accounting_provider
from app.accounting.base import AccountingProvider, CustomerDTO
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/accounting", tags=["accounting"])


@router.get("/customers", response_model=list[CustomerDTO])
def list_customers(
    provider: AccountingProvider = Depends(get_accounting_provider),
    _: User = Depends(get_current_user),
) -> list[CustomerDTO]:
    return provider.get_customers()
