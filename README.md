# BeforeScroll

**BeforeScroll**, kullanıcının dijital kullanım alışkanlıklarını kendi geçmiş davranışlarıyla karşılaştırarak uzun veya riskli ekran oturumları başlamadan önce farkındalık oluşturmayı amaçlayan bir prototiptir. Uygulama; kullanım örüntülerini, günün saatini ve tamamlanmış sorumlulukları birlikte değerlendirir. Amacı telefonu tamamen bırakmayı sağlamak değil, kullanıcının odağını korumasına ve kullanımına bilinçli biçimde ara vermesine destek olmaktır.

> **Demo bilgisi:** Proje şu an gerçek telefon kullanım verilerini toplamaz. Model ve panel, uygulamanın içindeki kurallı sentetik verilerle çalışır. Sonuçlar ürün veya sağlık önerisi olarak değerlendirilmemelidir.

## Neler yapıyor?

- **Sentetik kullanım verisi üretir:** Farklı kullanıcılar ve günler için uygulama oturumları, kullanım süreleri, bildirimler, uygulama açılışları ve tetikleyici türleri oluşturur.
- **Riskli oturumları tahmin eder:** Geçmiş oturumlar ve zaman bilgileriyle, belirlenen erken uyarı ufkunda riskli kullanım olasılığını hesaplar. Özellikler yalnızca karar anından önce tamamlanmış oturumları kullanacak şekilde hazırlanır.
- **Kişisel ve sorumluluğa duyarlı eşikler uygular:** Bekleyen görevler varken sistem daha hassas, görevler tamamlandığında ise daha esnek çalışır.
- **Etkileşimli bir gösterge paneli sunar:** Risk puanı ve uyarı geri sayımı; günlük kullanım eğilimi; haftalık riskli oturumlar; bildirim ve sıkılma kaynaklı kullanım dağılımı; görev listesi ve günlük check-in gösterilir.
- **Basit bir rehber asistan içerir:** Önceden tanımlı sorulara kullanıcının simüle edilmiş örüntülerine göre yanıt verir; mola ve bildirimleri gruplama önerileri sunar.
- **Model deneylerini destekler:** Veri seti ve özellikleri dışa aktarır, metrikleri ve özellik önemini hesaplar; istenirse farklı tahmin ufuklarını karşılaştırır.

## Kullanılan teknolojiler

### Sunucu ve makine öğrenmesi

- **Python 3.11** — veri simülasyonu, özellik üretimi ve modelleme.
- **Flask** — gösterge panelini sunan web sunucusu ve JSON API.
- **NumPy ve pandas** — sentetik verilerin ve zaman serilerinin hazırlanması.
- **scikit-learn** — lojistik regresyon ve HistGradientBoosting sınıflandırıcıları, zaman bazlı eğitim/doğrulama/test ayrımı ve değerlendirme metrikleri.

### Arayüz ve çalıştırma

- **HTML, CSS ve JavaScript** — ek bir frontend framework'ü olmadan oluşturulan, mobil uyumlu arayüz; açık/koyu/otomatik tema desteği.
- **Docker ve Docker Compose** — uygulamayı ve isteğe bağlı model deneylerini konteyner içinde çalıştırma.

## Başlarken

Komutları, uygulama dosyalarının bulunduğu `beforescroll/` dizininden çalıştırın:

```bash
cd beforescroll
python -m venv .venv
```

Sanal ortamı etkinleştirin:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Bağımlılıkları kurup web uygulamasını başlatın:

```bash
pip install -r requirements.txt
python app.py
```

Ardından tarayıcıdan [http://localhost:8000](http://localhost:8000) adresini açın. İlk başlangıçta sentetik veri üretilir ve model eğitilir; bu işlem birkaç saniye sürebilir.

## Model deneyleri

Varsayılan ayarlarla sentetik veri üretmek, özellikleri oluşturmak, modelleri eğitip değerlendirmek için:

```bash
python main.py
```

1, 5, 10 ve 30 dakikalık erken uyarı ufuklarını karşılaştırmak için:

```bash
python main.py --sweep
```

Başlıca parametreler `--users`, `--days`, `--horizon`, `--seed` ve `--out` seçenekleriyle değiştirilebilir. Örneğin:

```bash
python main.py --users 60 --days 35 --horizon 10 --out output
```

Çıktılar varsayılan olarak `output/` dizinine yazılır. Bunlara oturum verileri (`sessions.csv`), özellikler (`features_h10.csv`) ve ufuk taraması çalıştırıldığında `horizon_sweep.csv` dahildir.

## Docker ile çalıştırma

Web uygulamasını başlatmak için `beforescroll/` dizininde:

```bash
docker compose up --build web
```

Model ufuk taramasını tek seferlik çalıştırmak için:

```bash
docker compose --profile train run --rm train
```

## API uç noktaları

Flask sunucusu aşağıdaki uç noktaları sağlar:

| Metot | Uç nokta | Açıklama |
|---|---|---|
| `GET` | `/` | Web arayüzünü sunar. |
| `GET` | `/api/state` | Panelin güncel simülasyon ve model durumunu döndürür. |
| `POST` | `/api/tasks` | Bir görevin tamamlanma durumunu günceller. |
| `POST` | `/api/checkin` | Günlük check-in yanıtını kaydeder. |
| `POST` | `/api/ask` | Asistana önceden tanımlı bir soru gönderir. |

## Proje yapısı

```text
beforescroll/
├── app.py                 # Flask uygulaması ve API uç noktaları
├── main.py                # Veri/model deneyleri için komut satırı girişi
├── config.py              # Simülasyon ve risk eşikleri
├── simulate.py            # Sentetik oturum verisi üretimi
├── features.py            # Zamana duyarlı özellik üretimi
├── model.py               # Eğitim, değerlendirme ve ufuk taraması
├── beforescroll/
│   └── service.py         # Panelin kullandığı model/veri servisi
├── web/
│   └── index.html         # İstemci arayüzü
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
