# backtester.py — bulk history download to stay within Railway's 30s timeout

import yfinance as yf
import concurrent.futures
import pandas as pd
from scorer import calculate_score

def _fetch_and_score(ticker: str):
    try:
        info = yf.Ticker(ticker).info
        if not info.get("currentPrice"):
            return None
        return {"ticker": ticker, "score": calculate_score(info)["total_score"]}
    except:
        return None

def _year_return(close_df: pd.DataFrame, ticker: str, year: int):
    try:
        if ticker not in close_df.columns:
            return None
        s  = close_df[ticker].dropna()
        yr = s[s.index.year == year]
        if len(yr) < 10:
            return None
        return round((yr.iloc[-1] - yr.iloc[0]) / yr.iloc[0] * 100, 2)
    except:
        return None

def run_backtest(tickers: list, years: list) -> dict:
    # 1. Score each ticker once in parallel (current fundamentals, same for all years)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        scored = [r for r in ex.map(_fetch_and_score, tickers) if r]

    top3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
    if not top3:
        return {
            "years_tested": 0, "total_strategy_return": 0,
            "total_sp500_return": 0, "outperformance": 0, "yearly_results": []
        }

    # 2. Fetch ALL price history in ONE bulk request instead of N×M individual calls
    dl_tickers = [s["ticker"] for s in top3] + ["SPY"]
    start_date = f"{min(years)}-01-01"
    end_date   = f"{max(years)}-12-31"

    close = pd.DataFrame()
    try:
        raw = yf.download(dl_tickers, start=start_date, end=end_date,
                          auto_adjust=True, progress=False)
        # yfinance returns MultiIndex columns when multiple tickers are given
        if isinstance(raw.columns, pd.MultiIndex):
            close = raw["Close"]
        else:
            close = raw[["Close"]].rename(columns={"Close": dl_tickers[0]})
    except Exception:
        pass

    # 3. Compile year-by-year results
    results        = []
    total_strategy = 0
    total_sp500    = 0
    valid_years    = 0

    for year in years:
        sp500_ret  = _year_return(close, "SPY", year)
        year_picks = []
        year_rets  = []

        for stock in top3:
            ret  = _year_return(close, stock["ticker"], year)
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
