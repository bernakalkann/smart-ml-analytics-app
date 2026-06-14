# Node.js 18 alpine tabanlı hafif imaj kullan
FROM node:18-alpine

# Çalışma dizinini oluştur
WORKDIR /app

# Bağımlılık tanımlarını kopyala
COPY package*.json ./

# Bağımlılıkları kur
RUN npm install --production

# Kalan tüm dosyaları kopyala
COPY . .

# Gateway varsayılan portunu aç
EXPOSE 3000

# Gateway'i başlat
CMD ["npm", "start"]
