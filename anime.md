# Animasyon Çalışması (anime.md)

Frontend'e animasyon altyapısı entegrasyonu. İlke: **yalnızca CSS**, yeni bağımlılık yok,
`prefers-reduced-motion` her zaman saygı görür.

## Durum

| Ekran | Durum | Dosya |
|---|---|---|
| Login | Tamamlandı | `frontend/src/index.css` ("Login animasyonları") |
| Layout (header/nav) | Tamamlandı (sayfa geçişi, aktif menü) | `components/Layout.tsx` |
| Dashboard | Tamamlandı (kart + liste satırı) | `index.css` ("Genel animasyonlar") |
| Invoices | Tamamlandı (satırlar genel kurallardan, rozet pop-in) | `pages/Invoices.tsx` |
| Settings | Yapılacak | `pages/Settings.tsx` |

## Login'de yapılanlar

- Sol panel gradient akışı (`login-gradient`, 14 sn)
- Arka plan dairelerinin süzülmesi (`login-float`)
- Logo ikonu çizim efekti (`login-draw`)
- Başlık/açıklama/rozet/form alanları kademeli giriş (`login-rise`)
- Hatalı girişte hata kutusu sarsıntısı (`login-shake`)
- Buton hover/active geçişi
- `prefers-reduced-motion: reduce` → hepsi kapalı

## Sıradaki adımlar

1. Ortak keyframe'leri (`rise`, `shake`) `login-` önekinden çıkarıp genel yardımcı sınıflara taşı.
2. ~~Sayfa geçişi~~ — yapıldı (`.page-enter` fade, `NavLink` aktif durum).
3. ~~Dashboard kartları~~ — yapıldı: `.card`/`.alert` giriş animasyonu, liste satırlarında kademeli giriş + hover.
4. ~~Fatura satırları/rozet~~ — yapıldı (`badge-pop`).
5. Toast/alert bildirimleri için giriş-çıkış animasyonu.

## Notlar

- Referans repo `JohnHeibel/ClaudeAnimationBase` oturuma eklenemedi (izin reddedildi);
  içeriği incelenmedi, bu yüzden hiçbir kod ondan alınmadı.
- Doğrulama: `cd frontend && npm run build` geçti; görsel kontrol `npm run dev` ile yapılmalı.
- Push: GitHub App erişimi (403) çözülünce `claude/kur-lvzoen` dalına gönderilecek.
