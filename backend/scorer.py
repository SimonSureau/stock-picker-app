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

def calculate_score(info: dict) -> dict:
    """
    Main scoring function.
    Takes a yfinance info dict, returns a score and breakdown.
    """
    pe    = info.get("trailingPE")
    margin = info.get("profitMargins")
    growth = info.get("revenueGrowth")
    de    = info.get("debtToEquity")

    # Score each metric individually
    pe_score     = score_pe_ratio(pe)
    margin_score = score_profit_margin(margin)
    growth_score = score_revenue_growth(growth)
    de_score     = score_debt_to_equity(de)

    # Weighted average (weights must add to 1.0)
    total = (
        pe_score     * 0.30 +
        margin_score * 0.25 +
        growth_score * 0.25 +
        de_score     * 0.20
    )

    return {
        "total_score": round(total, 1),
        "breakdown": {
            "pe_ratio":      {"score": pe_score,     "value": pe,     "weight": "30%"},
            "profit_margin": {"score": margin_score, "value": margin, "weight": "25%"},
            "revenue_growth":{"score": growth_score, "value": growth, "weight": "25%"},
            "debt_to_equity":{"score": de_score,     "value": de,     "weight": "20%"},
        }
    }