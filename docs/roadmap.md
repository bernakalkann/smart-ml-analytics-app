# Proje Geliştirme Yol Haritası (Roadmap)

Bu döküman, sıfırdan başlanan **Akıllı Veri Analitiği ve Makine Öğrenmesi Uygulaması** projesinin fazlara ayrılmış, çevik (Agile/Scrum) metodolojiye uygun proje yönetim adımlarını ve teslim edilecek çıktıları (deliverables) listeler.

---

## Proje Zaman Çizelgesi Genel Bakış

```text
|-- Faz 1: Analiz & Altyapı --|-- Faz 2: ML & Pipeline --|-- Faz 3: Mikroservisler --|-- Faz 4: Bulut & CI/CD --|-- Faz 5: Test & Go-Live --|
|         Hafta 1 - 4         |       Hafta 5 - 8        |       Hafta 9 - 12        |       Hafta 13 - 16      |       Hafta 17 - 20       |
```

---

## 🛠️ Detaylı Faz Planı

### Faz 1: Altyapı ve Veri Tabanı Katmanının Kurulması (Hafta 1 - 4)
Bu fazda projenin veri depolama katmanı ve temel bulut ağ yapıları hazırlanır.

*   **Görevler:**
    1.  PostgreSQL (ilişkisel işlemler için) ve MongoDB (yarı-yapısal veriler ve loglar için) şemalarının tasarlanması ve yerel/bulut veritabanlarının kurulması.
    2.  Google Cloud Platform (GCP) üzerinde BigQuery Veri Ambarı ve dataset'lerin oluşturulması.
    3.  Kaynak veritabanlarından BigQuery'ye veri aktaracak batch ve CDC (Debezium/Kafka veya Airflow) entegrasyonlarının prototiplenmesi.
    4.  Terraform kullanarak AWS, Azure ve GCP ağ altyapısının (VPC, Subnet'ler, Cross-Cloud Peering) kurulması.
*   **Çıktılar:**
    *   Veritabanı şemaları (DDL).
    *   İlk Terraform ağ ve veritabanı konfigürasyon kodları.
    *   İlk ham veri aktarım senaryoları.

---

### Faz 2: ML Model Geliştirme ve Veri Hattı Entegrasyonu (Hafta 5 - 8)
Makine öğrenmesi modellerinin tasarlanması ve BigQuery analitik verileriyle eğitilmeye başlanması.

*   **Görevler:**
    1.  BigQuery üzerinde SQL tabanlı öznitelik mühendisliği (Feature Engineering) sorgularının yazılması ve `gold` veri tablolarının oluşturulması.
    2.  Python ile PyTorch/TensorFlow derin öğrenme modellerinin geliştirilmesi.
    3.  C# (.NET) ile tablosal regresyon/sınıflandırma için ML.NET eğitim betiklerinin yazılması.
    4.  Eğitim süreçlerini takip etmek ve modelleri versiyonlamak için **MLflow** veya bulut-yerel Model Registry entegrasyonunun yapılması.
*   **Çıktılar:**
    *   BigQuery Feature Engineering SQL dosyaları.
    *   Python ve C# model eğitim kodları.
    *   Kayıt altına alınmış ilk model sürümleri (artifacts).

---

### Faz 3: Mikroservis Geliştirme ve Servisler Arası Entegrasyon (Hafta 9 - 12)
Veritabanları, modeller ve kullanıcı arayüzleri arasındaki köprülerin kurulması.

*   **Görevler:**
    1.  Eğitilen modelleri yükleyip sunan **Python FastAPI ML Inference API**'sinin yazılması.
    2.  Kullanıcı isteklerini karşılayan, doğrulamaları yapan ve ML servisine yönlendiren **Node.js (Express) Gateway** geliştirilmesi.
    3.  Raporlama ve yönetim paneli olarak hizmet verecek **PHP (Laravel)** backend servislerinin yazılması.
    4.  Performans kritik servisler için **gRPC** protokollarının (Protocol Buffers) hazırlanması.
    5.  Asenkron olaylar için **Apache Kafka** event topic'lerinin tasarlanması ve Java Spring Boot kuyruk dinleyicilerinin yazılması.
*   **Çıktılar:**
    *   Mikroservis kod depoları ve Dockerfile dosyaları.
    *   `protobuf` şemaları.
    *   Servisler arası lokal entegrasyon testlerinin tamamlanması.

---

### Faz 4: Bulut Canlandırması (Cloud Deployment) ve CI/CD (Hafta 13 - 16)
Sistemin AWS, GCP ve Azure üzerinde tam otomatik ve ölçeklenebilir olarak dağıtılması.

*   **Görevler:**
    1.  AWS SageMaker Serverless Endpoint altyapısının Terraform ile kurulması.
    2.  API Gateway ve Lambda proxy fonksiyonlarının Terraform tanımlarının tamamlanması ve kodlarının paketlenmesi.
    3.  GitHub Actions veya GitLab CI ile otomatik entegrasyon:
        *   Kodların test edilmesi.
        *   Docker imajlarının build edilmesi ve bulut depolarına (ECR/GCR) yüklenmesi.
        *   ECS/App Service ve Lambda'ya otomatik deploy yapılması.
*   **Çıktılar:**
    *   Tamamlanmış IaC (Terraform) kod kütüphanesi.
    *   CI/CD pipeline tanımları (`.github/workflows/*.yml`).
    *   AWS/Azure üzerinde çalışan canlı servisler.

---

### Faz 5: Güvenlik, Testler ve Canlıya Geçiş (Go-Live) (Hafta 17 - 20)
Sistemin üretime (Production) hazır hale getirilmesi, güvenlik sıkılaştırmaları ve yayına alım.

*   **Görevler:**
    1.  **Yük Testleri (Load/Stress Testing):** K6 veya Locust kullanarak API Gateway ve ML modellerinin anlık yoğun yük altındaki gecikme (latency) ve hata oranlarının ölçülmesi.
    2.  **Güvenlik Sıkılaştırma:** IAM politikalarının en az yetki prensibiyle (Least Privilege) kısıtlanması, API Gateway yetkilendirmesi (Cognito/JWT) eklenmesi.
    3.  **İzleme ve Alarmlar:** Datadog veya AWS CloudWatch üzerinde dashboard'ların oluşturulması, hata ve yüksek gecikme durumunda Slack/PagerDuty alarmlarının kurulması.
    4.  **Canlıya Geçiş:** Mavi-Yeşil (Blue-Green) veya Canary Deployment stratejisi ile trafiğin canlı ortama kademeli aktarılması.
*   **Çıktılar:**
    *   Yük testi ve güvenlik denetim raporları.
    *   Canlı izleme panelleri ve aktif alarm mekanizmaları.
    *   Tamamen canlı ve çalışan Akıllı Veri Analitiği sistemi.
