from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import concurrent.futures
import yfinance as yf
import time
from scorer import calculate_score
from fund_scorer import calculate_fund_score
from backtester import run_backtest
from sentiment import get_combined_sentiment

# Cache SPY benchmark data for 1 hour to avoid fetching on every request
_sp500_cache: dict = {"data": None, "ts": 0.0}

def get_sp500_benchmark() -> dict:
    if time.time() - _sp500_cache["ts"] < 3600 and _sp500_cache["data"]:
        return _sp500_cache["data"]
    # Hard 8-second timeout — a slow or blocked Yahoo Finance response
    # must never hang a user request.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(lambda: yf.Ticker("SPY").info)
        try:
            spy_info = future.result(timeout=8)
            _sp500_cache["data"] = {
                "52wk_change": spy_info.get("52WeekChange"),
                "3yr_return":  spy_info.get("threeYearAverageReturn"),
            }
        except Exception:
            _sp500_cache["data"] = {"52wk_change": None, "3yr_return": None}
    _sp500_cache["ts"] = time.time()
    return _sp500_cache["data"]

# Create the app
app = FastAPI(title="Stock Picker API")

# Allow your React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check — no yfinance, instant response
@app.get("/health")
def health():
    return {"status": "ok"}

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
        "dividend_yield": info.get("dividendYield") or info.get("trailingAnnualDividendYield"),
        "dividend_rate": info.get("dividendRate"),
        "payout_ratio": info.get("payoutRatio"),
        "ex_dividend_date": info.get("exDividendDate"),
    }

# Route 4: Score a single stock
@app.get("/score/{ticker}")
def get_score(ticker: str):
    stock = yf.Ticker(ticker.upper())
    info = stock.info
    if not info.get("currentPrice"):
        raise HTTPException(status_code=404, detail="Ticker not found")
    sp500 = get_sp500_benchmark()
    score_data = calculate_score(info, sp500_52wk=sp500["52wk_change"])
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
    sp500 = get_sp500_benchmark()
    results = []
    for ticker in tickers[:10]:  # max 10 at a time
        try:
            stock = yf.Ticker(ticker.upper())
            info = stock.info
            if info.get("currentPrice"):
                score_data = calculate_score(info, sp500_52wk=sp500["52wk_change"])
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
# Route 6: Run a backtest
@app.post("/backtest")
def backtest(tickers: list[str]):
    years = [2022, 2023, 2024]
    return run_backtest(tickers, years)
# Route 7: Score an ETF, index fund, or mutual fund
@app.get("/fund/{ticker}")
def get_fund_score(ticker: str):
    stock = yf.Ticker(ticker.upper())
    info = stock.info
    quote_type = info.get("quoteType", "")
    if not info.get("totalAssets") and not info.get("navPrice") and not info.get("regularMarketPrice"):
        raise HTTPException(status_code=404, detail="Fund not found")
    sp500 = get_sp500_benchmark()
    score_data = calculate_fund_score(info, sp500_3yr=sp500["3yr_return"])
    return {
        "ticker": ticker.upper(),
        "name": info.get("longName"),
        "quote_type": quote_type,
        "fund_family": info.get("fundFamily"),
        "category": info.get("category"),
        "price": info.get("navPrice") or info.get("regularMarketPrice"),
        "total_assets": info.get("totalAssets"),
        "expense_ratio": info.get("annualReportExpenseRatio") or info.get("expenseRatio"),
        "three_year_return": info.get("threeYearAverageReturn"),
        "five_year_return": info.get("fiveYearAverageReturn"),
        "ytd_return": info.get("ytdReturn"),
        "dividend_yield": info.get("dividendYield") or info.get("trailingAnnualDividendYield"),
        "beta": info.get("beta3Year") or info.get("beta"),
        **score_data
    }

# Route 8: Goal-based recommendations
_GOAL_TICKERS = {
    "growth":           ["NVDA", "META",  "GOOGL", "AMZN", "MSFT", "TSLA", "AVGO", "CRM",  "QQQ",  "VUG" ],
    "passive_income":   ["KO",   "PEP",   "JNJ",   "PG",   "ABBV", "O",    "VZ",   "SCHD", "VYM",  "JEPI"],
    "balanced":         ["AAPL", "MSFT",  "JPM",   "JNJ",  "V",    "PG",   "VOO",  "VTI",  "SCHD"        ],
    "value":            ["BRK-B","JPM",   "BAC",   "INTC", "PFE",  "C",    "WFC",  "CVS",  "VTV",  "IVE" ],
    "international":    ["ASML", "NVO",   "TSM",   "TM",   "SONY", "SAP",  "UL",   "BTI",  "EFA",  "VEU" ],
    "consumer_staples": ["KO",   "PEP",   "PG",    "WMT",  "COST", "MDLZ", "GIS",  "CL",   "VDC",  "XLP" ],
}

@app.get("/recommend")
def recommend(goal: str, amount: float):
    tickers = _GOAL_TICKERS.get(goal)
    if not tickers:
        raise HTTPException(status_code=400, detail="Unknown goal. Use: growth, passive_income, balanced")

    sp500 = get_sp500_benchmark()
    results = []

    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            quote_type = info.get("quoteType", "")
            is_fund = quote_type in ("ETF", "MUTUALFUND")

            if is_fund:
                price = info.get("navPrice") or info.get("regularMarketPrice")
                if not price:
                    continue
                score_data = calculate_fund_score(info, sp500_3yr=sp500["3yr_return"])
                category = info.get("category") or "ETF"
            else:
                price = info.get("currentPrice")
                if not price:
                    continue
                score_data = calculate_score(info, sp500_52wk=sp500["52wk_change"])
                category = info.get("sector") or "Stock"

            results.append({
                "ticker":      ticker,
                "name":        info.get("longName", ticker),
                "category":    category,
                "price":       price,
                "type":        "ETF" if is_fund else "Stock",
                "total_score": score_data["total_score"],
            })
        except Exception:
            pass

    results.sort(key=lambda x: x["total_score"], reverse=True)
    top = results[:5]

    if top:
        total_score = sum(r["total_score"] for r in top)
        for r in top:
            r["allocation"] = round(amount * r["total_score"] / total_score, 2)
            r["shares"]     = max(0, int(r["allocation"] / r["price"])) if r["price"] > 0 else 0

    return {"goal": goal, "amount": amount, "recommendations": top}

# Route 9: Get sentiment for a stock
@app.get("/sentiment/{ticker}")
def get_sentiment(ticker: str):
    stock = yf.Ticker(ticker.upper())
    info  = stock.info
    company = info.get("longName", ticker)
    return get_combined_sentiment(ticker.upper(), company)