# Proje 3: Akıllı Veri Analitiği ve Makine Öğrenmesi Uygulaması

Bu proje; bulut platformlarında veri işleme, makine öğrenmesi modeli geliştirme, eğitme, dağıtma ve verilerden tahmin/bilgi çıkarma süreçlerini uçtan uca yöneten çoklu dil (Python, Node.js, .NET, Java, PHP) ve çoklu bulut (AWS, GCP, Azure) mimarisinin şablonunu ve dökümantasyonunu sunar.

> [!IMPORTANT]
> **Önemli Tavsiye:** Bu projede çalışırken lütfen IDE'nizde `/Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics` klasörünü **aktif çalışma alanı (workspace)** olarak ayarlayın.

---

## 📂 Dizin Yapısı

```text
project-3-smart-analytics/
├── README.md                           # Proje genel bakışı ve dizin haritası
├── docker-compose.yml                  # Yerel mikroservis orkestrasyonu (FastAPI + Gateway)
├── docs/                               # Detaylı Mimari ve Strateji Dökümanları
│   ├── architecture_and_design.md      # Mikroservis tasarımı ve bulut dağılımı
│   ├── ml_pipeline.md                  # Veri ambarı ve model eğitim boru hattı
│   ├── cloud_deployment_strategy.md    # Terraform/Sunucusuz dağıtım stratejileri
│   └── roadmap.md                      # Proje yol haritası (Faz 1 - Faz 5)
└── boilerplate/                        # Temel Başlangıç Kod Şablonları (Boilerplate)
    ├── python-ml-api/                  # FastAPI ile ML Model API
    │   ├── main.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── .env.example
    ├── node-gateway/                   # Express.js Client API Gateway
    │   ├── server.js
    │   ├── package.json
    │   ├── Dockerfile
    │   └── .env.example
    └── bigquery-connector/             # Python BigQuery Okuma/Yazma Scripti
        ├── bq_connector.py
        └── requirements.txt
```

---

## ⚡ Docker Compose ile Yerel Kurulum ve Çalıştırma

Projeyi yerel bilgisayarınızda tek bir komutla ayağa kaldırmak için:

1.  **Bağlantıları Docker ortamında ayağa kaldırın:**
    ```bash
    docker-compose up --build
    ```
2.  **Gateway üzerinden test edin:**
    ```bash
    curl -X POST http://localhost:3000/api/predict \
      -H "Content-Type: application/json" \
      -d '{"features": [120.0, 3.0, 15.0, 4.5]}'
    ```

---

## 📖 Dökümantasyon Bağlantıları

Proje detaylarını incelemek için aşağıdaki dökümantasyon dosyalarına tıklayabilirsiniz:

1. **[Sistem Mimarisi ve Mikroservis Tasarımı](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/architecture_and_design.md):** Farklı dil ve teknolojilerin entegrasyonu ile bulut dağılım planları.
2. **[Makine Öğrenmesi Boru Hattı (ML Pipeline)](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/ml_pipeline.md):** Veri çekme, işleme, BigQuery analitiği ve model eğitim döngüsü.
3. **[Bulut Dağıtım Stratejisi](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/cloud_deployment_strategy.md):** AWS üzerinde SageMaker, API Gateway ve Lambda entegrasyonu için IaC (Terraform) şablonu.
4. **[Geliştirme Yol Haritası](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/roadmap.md):** Projenin hayata geçirilmesi için adım adım takvim ve metodoloji planı.

---

## 🚀 Başlangıç Kod Şablonları

- **[FastAPI Model API](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/boilerplate/python-ml-api/main.py):** TensorFlow ve PyTorch modellerini yükleyip web API üzerinden sunan Python servisi.
- **[Express.js Gateway](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/boilerplate/node-gateway/server.js):** Python ML servisine güvenli istek atan ve client'lara veri sunan ara katman servisi.
- **[BigQuery Connector](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/boilerplate/bigquery-connector/bq_connector.py):** Python üzerinden BigQuery'ye yüksek performanslı veri okuma/yazma gerçekleştiren kütüphane.
