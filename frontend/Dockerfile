# 使用 Node.js 18 作為基礎映像
FROM node:18-alpine

# 設置工作目錄
WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製所有前端程式碼
COPY . .

# 構建生產版本
RUN npm run build

# 驗證 dist 目錄是否存在
RUN ls -la dist

# 安裝 serve 來提供靜態檔案
RUN npm install -g serve

# 暴露端口（生產環境使用 5000）
EXPOSE 5000

# 啟動生產伺服器
CMD ["serve", "-s", "dist", "-l", "5000"]