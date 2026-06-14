/**
 * Express.js API Gateway Şablonu
 * 
 * Bu mikroservis, istemciden (Frontend/Mobil) gelen tahmin isteklerini karşılar,
 * girdi doğrulaması yapar ve ardından asıl tahmini üretecek olan Python ML API'sine
 * giden HTTP/REST isteğini yönetir.
 */

const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json());

// Çevre Değişkenleri
const PORT = process.env.PORT || 3000;
const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';

/**
 * 1. Health Check Endpoint
 */
app.get('/health', async (req, res) => {
    try {
        // Python ML Servisinin sağlık durumunu kontrol et
        const mlHealth = await axios.get(`${ML_API_URL}/health`, { timeout: 3000 });
        return res.status(200).json({
            status: "UP",
            gateway: "healthy",
            ml_service: mlHealth.data
        });
    } catch (error) {
        return res.status(503).json({
            status: "DOWN",
            gateway: "healthy",
            ml_service: "UNREACHABLE",
            details: error.message
        });
    }
});

/**
 * 2. Tahmin İsteklerini Yönlendiren Endpoint
 * POST /api/predict
 */
app.post('/api/predict', async (req, res) => {
    const { features } = req.body;

    // A. Temel Girdi Doğrulaması (Validation)
    if (!features || !Array.isArray(features)) {
        return res.status(400).json({
            error: "Geçersiz İstek Şeması",
            message: "'features' alanı zorunludur ve bir dizi (array) olmalıdır."
        });
    }

    if (features.length !== 4) {
        return res.status(400).json({
            error: "Geçersiz Boyut",
            message: "'features' dizisi tam olarak 4 sayısal değer içermelidir: [Alan, Oda Sayısı, Yaş, Uzaklık]"
        });
    }

    // Her elemanın sayı olduğunu kontrol et
    const allNumbers = features.every(num => typeof num === 'number');
    if (!allNumbers) {
        return res.status(400).json({
            error: "Geçersiz Tip",
            message: "Tüm 'features' elemanları sayı (float/integer) olmalıdır."
        });
    }

    // B. Python ML API'sine Yönlendirme
    try {
        console.log(`[Gateway] Python ML Servisine istek atılıyor: ${ML_API_URL}/predict`);
        
        const response = await axios.post(`${ML_API_URL}/predict`, {
            features: features
        }, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 5000 // 5 saniye zaman aşımı
        });

        // C. Tahmin Sonucunu İstemciye İletme
        return res.status(200).json({
            success: true,
            data: response.data
        });

    } catch (error) {
        console.error(`[Gateway Hata] ML Servisi çağrılamadı: ${error.message}`);
        
        if (error.response) {
            // ML servisinden gelen hata (4xx, 5xx)
            return res.status(error.response.status).json({
                success: false,
                error: "ML Servis Hatası",
                details: error.response.data
            });
        } else if (error.request) {
            // ML servisine ulaşılamadı (Network/Timeout)
            return res.status(504).json({
                success: false,
                error: "Gateway Timeout",
                message: "Python ML API servisinden zamanında yanıt alınamadı."
            });
        } else {
            // Diğer beklenmeyen hatalar
            return res.status(500).json({
                success: false,
                error: "Dahili Gateway Hatası",
                message: error.message
            });
        }
    }
});

// Sunucuyu Başlat
app.listen(PORT, () => {
    console.log(`[Gateway] Node.js Express Sunucusu çalışıyor: http://localhost:${PORT}`);
    console.log(`[Gateway] Hedef Python ML Servisi: ${ML_API_URL}`);
});
