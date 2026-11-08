<div align="center">

# 🌈 BeforeScroll

### Ekrana dalmadan önce, kendine bir an ver.

**BeforeScroll**, uzun veya riskli ekran oturumları başlamadan önce kişisel kullanım örüntülerini görünür kılmayı amaçlayan, makine öğrenmesi destekli bir farkındalık demosudur.

[✨ Özellikler](#-öne-çıkan-özellikler) · [🚀 Hızlı başlangıç](#-hızlı-başlangıç) · [🧠 Model deneyleri](#-model-deneyleri) · [🔌 API](#-api-uç-noktaları) · [🗂️ Proje yapısı](#️-proje-yapısı)

<br>

![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20App-000000?style=for-the-badge&logo=flask&logoColor=white)
![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

</div>

> [!IMPORTANT]
> **Bu proje bir demo ve farkındalık aracıdır.** Gerçek telefon kullanım verilerini toplamaz; model ve panel uygulama içinde üretilen kurallı sentetik verilerle çalışır. Gösterilen sonuçlar ürün, sağlık veya klinik tavsiye değildir.

---

## 📚 İçindekiler

- [🌟 Proje hakkında](#-proje-hakkında)
- [✨ Öne çıkan özellikler](#-öne-çıkan-özellikler)
- [🧰 Teknoloji yığını](#-teknoloji-yığını)
- [🚀 Hızlı başlangıç](#-hızlı-başlangıç)
- [🧠 Model deneyleri](#-model-deneyleri)
- [🐳 Docker ile çalıştırma](#-docker-ile-çalıştırma)
- [🔌 API uç noktaları](#-api-uç-noktaları)
- [🗂️ Proje yapısı](#️-proje-yapısı)
- [⚠️ Sınırlar ve sorumlu kullanım](#️-sınırlar-ve-sorumlu-kullanım)

## 🌟 Proje hakkında

Ekranda ne kadar zaman geçirdiğimizi çoğu zaman oturum bittikten sonra fark ederiz. **BeforeScroll**, bu farkındalığı oturum başlamadan önce desteklemek için geçmiş kullanım örüntülerine bakan bir prototiptir.

Uygulama sentetik oturumlar oluşturur, bu verilerden zamana duyarlı özellikler çıkarır ve belirlenen erken uyarı ufkunda riskli kullanım olasılığını tahmin eder. Sonuçlar etkileşimli bir gösterge panelinde sunulur.

## ✨ Öne çıkan özellikler

| Özellik | Açıklama |
|---|---|
| 🎲 **Sentetik kullanım verisi** | Farklı kullanıcı ve günler için oturum süresi, uygulama açılışı, bildirimler ve kullanım tetikleyicileri simüle edilir. |
| 🔮 **Erken risk tahmini** | Geçmiş oturumlar ve zaman bilgileri kullanılarak seçilen uyarı ufkunda riskli kullanım olasılığı hesaplanır. Özellikler karar anından önceki bilgilerle sınırlıdır. |
| 🎚️ **Uyarlanabilir eşikler** | Bekleyen görevler varken sistem daha hassas, görevler tamamlandığında ise daha esnek eşikler uygular. |
| 📊 **Etkileşimli gösterge paneli** | Risk puanı, uyarı geri sayımı, günlük kullanım eğilimi, haftalık riskli oturumlar ve bildirim/sıkılma kaynaklı kullanım dağılımı görüntülenir. |
| 💬 **Rehber asistan** | Önceden tanımlı sorulara simüle edilmiş kullanım örüntülerine göre yanıt verir; mola ve bildirimleri gruplama önerileri sunar. |
| 🧪 **Model deneyleri** | Veri ve özellikleri dışa aktarabilir, değerlendirme metriklerini ve özellik önemini inceleyebilir, farklı tahmin ufuklarını karşılaştırabilirsiniz. |
| 🌗 **Tema seçenekleri** | Mobil uyumlu arayüz açık, koyu ve otomatik tema seçenekleri sunar. |

## 🧰 Teknoloji yığını

### Sunucu ve makine öğrenmesi

- **Python 3.11** — simülasyon, özellik üretimi ve modelleme
- **Flask** — web sunucusu ve JSON API
- **NumPy & pandas** — sentetik veri ve zaman serilerinin hazırlanması
- **scikit-learn** — lojistik regresyon, HistGradientBoosting, zaman bazlı veri ayrımı ve değerlendirme metrikleri

### Arayüz ve dağıtım

- **HTML, CSS ve JavaScript** — ek bir frontend framework'ü gerektirmeyen istemci arayüzü
- **Docker & Docker Compose** — uygulamayı ve isteğe bağlı model deneylerini konteyner içinde çalıştırma

## 🚀 Hızlı başlangıç

> Komutları uygulama dosyalarının bulunduğu `beforescroll/` dizininden çalıştırın.

### 1. Depoyu alın ve sanal ortam oluşturun

```bash
cd beforescroll
python -m venv .venv
```

### 2. Sanal ortamı etkinleştirin

```bash
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 3. Bağımlılıkları kurup uygulamayı başlatın

```bash
pip install -r requirements.txt
python app.py
```

Tarayıcınızda [http://localhost:8000](http://localhost:8000) adresini açın. İlk başlangıçta sentetik veri üretilir ve model eğitilir; bu işlem birkaç saniye sürebilir.

## 🧠 Model deneyleri

Varsayılan ayarlarla sentetik veri üretmek, özellikleri oluşturmak ve modelleri eğitip değerlendirmek için:

```bash
python main.py
```

1, 5, 10 ve 30 dakikalık erken uyarı ufuklarını karşılaştırmak için:

```bash
python main.py --sweep
```

Deney ayarlarını komut satırı seçenekleriyle değiştirebilirsiniz:

```bash
python main.py --users 60 --days 35 --horizon 10 --out output
```

Kullanılabilen başlıca parametreler:

| Parametre | İşlev |
|---|---|
| `--users` | Simüle edilecek kullanıcı sayısı |
| `--days` | Simülasyonun kapsayacağı gün sayısı |
| `--horizon` | Erken uyarı ufku (dakika) |
| `--seed` | Tekrarlanabilir deneyler için rastgelelik tohumu |
| `--out` | Üretilen çıktıların kaydedileceği dizin |
| `--sweep` | Birden fazla uyarı ufkunu karşılaştırır |

Çıktılar varsayılan olarak `output/` dizinine yazılır. Üretilen dosyalar arasında oturum verileri (`sessions.csv`) ve özellik tablosu (ör. `features_h10.csv`) bulunur.

## 🐳 Docker ile çalıştırma

Web uygulamasını konteyner içinde başlatmak için:

```bash
docker compose up --build web
```

Model ufuk taramasını tek seferlik çalıştırmak için:

```bash
docker compose --profile train run --rm train
```

## 🔌 API uç noktaları

Flask sunucusu aşağıdaki uç noktaları sağlar:

| Metot | Uç nokta | Açıklama |
|---|---|---|
| `GET` | `/` | Web arayüzünü sunar. |
| `GET` | `/api/state` | Panelin güncel simülasyon ve model durumunu döndürür. |
| `POST` | `/api/tasks` | Bir görevin tamamlanma durumunu günceller. |
| `POST` | `/api/checkin` | Günlük check-in yanıtını kaydeder. |
| `POST` | `/api/ask` | Asistana önceden tanımlı bir soru gönderir. |

## 🗂️ Proje yapısı

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

## ⚠️ Sınırlar ve sorumlu kullanım

- BeforeScroll **gerçek cihaz kullanımını izlemez**; veriler sentetik olarak üretilir.
- Tahminler simülasyon ve model deneyleri içindir; gerçek kişilerin davranışları hakkında güvenilir sonuç garantisi vermez.
- Paneldeki öneriler genel farkındalık amaçlıdır ve profesyonel sağlık desteğinin yerine geçmez.

---

<div align="center">

**BeforeScroll — kaydırmadan önce bir an dur, neye ihtiyacın olduğunu fark et.** 🌿

</div>
