from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
import sys
import math
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# Add vnstock-agent to path
for _candidate in ['/app/vnstock_agent', '/home/hoang/vnstock-agent/src/vnstock_agent']:
    if _candidate not in sys.path:
        sys.path.insert(0, _candidate)

from vnstock_agent.core import (
    stock_history,
    stock_intraday,
    stock_price_depth,
    company_overview,
    company_shareholders,
    company_officers,
    company_news,
    company_events,
    financial_balance_sheet,
    financial_income_statement,
    financial_cash_flow,
    financial_ratio,
    listing_all_symbols,
    listing_symbols_by_group,
    listing_symbols_by_exchange,
    listing_industries,
    trading_price_board,
)

app = FastAPI(title="VN Research API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


def safe_call(fn, *args, **kwargs):
    try:
        result = fn(*args, **kwargs)
        if hasattr(result, 'to_dict'):
            return result.to_dict()
        elif hasattr(result, 'to_json'):
            return json.loads(result.to_json())
        elif hasattr(result, 'to_records'):
            return result.to_records()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/symbols")
async def get_symbols(source: str = "VCI"):
    data = safe_call(listing_all_symbols, source=source)
    return {"data": data}


@app.get("/api/symbols/group/{group}")
async def get_symbols_by_group(group: str, source: str = "VCI"):
    data = safe_call(listing_symbols_by_group, group=group.upper(), source=source)
    return {"data": data}


EXCHANGE_ALIASES = {
    "HOSE": "HSX",
    "HSX": "HSX",
    "HNX": "HNX",
    "UPCOM": "UPCOM",
}


@app.get("/api/symbols/exchange/{exchange}")
async def get_symbols_by_exchange(exchange: str, source: str = "VCI"):
    target = EXCHANGE_ALIASES.get(exchange.upper(), exchange.upper())
    data = safe_call(listing_symbols_by_exchange, source=source)
    filtered = [
        row for row in data
        if str(row.get("exchange", "")).upper() == target
        and str(row.get("type", "")).upper() == "STOCK"
    ]
    return {"data": filtered}


@app.get("/api/industries")
async def get_industries(source: str = "VCI"):
    data = safe_call(listing_industries, source=source)
    return {"data": data}


@app.get("/api/stock/{symbol}/history")
async def get_stock_history(symbol: str, start: str = None, end: str = None, interval: str = "1D", source: str = "VCI"):
    data = safe_call(stock_history, symbol, start, end, interval, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/intraday")
async def get_stock_intraday(symbol: str, page_size: int = 100, source: str = "VCI"):
    data = safe_call(stock_intraday, symbol, page_size, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/depth")
async def get_stock_depth(symbol: str, source: str = "VCI"):
    data = safe_call(stock_price_depth, symbol, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/price-board")
async def get_price_board(symbols: str, source: str = "VCI"):
    symbol_list = [s.strip() for s in symbols.split(",")]
    data = safe_call(trading_price_board, symbol_list, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/overview")
async def get_company_overview(symbol: str, source: str = "VCI"):
    data = safe_call(company_overview, symbol, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/shareholders")
async def get_shareholders(symbol: str, source: str = "VCI"):
    data = safe_call(company_shareholders, symbol, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/officers")
async def get_officers(symbol: str, source: str = "VCI"):
    data = safe_call(company_officers, symbol, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/news")
async def get_company_news(symbol: str, source: str = "VCI"):
    data = safe_call(company_news, symbol, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/events")
async def get_company_events(symbol: str, source: str = "VCI"):
    data = safe_call(company_events, symbol, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/financials/balance-sheet")
async def get_balance_sheet(symbol: str, period: str = "quarter", source: str = "VCI"):
    data = safe_call(financial_balance_sheet, symbol, period, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/financials/income")
async def get_income_statement(symbol: str, period: str = "quarter", source: str = "VCI"):
    data = safe_call(financial_income_statement, symbol, period, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/financials/cashflow")
async def get_cash_flow(symbol: str, period: str = "quarter", source: str = "VCI"):
    data = safe_call(financial_cash_flow, symbol, period, source)
    return {"data": data}


@app.get("/api/stock/{symbol}/financials/ratios")
async def get_financial_ratios(symbol: str, period: str = "quarter", source: str = "VCI"):
    data = safe_call(financial_ratio, symbol, period, source)
    return {"data": data}


@app.get("/dashboard")
async def standalone_dashboard():
    path = Path(__file__).parent.parent / "frontend" / "standalone.html"
    if not path.exists():
        raise HTTPException(status_code=404, detail="standalone.html not found")
    return FileResponse(path)


# ---------- Technical Indicators ----------

def _normalize_history(data):
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    if df.empty:
        return df
    if "time" in df.columns:
        df = df.rename(columns={"time": "date"})
    if "date" not in df.columns:
        df["date"] = df.index
    df = df.sort_values("date").reset_index(drop=True)
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            return pd.DataFrame()
    return df


def _round(val, ndigits=2):
    try:
        return round(float(val), ndigits)
    except Exception:
        return None


def _compute_indicators(df: pd.DataFrame):
    close = df["close"].astype(float)
    high = df["high"].astype(float)
    low = df["low"].astype(float)
    volume = df["volume"].astype(float)

    df["ma20"] = close.rolling(window=20, min_periods=1).mean().round(2)
    df["ma50"] = close.rolling(window=50, min_periods=1).mean().round(2)
    df["ma200"] = close.rolling(window=200, min_periods=1).mean().round(2)

    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window=14, min_periods=1).mean()
    avg_loss = loss.rolling(window=14, min_periods=1).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    df["rsi"] = (100 - 100 / (1 + rs)).round(2)

    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = (ema12 - ema26).round(2)
    signal = macd_line.ewm(span=9, adjust=False).mean().round(2)
    df["macd"] = macd_line
    df["signal"] = signal
    df["macd_hist"] = (macd_line - signal).round(2)

    tp = (high + low + close) / 3.0
    mf = tp * volume
    pos_mf = mf.where(tp > tp.shift(1), 0.0)
    neg_mf = mf.where(tp < tp.shift(1), 0.0)
    pos_sum = pos_mf.rolling(window=14, min_periods=1).sum()
    neg_sum = neg_mf.rolling(window=14, min_periods=1).sum()
    df["mfi"] = (100 - 100 / (1 + pos_sum / neg_sum.replace(0, np.nan))).round(2)

    df["volume_ma20"] = volume.rolling(window=20, min_periods=1).mean().round(2)
    df["volume_ratio"] = (volume / df["volume_ma20"].replace(0, np.nan)).round(2)

    window = 20
    recent = df.tail(window)
    resistance = float(recent["high"].max())
    support = float(recent["low"].min())
    last = float(close.iloc[-1]) if len(close) else None

    df["breakout"] = None
    if last is not None:
        if last >= resistance:
            df.loc[df.index[-1], "breakout"] = "breakout"
        elif last <= support:
            df.loc[df.index[-1], "breakout"] = "breakdown"

    return df


def _find_divergence(df: pd.DataFrame):
    result = {"regular_bullish": False, "regular_bearish": False, "hidden_bullish": False, "hidden_bearish": False}
    if len(df) < 30:
        return result
    recent = df.tail(20)
    price_lows = recent["low"].nsmallest(3).sort_index()
    price_highs = recent["high"].nlargest(3).sort_index()
    rsi_lows = recent["rsi"].loc[price_lows.index]
    rsi_highs = recent["rsi"].loc[price_highs.index]
    if len(price_lows) >= 2:
        p1, p2 = float(price_lows.iloc[0]), float(price_lows.iloc[-1])
        r1, r2 = float(rsi_lows.iloc[0]), float(rsi_lows.iloc[-1])
        if p2 < p1 and r2 > r1:
            result["regular_bullish"] = True
        if p2 > p1 and r2 < r1:
            result["hidden_bullish"] = True
    if len(price_highs) >= 2:
        p1, p2 = float(price_highs.iloc[0]), float(price_highs.iloc[-1])
        r1, r2 = float(rsi_highs.iloc[0]), float(rsi_highs.iloc[-1])
        if p2 > p1 and r2 < r1:
            result["regular_bearish"] = True
        if p2 < p1 and r2 > r1:
            result["hidden_bearish"] = True
    return result


def _money_flow_signal(df: pd.DataFrame):
    result = {
        "obv_trend": "neutral",
        "mfi_signal": "neutral",
        "volume_signal": "neutral",
        "flow_strength": 0,
    }
    if len(df) < 10:
        return result
    close = df["close"].astype(float)
    volume = df["volume"].astype(float)
    obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
    obv_ma = pd.Series(obv).rolling(window=20, min_periods=1).mean()
    result["obv_trend"] = "inflow" if float(obv.iloc[-1]) > float(obv_ma.iloc[-1]) else "outflow"
    mfi = float(df["mfi"].iloc[-1])
    if mfi > 80:
        result["mfi_signal"] = "overbought"
    elif mfi < 20:
        result["mfi_signal"] = "oversold"
    else:
        result["mfi_signal"] = "neutral"
    vol_ratio = float(df["volume_ratio"].iloc[-1])
    if vol_ratio > 1.5:
        result["volume_signal"] = "high"
    elif vol_ratio < 0.6:
        result["volume_signal"] = "low"
    else:
        result["volume_signal"] = "normal"
    result["flow_strength"] = int(min(100, max(0, round((mfi / 100) * 50 + vol_ratio * 25 + (50 if result["obv_trend"] == "inflow" else 0)))))
    return result


@app.get("/api/stock/{symbol}/indicators")
async def get_indicators(symbol: str, start: str = None, end: str = None, source: str = "VCI"):
    try:
        history = safe_call(stock_history, symbol, start, end, "1D", source)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    data = history.get("data") if isinstance(history, dict) else history
    if not data:
        return {"summary": {}, "history": []}
    df = _normalize_history(data)
    if df.empty:
        return {"summary": {}, "history": []}
    df = _compute_indicators(df)
    latest = df.tail(1)
    divergence = _find_divergence(df)
    flow = _money_flow_signal(df)

    support = float(df["low"].tail(20).min())
    resistance = float(df["high"].tail(20).max())

    latest_snapshot = {
        "date": str(latest["date"].iloc[0]) if "date" in latest.columns else None,
        "close": _round(latest["close"].iloc[0]),
        "ma20": _round(latest["ma20"].iloc[0]),
        "ma50": _round(latest["ma50"].iloc[0]),
        "ma200": _round(latest["ma200"].iloc[0]),
        "rsi": _round(latest["rsi"].iloc[0]),
        "macd": _round(latest["macd"].iloc[0]),
        "signal": _round(latest["signal"].iloc[0]),
        "macd_hist": _round(latest["macd_hist"].iloc[0]),
        "mfi": _round(latest["mfi"].iloc[0]),
        "volume_ratio": _round(latest["volume_ratio"].iloc[0], 2),
        "breakout": latest["breakout"].iloc[0] if "breakout" in latest.columns else None,
    }

    if latest_snapshot["close"] is not None:
        if latest_snapshot["close"] >= resistance:
            latest_snapshot["level_signal"] = "breakout"
        elif latest_snapshot["close"] <= support:
            latest_snapshot["level_signal"] = "breakdown"
        elif latest_snapshot["close"] > latest_snapshot.get("ma20") and latest_snapshot.get("ma20", 0) > latest_snapshot.get("ma50", 0):
            latest_snapshot["level_signal"] = "uptrend"
        elif latest_snapshot["close"] < latest_snapshot.get("ma20") and latest_snapshot.get("ma20", 0) < latest_snapshot.get("ma50", 0):
            latest_snapshot["level_signal"] = "downtrend"
        else:
            latest_snapshot["level_signal"] = "sideway"

    summary = {
        "symbol": symbol,
        "support": _round(support),
        "resistance": _round(resistance),
        "latest": latest_snapshot,
        "divergence": divergence,
        "money_flow": flow,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
    tail = df.tail(90)
    hist = []
    for _, row in tail.iterrows():
        hist.append({
            "date": str(row.get("date")),
            "open": _round(row.get("open")),
            "high": _round(row.get("high")),
            "low": _round(row.get("low")),
            "close": _round(row.get("close")),
            "volume": int(row.get("volume")) if pd.notna(row.get("volume")) else None,
            "ma20": _round(row.get("ma20")),
            "ma50": _round(row.get("ma50")),
            "ma200": _round(row.get("ma200")),
            "rsi": _round(row.get("rsi")),
            "macd": _round(row.get("macd")),
            "macd_hist": _round(row.get("macd_hist")),
            "mfi": _round(row.get("mfi")),
            "volume_ratio": _round(row.get("volume_ratio"), 2),
        })
    return {"summary": summary, "history": hist}


# Mount built React frontend AFTER all API routes
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8900)
