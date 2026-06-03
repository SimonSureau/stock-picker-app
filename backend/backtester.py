# backtester.py — parallel fetching for speed

import yfinance as yf
import concurrent.futures
from scorer import calculate_score

def _get_annual_return(ticker: str, year: int) -> float:
    try:
        hist = yf.Ticker(ticker).history(start=f"{year}-01-01", end=f"{year}-12-31")
        if hist.empty or len(hist) < 10:
            return None
        return round((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100, 2)
    except:
        return None

def _fetch_and_score(ticker: str):
    try:
        info = yf.Ticker(ticker).info
        if not info.get("currentPrice"):
            return None
        return {"ticker": ticker, "score": calculate_score(info)["total_score"]}
    except:
        return None

def run_backtest(tickers: list, years: list) -> dict:
    # Step 1 — score every ticker once in parallel (not once per year)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        scored = [r for r in ex.map(_fetch_and_score, tickers) if r]

    top3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
    if not top3:
        return {
            "years_tested": 0, "total_strategy_return": 0,
            "total_sp500_return": 0, "outperformance": 0, "yearly_results": []
        }

    # Step 2 — fetch all annual returns in parallel (top 3 picks + SPY for every year)
    tasks = [(s["ticker"], y) for s in top3 for y in years] + [("SPY", y) for y in years]
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        futures = {task: ex.submit(_get_annual_return, *task) for task in tasks}
    returns_map = {task: fut.result() for task, fut in futures.items()}

    # Step 3 — compile year-by-year results
    results = []
    total_strategy = 0
    total_sp500    = 0
    valid_years    = 0

    for year in years:
        sp500_ret  = returns_map.get(("SPY", year))
        year_picks = []
        year_rets  = []

        for stock in top3:
            ret  = returns_map.get((stock["ticker"], year))
            pick = {"ticker": stock["ticker"], "score": stock["score"]}
            if ret is not None:
                pick["return"] = ret
                year_rets.append(ret)
            year_picks.append(pick)

        if not year_rets:
            continue

        avg = round(sum(year_rets) / len(year_rets), 2)
        results.append({
            "year":            year,
            "top_picks":       year_picks,
            "strategy_return": avg,
            "sp500_return":    sp500_ret,
            "outperformed":    avg > (sp500_ret or 0),
        })
        total_strategy += avg
        total_sp500    += (sp500_ret or 0)
        valid_years    += 1

    return {
        "years_tested":          valid_years,
        "total_strategy_return": round(total_strategy, 2),
        "total_sp500_return":    round(total_sp500, 2),
        "outperformance":        round(total_strategy - total_sp500, 2),
        "yearly_results":        results,
    }
