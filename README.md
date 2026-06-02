# 📈 Stock Picker App

A full-stack stock analysis platform built with Python and React.

## Live Demo
🔗 [stock-picker-app.vercel.app](https://your-app.vercel.app)

## Features
- **Stock Scoring Model** — ranks stocks 0–100 using P/E ratio,
  profit margin, revenue growth, and debt-to-equity (weighted formula)
- **Stock Screener** — compare and rank multiple stocks side by side
- **Backtesting Engine** — tests strategy performance vs S&P 500
  across 5 years of historical data
- **Sentiment Analysis** — scores market sentiment using financial
  news and Yahoo Finance headlines

## Tech Stack
- **Backend:** Python, FastAPI, yfinance, NewsAPI
- **Frontend:** React, Vite, Recharts
- **Deployment:** Railway (backend), Vercel (frontend)

## Run Locally
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```