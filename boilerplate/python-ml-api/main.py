import os
import logging
from contextlib import asynccontextmanager
from typing import List

import torch
import torch.nn as nn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Logger Konfigürasyonu
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PythonMLApi")

# 1. PyTorch Model Tanımı
class PredictionModel(nn.Module):
    """
    Örnek Regresyon Modeli
    Girdi: 4 Adet Öznitelik (Örn: Metrekare, Oda Sayısı, Bina Yaşı, Konum Skoru)
    Çıktı: 1 Adet Sürekli Değer (Örn: Tahmini Fiyat)
    """
    def __init__(self, input_dim: int = 4, output_dim: int = 1):
        super(PredictionModel, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, output_dim)
        )
        
    def forward(self, x):
        return self.network(x)

# Global model değişkeni
model = None
MODEL_VERSION = "v1.0.0"

# 2. FastAPI Lifespan (Yaşam Döngüsü) Yönetimi
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI uygulaması başlarken modeli bellek üzerine yükler
    ve uygulama kapanırken kaynak temizliği yapar.
    """
    global model
    logger.info("Yapay Zeka Modeli yükleniyor...")
    
    # Model nesnesini oluştur
    model = PredictionModel()
    
    # Gerçek senaryoda model ağırlıkları diskten/S3'ten yüklenir:
    # model_path = os.getenv("MODEL_PATH", "models/model.pt")
    # if os.path.exists(model_path):
    #     model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    #     logger.info(f"Model ağırlıkları yüklendi: {model_path}")
    # else:
    #     logger.warning("Model dosyası bulunamadı, varsayılan rastgele ağırlıklar kullanılacak.")
    
    model.eval() # Modeli değerlendirme (tahmin) moduna al
    logger.info("Model başarıyla hazırlandı.")
    yield
    # Uygulama durdurulduğunda temizlik işlemleri buraya yazılır
    logger.info("Uygulama kapatılıyor, kaynaklar serbest bırakıldı.")

# FastAPI Uygulama Tanımı
app = FastAPI(
    title="Akıllı Analitik Makine Öğrenmesi Servisi",
    description="PyTorch modellerini sunan yüksek performanslı FastAPI mikroservisi.",
    version=MODEL_VERSION,
    lifespan=lifespan
)

# 3. Request ve Response Şemaları (Pydantic)
class InferenceInput(BaseModel):
    features: List[float] = Field(
        ..., 
        min_items=4, 
        max_items=4, 
        example=[120.0, 3.0, 15.0, 4.5],
        description="Girdi öznitelikleri sırasıyla: [Alan (m2), Oda Sayısı, Bina Yaşı, Merkeze Uzaklık (km)]"
    )

class InferenceOutput(BaseModel):
    prediction: float = Field(..., description="Model tarafından tahmin edilen sürekli değer")
    model_version: str = Field(..., description="Tahmini yapan modelin versiyonu")

# 4. API Endpoints
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Servis ve model durumunu kontrol eder."""
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Model henüz yüklenmedi veya hazır değil."
        )
    return {"status": "healthy", "model_version": MODEL_VERSION}

@app.post("/predict", response_model=InferenceOutput, status_code=status.HTTP_200_OK)
async def predict(payload: InferenceInput):
    """
    Verilen öznitelikleri kullanarak model tahminini (Inference) gerçekleştirir.
    """
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Model hazır değil."
        )
    
    try:
        # Girdiyi Tensor formatına dönüştür
        input_tensor = torch.tensor([payload.features], dtype=torch.float32)
        
        # Gradyan hesaplamasını kapatarak tahmini gerçekleştir (Memory & Speed optimization)
        with torch.no_grad():
            output_tensor = model(input_tensor)
            prediction_val = output_tensor.item()
            
        return InferenceOutput(
            prediction=prediction_val,
            model_version=MODEL_VERSION
        )
        
    except Exception as e:
        logger.error(f"Inference sırasında hata oluştu: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference hatası: {str(e)}"
        )

# Uygulamayı başlatmak için: uvicorn main:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
