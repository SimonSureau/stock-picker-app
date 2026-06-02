from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from scorer import calculate_score

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

# Route 4: Score a single stock
@app.get("/score/{ticker}")
def get_score(ticker: str):
    stock = yf.Ticker(ticker.upper())
    info = stock.info
    if not info.get("currentPrice"):
        raise HTTPException(status_code=404, detail="Ticker not found")
    score_data = calculate_score(info)
    return {
        "ticker": ticker.upper(),
        "name": info.get("longName"),
        "sector": info.get("sector"),
        "price": info.get("currentPrice"),
        **score_data
    }

# Route 5: Screen multiple stocks at once
@app.post("/screen")
def screen_stocks(tickers: list[str]):
    results = []
    for ticker in tickers[:10]:  # max 10 at a time
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            if info.get("currentPrice"):
                score_data = calculate_score(info)
                results.append({
                    "ticker": ticker.upper(),
                    "name": info.get("longName"),
                    "sector": info.get("sector"),
                    "price": info.get("currentPrice"),
                    **score_data
                })
        except:
            pass  # skip any tickers that fail
    # Sort by score, highest first
    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results