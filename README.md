# Proje 3: Akıllı Veri Analitiği ve Makine Öğrenmesi Uygulaması

Bu proje; bulut platformlarında veri işleme, makine öğrenmesi modeli geliştirme, eğitme, dağıtma ve verilerden tahmin/bilgi çıkarma süreçlerini uçtan uca yöneten çoklu dil (Python, Node.js, .NET, Java, PHP) ve çoklu bulut (AWS, GCP) mimarisinin çalışan altyapısını, şablonlarını ve IaC (Terraform) tanımlarını sunar.

---

## 🏗️ Sistem ve Bulut Mimarisi

Uygulamanın genel veri akışı, bulut entegrasyonları ve mikroservis yapısı aşağıdaki şekilde tasarlanmıştır:

```mermaid
graph TD
    %% İstemci ve Gateway Katmanı
    Client[İstemci / Web App] -->|HTTP POST Request /api/predict| Gateway[Node.js Express Gateway]
    
    %% Gateway ve Model Çıkarım Katmanı (Lokal ve Bulut)
    subgraph Lokal Geliştirme (Docker Compose)
        Gateway -->|Proxy Requests| FastAPI[FastAPI ML Serving API]
        FastAPI -->|Predict| ModelLocal[Yerel Model / PyTorch & TF]
    end
    
    subgraph AWS Bulut Altyapısı (Terraform IaC)
        APIGateway[AWS API Gateway] -->|Proxy Integration| LambdaProxy[AWS Lambda Proxy Function]
        LambdaProxy -->|boto3 invoke_endpoint| SageMaker[AWS SageMaker Serverless Endpoint]
        SageMaker -->|Model serving| S3[(Amazon S3 - Model Artifacts)]
    end

    %% Veri Ambarı Katmanı
    FastAPI -->|Log verisi yazma/okuma| BQConnector[BigQuery Connector]
    BQConnector -->|Veri Analitiği & Depolama| GCPBigQuery[(Google Cloud BigQuery)]

    %% İletişim Yolları
    Gateway -.->|Uzak Canlı Test| APIGateway
```

### Mimari Bileşenlerin Görevleri:
1. **Node.js Express Gateway (İstemci Ara Katmanı):** İstemcilerden gelen tüm istekleri karşılar, şema doğrulaması (request validation) yapar, kimlik doğrulama ekler ve istekleri gerçek tahmin servislerine yönlendirir.
2. **FastAPI ML Serving API (Python API):** Yerel geliştirme ortamında PyTorch ve TensorFlow tabanlı modelleri yükleyip web API üzerinden tahmin sunar.
3. **AWS SageMaker & Lambda & API Gateway (Bulut Üretim Hattı):** S3 üzerinde saklanan eğitilmiş makine öğrenmesi modelini (`model.tar.gz`), AWS SageMaker Serverless Endpoint kullanarak sıfır sunucu yönetimi ile yayına alır. Önündeki Lambda ve API Gateway ile de dış dünyaya açar.
4. **GCP BigQuery Connector:** Üretilen tahmin verilerini ve model girdi parametrelerini, gelecekteki analizler ve model iyileştirme (re-training) süreçleri için Google Cloud BigQuery veri ambarına kaydeder.

---

## 📂 Dizin Yapısı ve Proje Rehberi

