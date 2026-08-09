from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os
import sys
from pathlib import Path

# Add vnstock-agent to path
sys.path.insert(0, '/home/hoang/vnstock-agent/src')

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

app = FastAPI(title="VN Research API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/symbols")
async def get_symbols(source: str = "VCI"):
    data = safe_call(listing_all_symbols, source=source)
    return {"data": data}


@app.get("/api/symbols/group/{group}")
async def get_symbols_by_group(group: str, source: str = "VCI"):
    data = safe_call(listing_symbols_by_group, group=group.upper(), source=source)
    return {"data": data}


@app.get("/api/symbols/exchange/{exchange}")
async def get_symbols_by_exchange(exchange: str, source: str = "VCI"):
    data = safe_call(listing_symbols_by_exchange, exchange=exchange.upper(), source=source)
    return {"data": data}


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8900)
