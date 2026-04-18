# 部署到雲端平台

本指南說明如何將交易機器人儀表板部署到 Render.com 或 Railway.app。

## 方案 1: Render.com（推薦）

### 優點
- 完全免費
- 支持 WebSocket
- 自動 HTTPS
- 從 GitHub 自動部署

### 部署步驟

1. **註冊 Render 帳號**
   - 訪問 https://render.com
   - 使用 GitHub 帳號登錄

2. **創建新的 Web Service**
   - 點擊 "New +" → "Web Service"
   - 連接你的 GitHub 倉庫：`CryptoagentbeA9/trading-bot`
   - 選擇分支：`main`

3. **配置服務**
   - Name: `binance-trading-bot`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt && pip install -r requirements_dashboard.txt`
   - Start Command: `python run_dashboard.py`
   - Plan: `Free`

4. **設置環境變量**
   點擊 "Environment" 標籤，添加：
   ```
   BINANCE_API_KEY=你的API密鑰
   BINANCE_API_SECRET=你的API密鑰
   BINANCE_TESTNET=true
   PORT=10000
   ```

5. **部署**
   - 點擊 "Create Web Service"
   - 等待部署完成（約 3-5 分鐘）
   - 獲取你的 URL：`https://binance-trading-bot-xxxx.onrender.com`

### 注意事項
- 免費方案會在 15 分鐘無活動後休眠
- 首次訪問可能需要 30 秒喚醒
- 支持自定義域名

---

## 方案 2: Railway.app

### 優點
- 簡單易用
- 每月 $5 免費額度
- 快速部署

### 部署步驟

1. **註冊 Railway 帳號**
   - 訪問 https://railway.app
   - 使用 GitHub 帳號登錄

2. **創建新項目**
   - 點擊 "New Project"
   - 選擇 "Deploy from GitHub repo"
   - 選擇 `CryptoagentbeA9/trading-bot`

3. **配置環境變量**
   點擊項目 → Variables，添加：
   ```
   BINANCE_API_KEY=你的API密鑰
   BINANCE_API_SECRET=你的API密鑰
   BINANCE_TESTNET=true
   ```

4. **部署**
   - Railway 會自動檢測 Python 項目
   - 自動安裝依賴並啟動
   - 獲取你的 URL：`https://xxxx.up.railway.app`

### 注意事項
- 免費額度用完後需要付費
- 自動 HTTPS 和自定義域名
- 支持 WebSocket

---

## 配置文件說明

### Procfile
定義啟動命令：
```
web: python run_dashboard.py
```

### render.yaml
Render 部署配置，包含：
- Python 版本
- 構建命令
- 啟動命令
- 環境變量

### railway.json
Railway 部署配置，包含：
- 構建器設置
- 啟動命令
- 重啟策略

---

## 環境變量說明

| 變量名 | 說明 | 必需 |
|--------|------|------|
| `BINANCE_API_KEY` | 幣安 API 密鑰 | 是 |
| `BINANCE_API_SECRET` | 幣安 API 密鑰 | 是 |
| `BINANCE_TESTNET` | 是否使用測試網 | 否（默認 false） |
| `PORT` | 服務器端口 | 否（Render 自動設置） |

---

## 測試部署

部署完成後，訪問你的 URL：
- 應該看到即時儀表板
- WebSocket 連接應該正常（右上角顯示"已連接"）
- 可以看到帳戶餘額、持倉、交易記錄等

---

## 故障排除

### 部署失敗
- 檢查 requirements.txt 是否包含所有依賴
- 查看部署日誌找出錯誤

### WebSocket 無法連接
- 確認平台支持 WebSocket（Render 和 Railway 都支持）
- 檢查防火牆設置

### API 錯誤
- 確認環境變量設置正確
- 檢查 API 密鑰權限

---

## 本地測試

部署前可以本地測試：
```bash
# 安裝依賴
pip install -r requirements.txt
pip install -r requirements_dashboard.txt

# 設置環境變量
export BINANCE_API_KEY=你的密鑰
export BINANCE_API_SECRET=你的密鑰
export BINANCE_TESTNET=true

# 啟動
python run_dashboard.py
```

訪問 http://localhost:5000

---

## 安全建議

1. **不要提交 .env 文件到 Git**
2. **使用測試網進行測試**（BINANCE_TESTNET=true）
3. **限制 API 密鑰權限**（只給交易和查詢權限）
4. **定期更換 API 密鑰**
5. **監控異常活動**

---

## 更新部署

### Render
- 推送代碼到 GitHub
- Render 自動重新部署

### Railway
- 推送代碼到 GitHub
- Railway 自動重新部署

---

## 成本估算

### Render（免費方案）
- ✅ 完全免費
- ⚠️ 15 分鐘無活動後休眠
- ⚠️ 每月 750 小時運行時間

### Railway（免費額度）
- ✅ 每月 $5 免費額度
- ✅ 不會休眠
- ⚠️ 超出後按使用量計費

---

## 推薦配置

**開發/測試**: Render 免費方案
**生產環境**: Railway 付費方案（更穩定）

---

需要幫助？查看：
- Render 文檔: https://render.com/docs
- Railway 文檔: https://docs.railway.app
