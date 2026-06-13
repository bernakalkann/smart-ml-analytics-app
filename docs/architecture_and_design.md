# Sistem Mimarisi ve Mikroservis Tasarımı

Bu döküman, **Python, .NET, Java, Node.js, PHP** dillerinin bir arada çalıştığı hibrit, çoklu bulut (Multi-Cloud) tabanlı **Akıllı Veri Analitiği ve Makine Öğrenmesi Uygulaması**'nın sistem mimarisini ve entegrasyon stratejisini açıklar.

---

## 1. Çoklu Dil (Multi-Language) Rol Dağılımı ve Görevleri

Sistemde kullanılan her programlama dili, en güçlü olduğu uzmanlık alanına göre konumlandırılmıştır:

| Teknoloji / Dil | Sistemdeki Rolü | Konumlandırıldığı Katman | Neden Tercih Edildi? |
| :--- | :--- | :--- | :--- |
| **Node.js (Express/NestJS)** | API Gateway, Kimlik Doğrulama (Auth), Gerçek Zamanlı (Websocket) İletişim | Dışa Açık Katman (Frontend-Facing) | I/O yoğun işlerde yüksek asenkron performans ve zengin ekosistem. |
| **PHP (Laravel/Symfony)** | Yönetim Paneli, Raporlama Arayüzleri, Back-office İşlemleri | Sunucu Taraflı Arayüz (SSR) | Hızlı geliştirme süresi, güçlü ORM (Eloquent) ve kurumsal CMS özellikleri. |
| **Python (FastAPI)** | Model Eğitimi, ML Çıkarım (Inference) Servisi, ETL & BigQuery Bağlantıları | AI / ML Çekirdek Katmanı | PyTorch, TensorFlow ve Scikit-learn kütüphaneleriyle doğrudan entegrasyon. |
| **.NET (C# / ML.NET)** | Kurumsal Raporlama, Finansal/Tablo Veri Analitiği, ML.NET Servisleri | İş Mantığı (Enterprise Logic) | Güçlü tip güvenliği, yüksek bellek performansı ve Azure ekosistemiyle uyum. |
| **Java (Spring Boot)** | Büyük Veri İşleme (ETL), Kuyruk Tüketimi (Kafka), Veritabanı Senkronizasyonu | Veri Entegrasyon Katmanı | Enterprise-grade kararlılık, gelişmiş çoklu iş parçacığı (multithreading) yönetimi. |

---

## 2. Mikroservisler Arası İletişim Protokolleri

Mikroservisler birbirleriyle iki temel yöntemle haberleşir:

1. **Senkron İletişim (gRPC & REST):**
   * **gRPC (Protocol Buffers):** Düşük gecikmeli ve yüksek performanslı veri iletimi gerektiren durumlarda kullanılır. Örneğin, *Node.js API Gateway* veya *Java ETL Servisi*, *Python ML Servisi*'nden anlık tahmin isterken gRPC kullanır.
   * **REST (HTTP/2 JSON):** Dış istemciler ve yönetici paneli (PHP) ile yapılan entegrasyonlarda tercih edilir.
   
2. **Asenkron İletişim (Event-Driven - Kafka/RabbitMQ):**
   * Tahmin sonuçlarının loglanması, BigQuery veri ambarına aktarılması ve model yeniden eğitim (retraining) tetikleyicileri asenkron mesaj kuyrukları üzerinden yönetilir.

```mermaid
graph TD
    %% Clients
    Client[İstemci - Web/Mobil] -->|HTTP/Websocket| NodeGW[Node.js API Gateway]
    Admin[Yönetici Paneli] -->|HTTP| PHPPole[PHP Laravel Server]

    %% Internal Microservices
    subgraph "Kurumsal Mikroservis Ağı"
        NodeGW -->|gRPC - Hızlı Tahmin| PyML[Python FastAPI ML API]
        NodeGW -->|REST/gRPC| DotNetService[.NET Enterprise Core]
        PHPPole -->|REST/gRPC| DotNetService
        DotNetService -->|gRPC| JavaService[Java Spring Boot ETL]
    end

    %% Event Broker
    NodeGW -->|Yazma İstekleri| Kafka{Apache Kafka Event Broker}
    JavaService -->|Büyük Veri Akışı| Kafka
    PyML -->|Tahmin Logları| Kafka

    %% Databases
    subgraph "Veri ve Depolama Katmanı"
        DotNetService -->|SQL| PG[(PostgreSQL)]
        NodeGW -->|NoSQL| Mongo[(MongoDB)]
        Kafka -->|Consumer ETL| BQ[(Google Cloud BigQuery)]
    end
```

---

## 3. Çoklu Bulut (Multi-Cloud) Servis Dağılım Haritası

Sistemin AWS, GCP ve Azure üzerindeki en mantıklı dağılımı aşağıdaki gibidir. Bu yapı, her bulut sağlayıcısının en avantajlı olduğu servisleri (GCP BigQuery, AWS SageMaker/Lambda, Azure AD) tek mimaride birleştirir.

```mermaid
graph TB
    subgraph "AWS - Uygulama ve Sunucusuz Katman"
        Lambda[AWS Lambda - Node.js Gateway]
        SageMaker[AWS SageMaker - Python ML Inference]
        RDS[(AWS RDS - PostgreSQL)]
    end

    subgraph "Google Cloud (GCP) - Büyük Veri ve Analitik"
        BigQuery[(GCP BigQuery Data Warehouse)]
        VertexAI[GCP Vertex AI - Model Pipelines]
    end

    subgraph "Azure - Kurumsal Mantık ve .NET"
        AzureML[Azure ML Service - ML.NET]
        AppService[Azure App Service - .NET Core & PHP]
        CosmosDB[(Azure CosmosDB - MongoDB API)]
    end

    %% Cloud-to-Cloud Integration
    Lambda -->|Private Link / VPC Peering| RDS
    Lambda -->|gRPC / HTTPS| SageMaker
    AppService -->|Hybrid Connection| AzureML
    Lambda -->|Cross-Cloud API| BigQuery
    VertexAI -->|Data Link| BigQuery
    JavaService -->|Ingest| BigQuery
```

### Bulut Sağlayıcı Dağılım Tercih Nedenleri:
*   **GCP:** BigQuery, analitik sorgularda ve veri ambarı operasyonlarında sektör standardıdır. ML modellerini besleyecek büyük veri analizleri burada gerçekleşir.
*   **AWS:** SageMaker ve AWS Lambda sunucusuz API dağıtımı, hızlı ölçeklenme ve operasyonel maliyet avantajı sağlar.
*   **Azure:** Kurumsal .NET servisleri ve aktif dizin (Active Directory) entegrasyonu için en güvenli ve yerel ortamı sunar. ML.NET modelleri Azure ML ile sorunsuz bir şekilde yönetilir.
