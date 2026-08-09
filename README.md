# VN Research

Dashboard phân tích chứng khoán Việt Nam với chỉ báo kỹ thuật.

## Chạy local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cd backend && python app.py
```

Mở `http://localhost:8900/dashboard`

## Deploy

### Option A: Cloudflare Named Tunnel

```bash
# 1. Login Cloudflare
cloudflared tunnel login

# 2. Create named tunnel
cloudflared tunnel create vn-research

# 3. Route DNS
cloudflared tunnel route dns vn-research vn-research.hoangphuc1809.workers.dev

# 4. Run tunnel
cloudflared tunnel run vn-research
```

### Option B: Render

Push repo lên GitHub, kết nối Render, deploy với Dockerfile.

## API

- `GET /api/symbols/group/VN30`
- `GET /api/stock/{symbol}/history?start=2025-01-01&end=2025-12-31`
- `GET /api/stock/{symbol}/indicators?start=2025-01-01&end=2025-12-31`
- `GET /api/stock/{symbol}/overview`
- `GET /dashboard` - Standalone dashboard

## Chỉ báo kỹ thuật

- Hỗ trợ / Kháng cự (20 ngày)
- MA20, MA50, MA200
- RSI(14), MACD, MFI(14)
- Volume ratio
- Breakout/Breakdown
- Phân kỳ RSI
- Dòng tiền: OBV trend, MFI signal, volume signal
