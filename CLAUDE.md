# Muhasebe Entegrasyon WebApp

## Proje Amacı
Yerel ağda/on-premise çalışan bir muhasebe programından veri okuyabilen ve o programa
veri yazabilen (yükleyebilen) bir web uygulaması. Muhasebe programı **Zirve** olarak
netleşti (bkz. "Zirve Entegrasyon Notları"). Entegrasyon katmanı yine de
**adapter pattern** ile soyutlanmış durumda — ileride başka bir program/şube
farklı bir muhasebe programı kullanırsa iş mantığına dokunmadan yeni adapter eklenir.

> **Kapsam netleşiyor (2026-07-13 itibarıyla):** Uygulama artık tek bir firmanın
> kendi faturalarını girdiği bir araç olarak değil, **mali müşavirlerin/muhasebe
> ofislerinin birden fazla mükellefin (müşteri firmanın) muhasebe kayıtlarını
> otomatikleştirmesi için kullandığı çoklu-mükellef (multi-tenant) bir platform**
> olarak tasarlanıyor. Bu, veri modelini (Mükellef, Hesap Planı, mükellef bazlı
> Müşteri/Fatura/ZirAPI anahtarı) ve arayüzü (mükellef seçici) kökten etkileyen
> büyük bir yön değişikliği — henüz **tasarım/karar aşamasında**, kod
> yazılmadı. Detaylar için "Çoklu Mükellef Mimarisi (Karar Bekliyor)" bölümüne bak.

