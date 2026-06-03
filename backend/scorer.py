# scorer.py — Stock scoring algorithm
# Each metric is scored 0-100, then combined with weights

def score_pe_ratio(pe):
    """Lower P/E = better value. Score drops as P/E rises."""
    if pe is None or pe <= 0:
        return 50  # neutral if no data
    if pe < 10:   return 100
    if pe < 15:   return 85
    if pe < 20:   return 70
    if pe < 25:   return 55
    if pe < 35:   return 40
    if pe < 50:   return 25
    return 10

def score_profit_margin(margin):
    """Higher margin = better. Score rises with profitability."""
    if margin is None:
        return 50
    pct = margin * 100  # convert 0.25 → 25%
    if pct > 30:   return 100
    if pct > 20:   return 85
    if pct > 15:   return 70
    if pct > 10:   return 55
    if pct > 5:    return 40
    if pct > 0:    return 25
    return 10  # losing money

def score_revenue_growth(growth):
    """Higher revenue growth = better. Negative growth penalised."""
    if growth is None:
        return 50
    pct = growth * 100
    if pct > 30:   return 100
    if pct > 20:   return 85
    if pct > 10:   return 70
    if pct > 5:    return 55
    if pct > 0:    return 40
    if pct > -10:  return 25
    return 10  # shrinking fast

def score_debt_to_equity(de):
    """Lower debt = better. High debt is risky."""
    if de is None or de < 0:
        return 50
    if de < 0.3:  return 100
    if de < 0.7:  return 85
    if de < 1.0:  return 70
    if de < 1.5:  return 55
    if de < 2.0:  return 40
    if de < 3.0:  return 25
    return 10

def score_dividend_yield(yield_val):
    """
    Higher yield = more income, but very high yields signal distress.
    None/0 is neutral (50) so growth stocks aren't unfairly penalised.
    """
    if yield_val is None or yield_val == 0:
        return 50  # neutral — could be a growth stock
    pct = yield_val * 100
    if pct > 7:    return 30   # likely a yield trap
    if pct > 5:    return 65
    if pct > 3.5:  return 100  # sweet spot
    if pct > 2:    return 85
    if pct > 1:    return 60
    return 40  # minimal yield

def score_payout_ratio(ratio):
    """
    Sustainable payout is 30-60%. Above 100% means paying out more than earned.
    None is neutral; negative means paying dividends while unprofitable.
    """
    if ratio is None:
        return 50
    if ratio < 0:    return 10  # paying dividends while losing money
    if ratio > 1.0:  return 10  # unsustainable (>100%)
    if ratio > 0.80: return 30
    if ratio > 0.60: return 55
    if ratio > 0.30: return 100  # sweet spot
    return 70  # low payout — conservative but room to grow

def calculate_score(info: dict) -> dict:
    """
    Main scoring function.
    Takes a yfinance info dict, returns a score and breakdown.
    """
    pe           = info.get("trailingPE")
    margin       = info.get("profitMargins")
    growth       = info.get("revenueGrowth")
    de           = info.get("debtToEquity")
    div_yield    = info.get("dividendYield") or info.get("trailingAnnualDividendYield")
    payout_ratio = info.get("payoutRatio")

    # Score each metric individually
    pe_score     = score_pe_ratio(pe)
    margin_score = score_profit_margin(margin)
    growth_score = score_revenue_growth(growth)
    de_score     = score_debt_to_equity(de)
    div_score    = score_dividend_yield(div_yield)
    payout_score = score_payout_ratio(payout_ratio)

    # Weighted average (weights must add to 1.0)
    total = (
        pe_score     * 0.25 +
        margin_score * 0.20 +
        growth_score * 0.20 +
        de_score     * 0.15 +
        div_score    * 0.12 +
        payout_score * 0.08
    )

    return {
        "total_score": round(total, 1),
        "breakdown": {
            "pe_ratio":       {"score": pe_score,     "value": pe,           "weight": "25%"},
            "profit_margin":  {"score": margin_score, "value": margin,       "weight": "20%"},
            "revenue_growth": {"score": growth_score, "value": growth,       "weight": "20%"},
            "debt_to_equity": {"score": de_score,     "value": de,           "weight": "15%"},
            "dividend_yield": {"score": div_score,    "value": div_yield,    "weight": "12%"},
            "payout_ratio":   {"score": payout_score, "value": payout_ratio, "weight": "8%"},
        }
    }