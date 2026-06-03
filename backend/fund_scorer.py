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

def score_fund_vs_sp500(fund_3yr, sp500_3yr):
    """Score 3-year annualised return vs the S&P 500. Even small consistent alpha matters."""
    if fund_3yr is None or sp500_3yr is None:
        return 50
    alpha = fund_3yr - sp500_3yr  # decimal
    if alpha > 0.05:   return 100
    if alpha > 0.02:   return 85
    if alpha > 0:      return 70
    if alpha > -0.02:  return 55
    if alpha > -0.05:  return 35
    return 15

def calculate_fund_score(info: dict, sp500_3yr: float = None) -> dict:
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
    sp500_score   = score_fund_vs_sp500(three_yr, sp500_3yr)

    total = (
        expense_score * 0.30 +
        return_score  * 0.22 +
        sp500_score   * 0.18 +
        assets_score  * 0.12 +
        beta_score    * 0.10 +
        yield_score   * 0.08
    )

    alpha = round((three_yr - sp500_3yr) * 100, 1) if three_yr is not None and sp500_3yr is not None else None

    return {
        "total_score": round(total, 1),
        "fund_3yr_return": round(three_yr * 100, 1) if three_yr is not None else None,
        "sp500_3yr_return": round(sp500_3yr * 100, 1) if sp500_3yr is not None else None,
        "alpha": alpha,
        "breakdown": {
            "expense_ratio":     {"score": expense_score, "value": expense_ratio, "weight": "30%"},
            "three_year_return": {"score": return_score,  "value": three_yr,      "weight": "22%"},
            "vs_sp500":          {"score": sp500_score,   "value": alpha,         "weight": "18%"},
            "total_assets":      {"score": assets_score,  "value": total_assets,  "weight": "12%"},
            "beta":              {"score": beta_score,    "value": beta,          "weight": "10%"},
            "dividend_yield":    {"score": yield_score,   "value": div_yield,     "weight": "8%"},
        }
    }