## Teknoloji Stack
- **Backend:** Python 3.12+, FastAPI
- **ORM / DB:** SQLAlchemy 2.x + Alembic migration, PostgreSQL (geliştirmede SQLite kabul edilir)
- **Frontend:** React (Vite) — ayrı bir SPA olarak, FastAPI'ye REST/JSON üzerinden bağlanır
- **Doğrulama:** Pydantic v2 modelleri (request/response şemaları)
- **Zamanlanmış işler:** APScheduler (Celery/Redis'e MVP aşamasında gerek yok — gerekirse sonra eklenir)
- **Auth:** Session tabanlı veya JWT, local kullanıcı tablosu, rol bazlı yetkilendirme (admin/kullanıcı)
- **Test:** pytest + httpx (backend), Vitest (frontend)
- **Lint/format:** ruff + black (backend), eslint + prettier (frontend)
- **Deployment:** Docker Compose (backend + frontend build + db) — tek komutla müşteri sahasına kurulabilmeli
- **Loglama:** structlog veya standart logging, JSON formatlı, dosyaya yazılır

## Platform Uyumluluğu (Windows dahil)
Zirve bir Windows masaüstü uygulaması olduğu için müşteri sahasındaki sunucu
büyük ihtimalle **Windows** olacak. Bu yüzden:
- Kodda Unix'e özgü varsayım yok: dosya yolları için (gerekirse) her zaman
  `pathlib.Path` kullanılır, ham `/` ile string birleştirme yapılmaz.
- İşletim sistemine özgü sistem paketi/sürücü gerektiren bağımlılıklardan
  kaçınılır (ör. `pyodbc`/`unixODBC` bu yüzden kaldırıldı — ZirAPI'ye HTTP
  isteği atmak yeterli, bkz. "Zirve Entegrasyon Notları").
- Docker Compose kurulumu Windows'ta Docker Desktop (WSL2 backend) ile
  değişiklik gerektirmeden çalışır; bu yüzden on-premise kurulum için
  öncelikli önerilen yol Docker Compose'dur.
- README'de hem macOS/Linux (bash) hem Windows (PowerShell) için ayrı
  kurulum adımları tutulur; sadece birini güncelleyip diğerini unutmamak
  gerekir.
- `.gitattributes` ile satır sonu normalize edilir (CRLF/LF karışıklığı
  Windows'ta geliştirme yapılırsa sorun çıkarmasın diye).

## Klasör Yapısı (öneri)
```
backend/
  app/
    api/            # FastAPI router'ları
    core/           # config, security, logging
    models/         # SQLAlchemy modelleri
    schemas/        # Pydantic şemaları
    accounting/      # muhasebe entegrasyon katmanı
      base.py        # AccountingProvider abstract interface
      zirve.py        # Zirve adapter (ZirAPI üzerinden HTTP)
      mock.py         # geliştirme/test için sahte adapter
    services/        # iş mantığı
    jobs/            # zamanlanmış senkronizasyon işleri
  tests/
  alembic/
frontend/
  src/
docker-compose.yml
.env.example
```

## Muhasebe Entegrasyon Kuralları
- Her muhasebe programı bir `AccountingProvider` interface'ini implemente eder
  (ör. `get_customers()`, `get_invoices()`, `push_invoice()`, `get_stock()`,
  `push_stock_movement()`). İş mantığı asla belirli bir muhasebe programına
  özel kod içermez, sadece bu interface üzerinden konuşur.
- Bağlantı bilgileri (API anahtarı, sunucu adresi, kullanıcı/şifre) **kesinlikle
  koda gömülmez**. Kurulum genelinde sabit olanlar (DB şifresi, SECRET_KEY)
  `.env` üzerinden okunur ve asla commit edilmez. Zirve API key gibi kurulum
  sonrası kullanıcı tarafından girilecek değerler ise admin panelinden girilir
  ve DB'de **şifreli** saklanır (bkz. "Zirve Entegrasyon Notları").
- Muhasebe programına yazılan her işlem (fatura, fiş, stok hareketi) audit log
  tablosuna kaydedilir: kim, ne zaman, ne gönderildi, sonuç neydi (başarı/hata).
- Muhasebe programına giden her yazma işlemi idempotent olacak şekilde tasarlanır
  (aynı kaydın iki kez gönderilmesi mükerrer kayıt oluşturmamalı) — harici referans
  numarası ile eşleştirme yapılır.
- Muhasebe programı erişilemez durumdaysa (ağ/servis kesintisi) istek kuyruğa
  alınır, kullanıcıya net hata mesajı gösterilir; sessiz başarısızlık yok.
- Gerçek program belirlenene kadar `mock.py` adapter'ı ile geliştirme ve test
  yapılır; iş mantığı ve UI bu mock üzerinden tamamlanabilir.

## Uygulanan Özellikler (Durum: 2026-07-13)
- **Auth:** JWT tabanlı login, rol bazlı yetki (admin/user), `/users/me`, `/users` (admin).
- **Müşteri (cari hesap):** `AccountingProvider` üzerinden listeleme, oluşturma,
  güncelleme (`/accounting/customers`).
- **Fatura yaşam döngüsü:** oluştur+gönder (idempotent, `reference_no` ile),
  iptal et, satır düzenle (sadece `status=failed` faturalarda, otomatik yeniden
  gönderim), yumuşak sil (silinenler kutusu), geri yükle, kalıcı sil (admin-only,
  önce silinmiş olmalı). Her yazma işlemi `AuditLog` tablosuna kaydediliyor.
- **Gelir/Gider ayrımı:** `Invoice.invoice_type` alanı (`"gelir" | "gider"`,
  varsayılan `"gelir"`) — backend (model/migration/şema/servis/route) ve frontend
  (form seçimi + Fatura Girişi ekranında ayrı "Gelir Faturaları" / "Gider
  Faturaları" ve ayrı "Silinen Gelir/Gider" bölümleri) tamamlandı.
- **Ayarlar:** `/settings/accounting` (ZirAPI anahtarı) ve `/settings/anthropic`
  (Claude API anahtarı, PDF fatura okuma için) — ikisi de admin-only, DB'de
  şifreli saklanıyor, sadece maskeli önizleme dönüyor. **Not:** Anthropic anahtarı
  için backend endpoint'i var ama Settings.tsx'te henüz form eklenmedi (TODO).
- **Frontend genel:** ortak `Layout.tsx` (header/nav/logout, tüm sayfalarda),
  tasarım sistemi (`index.css`), Login ekranı renkli split-screen olarak
  yeniden tasarlandı.
- **Test:** 43 backend testi (pytest) geçiyor; `requests.http` dosyası (VS
  Code REST Client / JetBrains formatı) manuel API testleri için mevcut.
- **Repo:** GitHub'da `alperymz-arch/zirveders` — her onaylanan değişiklik
  commit+push edildi.

## Toplu İçe Aktarma / PDF Okuma (Tasarlandı, Duraklatıldı)
- Hedef: Excel/CSV ile toplu fatura girişi + PDF faturaların Claude API
  (`claude-sonnet-5`, döküman anlama) ile aynı tek-satır Excel formatına
  (`musteri_kodu | referans_no | aciklama | tutar`) dönüştürülmesi, **her
  zaman kullanıcı onayından geçmesi zorunlu** (asla otomatik fatura oluşmaz).
- Bağımlılıklar eklendi ve commit edildi: `openpyxl`, `anthropic` (backend
  `requirements.txt`). Servis/route/frontend kodu **henüz yazılmadı** — ilk
  taslak kullanıcı tarafından "daha profesyonel bir tasarıma dönüştürülecek"
  gerekçesiyle reddedildi, iş duraklatıldı.
- Devam kararı alındığında ek gereksinimler netleşti (henüz uygulanmadı):
  - Önizleme tablosunda güçlü doğrulama (mükerrer referans no, eşleşmeyen
    müşteri kodu tespiti).
  - Ayrı bir `/invoices/import` sayfası/sihirbazı (mevcut Fatura Girişi
    ekranına eklenmeyecek).
  - Performans: toplu yüklemede provider'a gönderim ve PDF çıkarımı
    paralelleştirilecek (`ThreadPoolExecutor`, provider push için maks. 5,
    Claude PDF çıkarımı için maks. 3 eşzamanlı), güvenlik sınırı olarak
    200 satır / 10 PDF üst limiti düşünüldü.
- **Mükellef mimarisi netleşmeden bu özelliğin son tasarımı kilitlenmeyecek**
  — muhtemelen mükellef bazlı çalışacak ve hesap kodu kolonu eklenecek
  (bkz. aşağıki bölüm).

## Çoklu Mükellef Mimarisi (Karar Bekliyor — henüz kod yok)
Kullanıcı 2026-07-13'te uygulamanın asıl hedefini netleştirdi: **mali
müşavirler/muhasebe ofisleri, birden fazla mükellefin (müşteri firma) muhasebe
kayıtlarını bu uygulama üzerinden otomatikleştirecek.** Bu, mevcut "tek firma"
varsayımını (tek ZirAPI anahtarı, tek müşteri listesi, tek fatura havuzu)
kökten değiştiriyor. Netleşmesi gereken noktalar:
- **Yeni `Mükellef` modeli:** ad/unvan, VKN, aktif/pasif durumu. Mevcut
  `Customer` (cari hesap) ve `Invoice` kayıtları mükellef bazlı olacak.
- **Hesap Planı:** her mükellefe ait, sisteme yüklenebilir; tekrar eden
  firmalarda aynı hesap kodları otomatik önerilecek/eşleşecek. Muhtemelen
  toplu içe aktarma Excel formatına bir hesap kodu kolonu eklenecek.
- **Kullanıcı erişimi (netleşmedi):** ofisteki tüm kullanıcılar tüm
  mükellefleri mi görecek, yoksa kullanıcı bazlı mükellef ataması mı olacak?
- **ZirAPI bağlantı modeli (netleşmedi):** her mükellefin ayrı ZirAPI anahtarı
  mı olacak, yoksa tek anahtar + mükellef/firma parametresi ile mi çalışılacak
  (Zirve'nin kendisi çoklu firma destekliyor, ZirAPI'nin buna nasıl eriştiği
  gerçek anahtarla teyit edilene kadar belirsiz)?
- **UI:** bir "mükellef seçici" (workspace switcher benzeri) eklenmesi
  gerekecek; seçili mükellef, gösterilen müşteri/fatura/ayarlar bağlamını
  belirleyecek.
- Bu mimari netleşene kadar **yeni model/migration/route yazılmayacak** —
  önce kapsam ve veri modeli kullanıcıyla birlikte kesinleştirilecek.

## Zirve Entegrasyon Notları
- Zirve'nin resmi/genel kullanıma açık bir REST/SOAP API'si veya DLL'i **yok**.
- **Karar:** Bu uygulamayı kullanacak kişilerin zaten kendi **ZirAPI**
  (zirapi.com, Zeruxsoft'un üçüncü parti API'si) aboneliği/API key'i olduğu
  varsayılıyor. Bu yüzden Zirve'nin veritabanına hiç dokunmuyoruz — adapter
  doğrudan ZirAPI'ye HTTP isteği atıyor (`app/accounting/zirve.py`,
  `httpx` ile).
- **API key .env'de tutulmaz.** Her kurulum kendi ZirAPI anahtarını admin
  panelindeki "Muhasebe Ayarları" ekranından (`/settings` sayfası,
  `PUT /api/settings/accounting`) girer. Anahtar DB'de `accounting_settings`
  tablosunda `SECRET_KEY`'den türetilen bir Fernet anahtarıyla **şifreli**
  saklanır (`app/core/security.py` → `encrypt_secret`/`decrypt_secret`).
  API üzerinden asla düz metin geri dönmez, sadece son 4 hane maskeli
  gösterilir (`api_key_preview`).
- `app/accounting/zirve.py` içindeki ZirAPI endpoint path'leri
  (`/cari`, `/fatura`), auth header'ı (`X-Api-Key`) ve istek/yanıt alan
  adları (`kod`, `unvan`, `vkn`, `bakiye` vb.) **placeholder/TODO'dur** —
  Zeruxsoft'un resmi dökümantasyonu elde edilip gerçek bir ZirAPI anahtarıyla
  test edilmeden doğrulanamadı. Gerçek anahtar alınınca bu adapter
  güncellenmeli.
- Bu değişiklik önceki "SQL Server'a salt-okunur bağlan + dosya bırak"
  kararının yerini aldı — artık `pyodbc`/`unixODBC` bağımlılığı yok,
  ODBC sürücüsü kurulum derdi ortadan kalktı.

## Güvenlik Kuralları
- Bu uygulama finansal veriyle çalışıyor — güvenlik varsayılan, opsiyonel değil.
- Tüm endpoint'ler auth zorunlu (login/health-check hariç).
- Girdi doğrulaması sınırda (API katmanında) Pydantic ile yapılır, iç katmanlarda
  tekrar doğrulama yapılmaz (güvenme/doğrulama sınırı netleştirilir).
- SQL injection riskine karşı ham SQL yerine SQLAlchemy ORM/query builder kullanılır.
- Şifreler bcrypt/argon2 ile hash'lenir, asla düz metin saklanmaz.
- Hassas veriler (muhasebe API anahtarları, DB şifreleri) `.env` / secret manager'da
  tutulur, loglara asla yazılmaz.
- Rate limiting ve brute-force koruması login endpoint'inde zorunlu.

## Kod Stili Kuralları
- Python: tip belirteci (type hints) zorunlu, `black` + `ruff` ile formatlanır.
- Fonksiyon/sınıf isimleri açıklayıcı olmalı; docstring sadece davranışı
  şaşırtıcıysa yazılır, aksi halde isimlendirme yeterli olmalı.
- Her yeni API endpoint için en az bir pytest testi eklenir (mutlu yol + hata yolu).
- Gereksiz soyutlama yok: tek bir muhasebe programı adapter'ı gerekiyorsa fazla
  genel bir plugin sistemi kurulmaz, `AccountingProvider` interface'i yeterlidir.

## Yapılmayacaklar
- Muhasebe programına doğrudan veritabanı bağlantısı ile yazma yapılmaz
  (API/webservis yoksa dosya bazlı — CSV/XML aktarım — güvenli alternatiftir).
- Muhasebe API anahtarları asla `.env`'e veya koda gömülmez, düz metin
  loglanmaz ya da API yanıtında geri dönülmez (sadece maskeli önizleme).
- Gerçek muhasebe kimlik bilgileriyle test yapılmaz; test ortamı/mock kullanılır.
- Onaysız `--force`, `git push --force`, `rm -rf`, migration'ı geri alma gibi
  yıkıcı işlemler yapılmaz.

## Açık Kararlar (netleşince güncellenecek)
- [x] Hangi muhasebe programı? → **Zirve**
- [x] Entegrasyon yöntemi? → **ZirAPI** (kullanıcının kendi aboneliği), API key
      admin panelinden girilip DB'de şifreli saklanıyor
- [ ] ZirAPI'nin gerçek endpoint path'leri, auth header formatı, istek/yanıt
      alan adları (gerçek bir ZirAPI anahtarıyla test edilip
      `app/accounting/zirve.py` güncellenecek)
- [ ] Kaç kullanıcı, kaç şube — tek sunucu mu yoksa çoklu kurulum mu olacak?
- [ ] Senkronizasyon sıklığı: gerçek zamanlı mı, periyodik mi (ör. 15 dk)?
- [x] Uygulamanın hedef kullanıcısı? → **Mali müşavir/muhasebe ofisi**,
      birden fazla mükellefin muhasebe kaydını otomatikleştirmek için
      (bkz. "Çoklu Mükellef Mimarisi")
- [ ] Kullanıcı ↔ mükellef erişim modeli: herkes tüm mükellefleri mi görür,
      yoksa kullanıcı bazlı mükellef ataması mı olacak?
- [ ] ZirAPI ↔ mükellef ilişkisi: mükellef başına ayrı ZirAPI anahtarı mı,
      tek anahtar + firma parametresi mi?
- [ ] Hesap Planı veri modeli ve toplu içe aktarma/PDF okuma akışına nasıl
      entegre olacağı (hesap kodu kolonu, otomatik eşleştirme kuralları)
