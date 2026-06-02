from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf

# Create the app
app = FastAPI(title="Stock Picker API")

# Allow your React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Route 1: Get a current stock quote
@app.get("/quote/{ticker}")
def get_quote(ticker: str):
    stock = yf.Ticker(ticker.upper())
    info = stock.info
    if not info.get("currentPrice"):
        raise HTTPException(status_code=404, detail="Ticker not found")
    return {
        "ticker": ticker.upper(),
        "name": info.get("longName"),
        "price": info.get("currentPrice"),
        "change_percent": info.get("regularMarketChangePercent"),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "volume": info.get("volume"),
    }

# Route 2: Get price history for a chart
@app.get("/history/{ticker}")
def get_history(ticker: str, period: str = "1y"):
    stock = yf.Ticker(ticker.upper())
    hist = stock.history(period=period)
    if hist.empty:
        raise HTTPException(status_code=404, detail="Ticker not found")
    return {
        "ticker": ticker.upper(),
        "prices": [
            {"date": str(date.date()), "close": round(row["Close"], 2)}
            for date, row in hist.iterrows()
        ]
    }

# Route 3: Get key financials
@app.get("/financials/{ticker}")
def get_financials(ticker: str):
    stock = yf.Ticker(ticker.upper())
    info = stock.info
    if not info.get("currentPrice"):
        raise HTTPException(status_code=404, detail="Ticker not found")
    return {
        "ticker": ticker.upper(),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
        "revenue": info.get("totalRevenue"),
        "debt_to_equity": info.get("debtToEquity"),
        "profit_margin": info.get("profitMargins"),
        "sector": info.get("sector"),
    }