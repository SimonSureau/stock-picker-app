import os, requests, yfinance as yf
from dotenv import load_dotenv

load_dotenv()

# Financial sentiment word lists
POSITIVE_WORDS = [
    "beat", "beats", "surge", "surges", "rally", "rallies",
    "profit", "profits", "growth", "record", "strong",
    "upgrade", "buy", "bullish", "outperform", "raised",
    "exceeded", "innovative", "partnership", "contract",
    "dividend", "expansion", "gain", "gains", "soars", "soar",
    "positive", "optimistic", "opportunity", "momentum"
]

NEGATIVE_WORDS = [
    "miss", "misses", "missed", "drop", "drops", "fall", "falls",
    "loss", "losses", "lawsuit", "investigation", "fraud",
    "downgrade", "sell", "bearish", "underperform", "cut",
    "decline", "warning", "risk", "concern", "weak", "recall",
    "layoff", "layoffs", "bankrupt", "debt", "crash", "plunge",
    "plunges", "negative", "pessimistic", "volatile"
]

def score_text(text: str) -> float:
    """Score a piece of text: +1 per positive word, -1 per negative word."""
    words = text.lower().split()
    score = 0
    for word in words:
        clean = word.strip(".,!?\"'()")
        if clean in POSITIVE_WORDS: score += 1
        if clean in NEGATIVE_WORDS: score -= 1
    return score

def get_news_sentiment(ticker: str, company: str) -> list:
    """Fetch recent news headlines from NewsAPI."""
    key = os.getenv("NEWS_API_KEY")
    if not key:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": f"{ticker} stock",
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": key
        }
        res = requests.get(url, params=params, timeout=5)
        articles = res.json().get("articles", [])
        results = []
        for a in articles[:8]:
            title = a.get("title", "")
            score = score_text(title)
            results.append({
                "source": "news",
                "text": title,
                "score": score,
                "label": "positive" if score > 0 else "negative" if score < 0 else "neutral"
            })
        return results
    except:
        return []

def get_yahoo_finance_news(ticker: str) -> list:
    """Get recent news from Yahoo Finance using yfinance — no API key needed."""
    try:
        stock = yf.Ticker(ticker)
        news = stock.news
        results = []
        for item in news[:10]:
            title = item.get("content", {}).get("title", "")
            if not title:
                continue
            score = score_text(title)
            results.append({
                "source": "Yahoo Finance",
                "text": title,
                "score": score,
                "label": "positive" if score > 0 else "negative" if score < 0 else "neutral"
            })
        return results
    except:
        return []

def get_combined_sentiment(ticker: str, company: str) -> dict:
    """Combine NewsAPI and Yahoo Finance sentiment into one overall score."""
    news_items  = get_news_sentiment(ticker, company)
    yahoo_items = get_yahoo_finance_news(ticker)
    all_items   = news_items + yahoo_items

    if not all_items:
        return { "overall_score": 0, "label": "neutral", "items": [], "news_count": 0, "yahoo_count": 0 }

    total = sum(i["score"] for i in all_items)
    avg   = round(total / len(all_items), 2)
    label = "positive" if avg > 0.2 else "negative" if avg < -0.2 else "neutral"

    return {
        "overall_score": avg,
        "label": label,
        "total_items": len(all_items),
        "news_count": len(news_items),
        "yahoo_count": len(yahoo_items),
        "items": all_items
    }