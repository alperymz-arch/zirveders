from abc import ABC, abstractmethod

from pydantic import BaseModel


class CustomerDTO(BaseModel):
    external_id: str
    name: str
    tax_number: str | None = None
    balance: float = 0.0


class InvoiceDTO(BaseModel):
    external_id: str | None = None
    reference_no: str
    customer_external_id: str
    total_amount: float
    currency: str = "TRY"
    lines: list[dict] = []


class AccountingProvider(ABC):
    """Muhasebe programlarıyla konuşan tüm adapter'ların uyması gereken sözleşme.

    Yeni bir muhasebe programı eklenirken sadece bu sınıfı implemente eden bir
    adapter yazılır; iş mantığı ve API katmanı değişmez.
    """

    @abstractmethod
    def get_customers(self) -> list[CustomerDTO]: ...

    @abstractmethod
    def get_customer(self, external_id: str) -> CustomerDTO | None: ...

    @abstractmethod
    def push_invoice(self, invoice: InvoiceDTO) -> str:
        """Faturayı muhasebe programına gönderir, oluşan kaydın external_id'sini döner."""
        ...

    @abstractmethod
    def cancel_invoice(self, external_id: str) -> None:
        """Muhasebe programında daha önce oluşturulmuş bir faturayı iptal eder."""
        ...
