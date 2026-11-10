# Animasyon Çalışması (anime.md)

Frontend'e animasyon altyapısı entegrasyonu. İlke: **yalnızca CSS**, yeni bağımlılık yok,
`prefers-reduced-motion` her zaman saygı görür.

## Durum

| Ekran | Durum | Dosya |
|---|---|---|
| Login | Tamamlandı (push bekliyor) | `frontend/src/index.css` ("Login animasyonları") |
| Layout (header/nav) | Yapılacak | `components/Layout.tsx` |
| Dashboard | Yapılacak | `pages/Dashboard.tsx` |
| Invoices | Yapılacak | `pages/Invoices.tsx` |
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
2. Sayfa geçişi: route değişiminde hafif fade/rise.
3. Dashboard kartlarında kademeli giriş + hover yükselmesi.
4. Fatura tablosunda yeni/silinen satır animasyonu, durum rozeti geçişi.
5. Toast/alert bildirimleri için giriş-çıkış animasyonu.

## Notlar

- Referans repo `JohnHeibel/ClaudeAnimationBase` oturuma eklenemedi (izin reddedildi);
  içeriği incelenmedi, bu yüzden hiçbir kod ondan alınmadı.
- Doğrulama: `cd frontend && npm run build` geçti; görsel kontrol `npm run dev` ile yapılmalı.
- Push: GitHub App erişimi (403) çözülünce `claude/kur-lvzoen` dalına gönderilecek.
