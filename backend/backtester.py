# backtester.py
# Simulates buying top-scoring stocks each year and measures performance

import yfinance as yf
from scorer import calculate_score
from datetime import datetime

def get_annual_return(ticker: str, year: int) -> float:
    """Get the % return of a stock over a calendar year."""
    try:
        start = f"{year}-01-01"
        end   = f"{year}-12-31"
        hist  = yf.Ticker(ticker).history(start=start, end=end)
        if hist.empty or len(hist) < 10:
            return None
        start_price = hist["Close"].iloc[0]
        end_price   = hist["Close"].iloc[-1]
        return round((end_price - start_price) / start_price * 100, 2)
    except:
        return None

def get_sp500_return(year: int) -> float:
    """Get the S&P 500 return for a given year (using SPY ETF)."""
    return get_annual_return("SPY", year)

def run_backtest(tickers: list, years: list) -> dict:
    """
    For each year, score all tickers, pick the top 3,
    measure their average return vs the S&P 500.
    """
    results = []
    total_strategy = 0
    total_sp500    = 0
    valid_years    = 0

    for year in years:
        # Score each ticker using current fundamentals
        scored = []
        for ticker in tickers:
            try:
                info = yf.Ticker(ticker).info
                if info.get("currentPrice"):
                    score_data = calculate_score(info)
                    scored.append({
                        "ticker": ticker,
                        "score": score_data["total_score"]
                    })
            except:
                pass

        # Pick top 3 scorers
        top3 = sorted(scored, key=lambda x: x["score"], reverse=True)[:3]
        if not top3:
            continue

        # Get their actual returns for that year
        returns = []
        for stock in top3:
            ret = get_annual_return(stock["ticker"], year)
            if ret is not None:
                stock["return"] = ret
                returns.append(ret)

        if not returns:
            continue

        # Average return of top 3 picks
        avg_return = round(sum(returns) / len(returns), 2)
        sp500_return = get_sp500_return(year)

        results.append({
            "year":          year,
            "top_picks":     top3,
            "strategy_return": avg_return,
            "sp500_return":  sp500_return,
            "outperformed":  avg_return > (sp500_return or 0)
        })

        total_strategy += avg_return
        total_sp500    += (sp500_return or 0)
        valid_years    += 1

    return {
        "years_tested":       valid_years,
        "total_strategy_return": round(total_strategy, 2),
        "total_sp500_return":    round(total_sp500, 2),
        "outperformance":        round(total_strategy - total_sp500, 2),
        "yearly_results":        results
    }