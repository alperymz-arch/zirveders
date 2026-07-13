from app.accounting.base import AccountingProvider, CustomerDTO, InvoiceDTO


class MockAccountingProvider(AccountingProvider):
    """Gerçek muhasebe programı netleşene kadar geliştirme ve test için kullanılır."""

    def __init__(self) -> None:
        self._customers = {
            "C001": CustomerDTO(external_id="C001", name="Örnek Müşteri A.Ş.", balance=1500.0),
            "C002": CustomerDTO(external_id="C002", name="Test Ticaret Ltd.", balance=-320.5),
        }
        self._invoice_counter = 0
        self._cancelled_invoices: set[str] = set()

    def get_customers(self) -> list[CustomerDTO]:
        return list(self._customers.values())

    def get_customer(self, external_id: str) -> CustomerDTO | None:
        return self._customers.get(external_id)

    def push_invoice(self, invoice: InvoiceDTO) -> str:
        self._invoice_counter += 1
        return f"MOCK-INV-{self._invoice_counter:05d}"

    def cancel_invoice(self, external_id: str) -> None:
        if external_id in self._cancelled_invoices:
            raise ValueError(f"Fatura zaten iptal edilmiş: {external_id}")
        self._cancelled_invoices.add(external_id)
