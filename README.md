# Muhasebe Entegrasyon WebApp

Yerel ağda çalışan bir webapp: muhasebe programından veri okur, muhasebe programına
veri yükler. Kurallar ve mimari kararlar için [CLAUDE.md](CLAUDE.md).

Zirve masaüstü uygulaması olduğu için müşteri sahasındaki sunucu genelde
**Windows** olur — bu proje hem Windows hem macOS/Linux'ta çalışacak şekilde
tasarlandı (bkz. "Windows Notları").

## Docker ile tam kurulum (önerilen, on-premise — Windows dahil)
Windows'ta [Docker Desktop](https://www.docker.com/products/docker-desktop/)
(WSL2 backend ile) kurulu olması yeterli; komutlar PowerShell'de de aynen çalışır.
```
copy .env.example .env   # Windows (PowerShell/cmd) — macOS/Linux'ta: cp .env.example .env
docker compose up -d --build
```

## Geliştirme (backend)

**macOS / Linux:**
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # SECRET_KEY, DATABASE_URL vb. düzenle
alembic upgrade head
python -m scripts.create_admin
uvicorn app.main:app --reload
```

**Windows (PowerShell):**
```
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy ..\.env.example ..\.env   # SECRET_KEY, DATABASE_URL vb. düzenle
alembic upgrade head
python -m scripts.create_admin
uvicorn app.main:app --reload
```
PowerShell script çalıştırmayı reddederse (`execution of scripts is disabled`),
yönetici olarak bir kere `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
çalıştırmak gerekir.

## Geliştirme (frontend)
```
cd frontend
npm install
npm run dev
```
(Windows'ta da aynı komutlar — Node.js kurulu olması yeterli.)

## Test
```
cd backend
pytest
```

## Windows Notları
- **ZirAPI tabanlı entegrasyon** (bkz. CLAUDE.md → "Zirve Entegrasyon
  Notları") sadece HTTP isteği attığı için işletim sistemine bağlı bir
  sürücü/bağımlılık gerektirmez — `pyodbc`/`unixODBC` gibi Unix'e özgü bir
  paket kullanılmıyor, Windows'ta ekstra kurulum gerekmez.
- Native (Docker'sız) Windows kurulumunda PostgreSQL yerine geliştirme için
  varsayılan SQLite (`DATABASE_URL=sqlite:///./dev.db`) sorunsuz çalışır;
  üretimde PostgreSQL kullanılacaksa [PostgreSQL for Windows](https://www.postgresql.org/download/windows/)
  kurulmalı ya da Docker Compose'daki `db` servisi tercih edilmeli.
- Docker Compose'da `frontend` servisi 80 portunu kullanıyor; Windows'ta IIS
  veya başka bir servis bu portu tutuyorsa `docker-compose.yml`'de
  `"80:80"` yerine `"8080:80"` gibi farklı bir host portu seçilebilir.
- Git satır sonu farklarından (CRLF/LF) kaynaklı sorunları önlemek için
  repoya `.gitattributes` eklendi.

## Durum
Muhasebe programı entegrasyonu **Zirve**, **ZirAPI** (zirapi.com) üzerinden
çalışıyor (`backend/app/accounting/zirve.py`). Kullanıcı kendi ZirAPI
anahtarını `/settings` sayfasından girer — gerçek endpoint/alan adları henüz
teyit edilmedi (TODO olarak işaretli). Geliştirme sırasında `mock` adapter
kullanılabilir (`ACCOUNTING_PROVIDER=mock`). Bkz. CLAUDE.md → "Açık Kararlar".

`/invoices` sayfasından fatura girilip muhasebe programına gönderilebiliyor:
müşteri seçimi, çok satırlı kalem girişi, otomatik/manuel referans no ile
idempotent gönderim ve geçmiş fatura listesi (`backend/app/api/routes/accounting.py`,
`backend/app/services/invoice_service.py`).
