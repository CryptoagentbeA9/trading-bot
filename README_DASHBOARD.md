# 交易機器人即時監控面板

## 功能特性

### 即時數據更新
- ✅ WebSocket 連接，每 2 秒自動更新
- ✅ 即時交易狀態顯示
- ✅ 當前持倉和盈虧
- ✅ 最近交易記錄
- ✅ 帳戶餘額監控
- ✅ 正在監控的漲幅榜幣種
- ✅ 交易信號和系統警報
- ✅ 系統健康狀態

### 視覺化圖表
- 📈 累計盈虧曲線圖 (Chart.js)
- 📊 即時價格變動
- 💹 盈虧百分比顯示

### 響應式設計
- 📱 支持手機瀏覽
- 💻 桌面端優化
- 🎨 深色主題界面

## 安裝依賴

```bash
pip install -r requirements_dashboard.txt
```

## 啟動方式

### 方法 1: 使用啟動腳本（推薦）

```bash
python run_dashboard.py
```

### 方法 2: 整合到現有交易機器人

```python
from dashboard_realtime import RealtimeDashboard
from binance_client import BinanceClient
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem
from strategy_engine import StrategyEngine
from strategy_config import StrategyConfig

# 初始化組件
client = BinanceClient(testnet=True)
metrics_tracker = MetricsTracker()
alerting_system = AlertingSystem()
strategy_config = StrategyConfig()
strategy_engine = StrategyEngine(client, strategy_config)

# 創建並啟動儀表板
dashboard = RealtimeDashboard(
    metrics_tracker=metrics_tracker,
    alerting_system=alerting_system,
    strategy_engine=strategy_engine,
    binance_client=client,
    port=5000
)

# 在背景執行緒運行
dashboard.run(debug=False)
```

## 訪問地址

- 本地訪問: http://localhost:5000
- 網絡訪問: http://0.0.0.0:5000
- 手機訪問: http://[你的電腦IP]:5000

## 配置文件

編輯 `config_dashboard.json` 自定義設置：

```json
{
  "dashboard": {
    "port": 5000,
    "update_interval_seconds": 2
  },
  "display": {
    "max_trades_display": 20,
    "max_alerts_display": 50
  }
}
```

## API 端點

### REST API
- `GET /api/status` - 機器人狀態
- `GET /api/metrics` - 交易指標
- `GET /api/balance` - 帳戶餘額
- `GET /api/positions` - 當前持倉
- `GET /api/trades` - 最近交易
- `GET /api/alerts` - 系統警報
- `GET /api/gainers` - 漲幅榜
- `GET /api/chart-data` - 圖表數據

### WebSocket 事件
- `connect` - 客戶端連接
- `disconnect` - 客戶端斷開
- `request_update` - 請求更新
- `dashboard_update` - 儀表板數據推送

## 技術架構

- **後端**: Flask + Flask-SocketIO
- **前端**: 原生 JavaScript + Socket.IO Client
- **圖表**: Chart.js
- **即時通信**: WebSocket
- **樣式**: 自定義 CSS (響應式設計)

## 安全建議

1. 在生產環境中使用 HTTPS
2. 設置防火牆規則限制訪問
3. 使用強密碼保護
4. 定期更新依賴包

## 故障排除

### 端口被占用
修改 `config_dashboard.json` 中的 `port` 設置

### WebSocket 連接失敗
檢查防火牆設置，確保端口開放

### 數據不更新
檢查後端服務是否正常運行，查看控制台日誌

## 截圖預覽

儀表板包含以下區塊：
- 📊 關鍵指標卡片（狀態、餘額、交易次數、勝率、盈虧）
- 📈 盈虧曲線圖表
- 💼 當前持倉列表
- 🔥 監控中的漲幅榜
- 📊 最近交易記錄
- 🔔 系統警報通知
