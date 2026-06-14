import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# Logger Ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BigQueryConnector")

class BigQueryConnector:
    """
    Python ile Google Cloud BigQuery arasında bağlantı kuran,
    veri okuma (sorgulama) ve yazma (insert/load) işlemlerini kolaylaştıran sınıf.
    """
    
    def __init__(self, credentials_path: Optional[str] = None):
        """
        GCP BigQuery İstemcisini (Client) başlatır.
        
        :param credentials_path: GCP Service Account JSON anahtar dosyasının yolu. 
                                 Belirtilmezse GOOGLE_APPLICATION_CREDENTIALS çevre değişkeni aranır.
        """
        if credentials_path:
            logger.info(f"Belirtilen JSON anahtarı ile BigQuery bağlantısı kuruluyor: {credentials_path}")
            self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
            self.client = bigquery.Client(credentials=self.credentials, project=self.credentials.project_id)
        else:
            logger.info("Çevre değişkenleri kullanılarak BigQuery bağlantısı kuruluyor.")
            # GOOGLE_APPLICATION_CREDENTIALS çevre değişkeni üzerinden otomatik oturum açar
            self.client = bigquery.Client()
            
    def run_query(self, query: str) -> pd.DataFrame:
        """
        Verilen SQL sorgusunu BigQuery üzerinde çalıştırır ve sonucu bir Pandas DataFrame olarak döner.
        
        :param query: Çalıştırılacak SQL sorgusu
        :return: Pandas DataFrame
        """
        try:
            logger.info("BigQuery SQL sorgusu yürütülüyor...")
            query_job = self.client.query(query)
            
            # Sorgunun bitmesini bekle ve sonucu pandas dataframe olarak al
            df = query_job.to_dataframe()
            logger.info(f"Sorgu başarıyla tamamlandı. {len(df)} satır veri çekildi.")
            return df
        except Exception as e:
            logger.error(f"Sorgu çalıştırılırken hata oluştu: {str(e)}")
            raise e

    def write_dataframe(
        self, 
        df: pd.DataFrame, 
        dataset_id: str, 
        table_id: str, 
        write_disposition: str = "WRITE_APPEND"
    ) -> bool:
        """
        Bir Pandas DataFrame'ini BigQuery tablosuna yüksek performanslı olarak yazar.
        Tablo yoksa otomatik olarak oluşturur (Auto-detect schema).
        
        :param df: Yazılacak veri (Pandas DataFrame)
        :param dataset_id: GCP BigQuery Dataset ID
        :param table_id: GCP BigQuery Table ID
        :param write_disposition: 'WRITE_TRUNCATE' (tabloyu temizle yeniden yaz), 
                                 'WRITE_APPEND' (sonuna ekle),
                                 'WRITE_EMPTY' (sadece tablo boşsa yaz)
        """
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            
            # Load Job konfigürasyonu
            job_config = bigquery.LoadJobConfig(
                # Şemayı otomatik algıla
                autodetect=True,
                # Yazma kuralları (Append, Overwrite vb.)
                write_disposition=write_disposition
            )
            
            logger.info(f"DataFrame '{dataset_id}.{table_id}' tablosuna yazılıyor...")
            job = self.client.load_table_from_dataframe(df, table_ref, job_config=job_config)
            
            # İşlemin tamamlanmasını bekle
            job.result()
            logger.info(f"DataFrame başarıyla '{dataset_id}.{table_id}' tablosuna yazıldı.")
            return True
            
        except Exception as e:
            logger.error(f"DataFrame BigQuery'ye yazılırken hata oluştu: {str(e)}")
            return False

    def insert_rows_json(self, rows: List[Dict[str, Any]], dataset_id: str, table_id: str) -> bool:
        """
        Streaming Insert yöntemiyle anlık JSON verilerini BigQuery tablosuna yazar.
        Gerçek zamanlı loglama ve anlık veri akışlarında bu yöntem tercih edilir.
        
        :param rows: [{col1: val1, col2: val2}] şeklinde sözlük listesi
        :param dataset_id: GCP BigQuery Dataset ID
        :param table_id: GCP BigQuery Table ID
        """
        try:
            table_ref = self.client.dataset(dataset_id).table(table_id)
            table = self.client.get_table(table_ref) # Tablo şemasını çek
            
            logger.info(f"{len(rows)} satır veri '{dataset_id}.{table_id}' tablosuna stream ediliyor...")
            errors = self.client.insert_rows_json(table, rows)
            
            if errors == []:
                logger.info("Veriler başarıyla BigQuery'ye aktarıldı.")
                return True
            else:
                logger.error(f"Streaming insert sırasında bazı hatalar oluştu: {errors}")
                return False
                
        except Exception as e:
            logger.error(f"Streaming insert sırasında kritik hata: {str(e)}")
            return False

# Basit Kullanım Testi
if __name__ == "__main__":
    # Bu script doğrudan çalıştırıldığında test yapar
    # Önemli: Testten önce GOOGLE_APPLICATION_CREDENTIALS çevresel değişkenini tanımlayınız.
    
    # bq = BigQueryConnector(credentials_path="path/to/key.json")
    
    # 1. Okuma Testi Örneği
    # query = "SELECT * FROM `gcp-project.dataset.table` LIMIT 10"
    # df = bq.run_query(query)
    # print(df.head())
    
    # 2. Yazma Testi Örneği
    # test_data = pd.DataFrame([{ "user_id": 1, "score": 95.5 }, { "user_id": 2, "score": 88.0 }])
    # bq.write_dataframe(test_data, "my_dataset", "my_table")
    print("BigQueryConnector modülü başarıyla derlendi. Canlı test için kimlik bilgilerinizi tanımlayıp main bloğunu aktifleştirin.")
