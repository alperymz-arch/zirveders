"""ZirAPI (Zeruxsoft) tabanlı Zirve entegrasyon adapter'ı.

Bu uygulamayı kullanacak kişilerin zirapi.com üzerinden zaten bir ZirAPI
aboneliği olduğu varsayılıyor — bu yüzden doğrudan Zirve'nin veritabanına
bağlanmıyoruz, onun yerine ZirAPI'nin REST arayüzüne istek atıyoruz.

API key .env dosyasına gömülmez: admin panelindeki "Muhasebe Ayarları"
ekranından girilir, DB'de şifreli saklanır (bkz. app/models/accounting_settings.py,
app/services/accounting_settings_service.py, app/api/routes/settings.py).

ÖNEMLİ: ZirAPI'nin gerçek endpoint yolları, istek/yanıt gövdeleri ve auth
header formatı bu dosyada TEYİT EDİLMEDİ — Zeruxsoft'un resmi dökümanı
elde edilmeden uydurulmadı. Aşağıdaki değerler TODO placeholder'dır; gerçek
bir ZirAPI anahtarı alınıp zirapi.com dökümantasyonu/destek ile teyit
edilince güncellenmeli.
"""

import httpx

from app.accounting.base import AccountingProvider, CustomerDTO, InvoiceDTO
from app.core.db import SessionLocal
from app.services.accounting_settings_service import get_decrypted_api_key


class ZirveAccountingProvider(AccountingProvider):
    # TODO: gerçek base URL zirapi.com dökümantasyonuyla teyit edilecek.
    BASE_URL = "https://api.zirapi.com"

    def _get_api_key(self) -> str:
        db = SessionLocal()
        try:
            api_key = get_decrypted_api_key(db)
        finally:
            db.close()
        if not api_key:
            raise RuntimeError(
                "ZirAPI anahtarı tanımlı değil. Admin panelinden "
                "Muhasebe Ayarları'na girip API key kaydedin."
            )
        return api_key

    def _client(self) -> httpx.Client:
        api_key = self._get_api_key()
        # TODO: auth header adı/biçimi (Authorization: Bearer mi, X-Api-Key mi?) teyit edilecek.
        return httpx.Client(
            base_url=self.BASE_URL, headers={"X-Api-Key": api_key}, timeout=15.0
        )

    def get_customers(self) -> list[CustomerDTO]:
        # TODO: gerçek endpoint path'i ve yanıt alan adları teyit edilecek (örn. /cari).
        with self._client() as client:
            response = client.get("/cari")
            response.raise_for_status()
            data = response.json()
        return [
            CustomerDTO(
                external_id=item.get("kod", ""),
                name=item.get("unvan", ""),
                tax_number=item.get("vkn"),
                balance=float(item.get("bakiye", 0) or 0),
            )
            for item in data
        ]

    def get_customer(self, external_id: str) -> CustomerDTO | None:
        for customer in self.get_customers():
            if customer.external_id == external_id:
                return customer
        return None

    def push_invoice(self, invoice: InvoiceDTO) -> str:
        # TODO: gerçek endpoint path'i ve gövde alan adları teyit edilecek (örn. /fatura).
        payload = {
            "referansNo": invoice.reference_no,
            "cariKod": invoice.customer_external_id,
            "toplamTutar": invoice.total_amount,
            "paraBirimi": invoice.currency,
            "satirlar": invoice.lines,
        }
        with self._client() as client:
            response = client.post("/fatura", json=payload)
            response.raise_for_status()
            data = response.json()
        return data.get("id", invoice.reference_no)
