# fund_scorer.py — Scoring for ETFs, index funds, and mutual funds

def score_expense_ratio(ratio):
    """Lower expense ratio = better. This is the single biggest drag on long-term returns."""
    if ratio is None:
        return 50
    pct = ratio * 100
    if pct < 0.05:  return 100  # ultra-low (VOO, IVV, VTI)
    if pct < 0.20:  return 90
    if pct < 0.50:  return 75
    if pct < 1.0:   return 55
    if pct < 1.5:   return 35
    return 15

def score_annual_return(ret):
    """Higher 3-year annualised return = better."""
    if ret is None:
        return 50
    pct = ret * 100
    if pct > 20:   return 100
    if pct > 15:   return 90
    if pct > 10:   return 75
    if pct > 7:    return 60
    if pct > 5:    return 50
    if pct > 0:    return 35
    return 15

def score_total_assets(assets):
    """Larger AUM = more liquid and stable."""
    if assets is None:
        return 50
    if assets > 100e9:  return 100
    if assets > 10e9:   return 85
    if assets > 1e9:    return 70
    if assets > 100e6:  return 55
    if assets > 10e6:   return 35
    return 15

def score_fund_beta(beta):
    """Beta near 1.0 = market-like risk. Very high beta = volatile."""
    if beta is None:
        return 50
    if beta < 0.3:   return 55  # bond-like, very conservative
    if beta < 0.7:   return 80
    if beta < 1.1:   return 100
    if beta < 1.3:   return 75
    if beta < 1.6:   return 50
    return 30

def score_fund_dividend_yield(yield_val):
    """Income-focused scoring. None/0 is neutral — many growth ETFs pay nothing."""
    if yield_val is None or yield_val == 0:
        return 50
    pct = yield_val * 100
    if pct > 7:    return 55
    if pct > 4:    return 90
    if pct > 2:    return 100
    if pct > 0.5:  return 70
    return 40

def calculate_fund_score(info: dict) -> dict:
    """
    Score an ETF, index fund, or mutual fund from a yfinance info dict.
    """
    expense_ratio = info.get("annualReportExpenseRatio") or info.get("expenseRatio")
    three_yr      = info.get("threeYearAverageReturn")
    total_assets  = info.get("totalAssets")
    beta          = info.get("beta3Year") or info.get("beta")
    div_yield     = info.get("dividendYield") or info.get("trailingAnnualDividendYield")

    expense_score = score_expense_ratio(expense_ratio)
    return_score  = score_annual_return(three_yr)
    assets_score  = score_total_assets(total_assets)
    beta_score    = score_fund_beta(beta)
    yield_score   = score_fund_dividend_yield(div_yield)

    total = (
        expense_score * 0.35 +
        return_score  * 0.30 +
        assets_score  * 0.15 +
        beta_score    * 0.10 +
        yield_score   * 0.10
    )

    return {
        "total_score": round(total, 1),
        "breakdown": {
            "expense_ratio":     {"score": expense_score, "value": expense_ratio, "weight": "35%"},
            "three_year_return": {"score": return_score,  "value": three_yr,      "weight": "30%"},
            "total_assets":      {"score": assets_score,  "value": total_assets,  "weight": "15%"},
            "beta":              {"score": beta_score,    "value": beta,          "weight": "10%"},
            "dividend_yield":    {"score": yield_score,   "value": div_yield,     "weight": "10%"},
        }
    }