```text
project-3-smart-analytics/
├── README.md                           # Proje genel bakışı ve hızlı başlangıç rehberi
├── docker-compose.yml                  # Yerel mikroservis orkestrasyonu (FastAPI + Gateway)
├── docs/                               # Detaylı Mimari ve Strateji Dökümanları
│   ├── architecture_and_design.md      # Mikroservis tasarımı ve bulut dağılım planları
│   ├── ml_pipeline.md                  # Veri ambarı, ETL ve model eğitim boru hattı
│   ├── cloud_deployment_strategy.md    # AWS SageMaker ve Lambda sunucusuz mimari dökümanı
│   └── roadmap.md                      # Proje yönetim yol haritası (Faz 1 - Faz 5)
├── terraform/                          # Altyapı Tanımlama Kodları (IaC)
│   ├── main.tf                         # AWS S3, SageMaker, Lambda, API Gateway kurulum scripti
│   ├── lambda_function.py              # AWS Lambda proxy kodları
│   ├── lambda_function.zip             # Paketlenmiş Lambda kodu
│   └── model.tar.gz                    # AWS SageMaker için örnek model paketi
└── boilerplate/                        # Temel Başlangıç Kod Şablonları (Boilerplate)
    ├── python-ml-api/                  # FastAPI ile ML Model Serving Servisi
    │   ├── main.py
    │   ├── requirements.txt
    │   ├── Dockerfile
    │   └── .env.example
    ├── node-gateway/                   # Express.js Client API Gateway
    │   ├── server.js
    │   ├── package.json
    │   ├── Dockerfile
    │   └── .env.example
    └── bigquery-connector/             # Python BigQuery Okuma/Yazma Modülü
        ├── bq_connector.py
        └── requirements.txt
```

---

## ⚡ Yerel Geliştirme ve Docker Çalıştırma

Projeyi yerel bilgisayarınızda tek bir komutla ayağa kaldırıp FastAPI servisinin Node.js Gateway arkasından tahmin üretmesini sağlayabilirsiniz.

### 1. Servisleri Başlatın:
```bash
docker-compose up --build
```
Bu komut; Node.js Gateway servisini `3000` portunda, Python FastAPI servisini ise `8000` portunda ayağa kaldırır.

### 2. Gateway Üzerinden Tahmin Testi Gerçekleştirin:
```bash
curl -X POST http://localhost:3000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [120.0, 3.0, 15.0, 4.5]}'
```

### 3. BigQuery Bağlayıcı Testi:
`boilerplate/bigquery-connector` dizinine giderek BigQuery kimlik bilgilerinizi ayarladıktan sonra yerel testlerinizi yapabilirsiniz:
```bash
cd boilerplate/bigquery-connector
pip install -r requirements.txt
python bq_connector.py
```

---

## ☁️ Bulut Dağıtım (AWS Terraform IaC)

Tüm bulut altyapısı (S3, SageMaker Endpoint, Lambda ve API Gateway) **Terraform** kullanılarak otomatikleştirilmiştir.

### Dağıtım Adımları:
1. **Terraform dizinine geçin:**
   ```bash
   cd terraform
   ```
2. **Gereksinimleri kurun ve ilklendirin:**
   ```bash
   terraform init
   ```
3. **Altyapıyı analiz edin (Planlama):**
   ```bash
   terraform plan
   ```
4. **AWS üzerinde dağıtımı gerçekleştirin:**
   ```bash
   terraform apply -auto-approve
   ```
*Dağıtım tamamlandığında size canlı tahmin isteklerini göndereceğiniz **API Gateway URL**'sini ve model ağırlıklarının yüklendiği **S3 Bucket** adını çıktı (output) olarak verecektir.*

---

## 📖 Mimari ve Strateji Detayları

Projenin teknik alt detaylarını öğrenmek için aşağıdaki mimari kılavuzları inceleyebilirsiniz:

1. **[Sistem Mimarisi ve Tasarımı](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/architecture_and_design.md):** Mikroservis yapısı, gRPC, Apache Kafka kullanımı ve diller arası iletişim.
2. **[Makine Öğrenmesi Boru Hattı](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/ml_pipeline.md):** Veri ambarı yapılandırması, özellik mühendisliği (Feature Engineering) ve eğitim döngüleri.
3. **[Bulut Dağıtım Kılavuzu](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/cloud_deployment_strategy.md):** Sunucusuz çıkarım (Serverless Inference), güvenlik (VPC, IAM) ve izleme (CloudWatch) stratejileri.
4. **[Roadmap (Yol Haritası)](file:///Users/bernakalkan/.gemini/antigravity-ide/scratch/project-3-smart-analytics/docs/roadmap.md):** 5 fazdan oluşan 20 haftalık çevik (Agile) geliştirme planı.
