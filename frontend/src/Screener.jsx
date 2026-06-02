import { useState } from "react"

const API = "http://localhost:8000"

const PRESETS = {
  "Tech Giants": ["AAPL", "MSFT", "GOOGL", "META", "AMZN"],
  "EV & Energy": ["TSLA", "RIVN", "NEE", "ENPH"],
  "Finance":     ["JPM", "BAC", "GS", "MS", "BLK"],
}

function ScoreChip({ score }) {
  const bg = score >= 70 ? "#14532d" : score >= 50 ? "#422006" : "#450a0a"
  const color = score >= 70 ? "#4ade80" : score >= 50 ? "#f59e0b" : "#f87171"
  return <span style={{ background:bg, color, padding:"3px 10px", borderRadius:99, fontWeight:700, fontSize:13 }}>{score}</span>
}

export default function Screener() {
  const [input, setInput] = useState("")
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)

  async function runScreen(tickers) {
    setLoading(true)
    setResults([])
    const res = await fetch(`${API}/screen`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tickers)
    })
    const data = await res.json()
    setResults(data)
    setLoading(false)
  }

  function handleSubmit() {
    const tickers = input.split(",").map(t => t.trim().toUpperCase()).filter(Boolean)
    if (tickers.length) runScreen(tickers)
  }

  return (
    <div>
      <h2 style={{ fontSize:20, fontWeight:800, marginBottom:8 }}>Stock Screener</h2>
      <p style={{ color:"#666", fontSize:13, marginBottom:16 }}>Enter up to 10 tickers separated by commas, or pick a preset.</p>

      <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:12 }}>
        {Object.entries(PRESETS).map(([name, tickers]) => (
          <button key={name} onClick={() => { setInput(tickers.join(", ")); runScreen(tickers); }}
            style={{ padding:"6px 14px", background:"#111", border:"1px solid #333", borderRadius:6, color:"#aaa", cursor:"pointer", fontSize:13 }}>
            {name}
          </button>
        ))}
      </div>

      <div style={{ display:"flex", gap:8, marginBottom:24 }}>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="AAPL, MSFT, TSLA, GOOGL"
          style={{ flex:1, padding:"10px 14px", background:"#111", border:"1px solid #333", borderRadius:8, color:"#fff", fontSize:14 }} />
        <button onClick={handleSubmit} style={{ padding:"10px 22px", background:"#4ade80", border:"none", borderRadius:8, fontWeight:700, cursor:"pointer", color:"#000" }}>
          {loading ? "Scoring..." : "Screen"}
        </button>
      </div>

      {loading && <p style={{ color:"#555", fontSize:13 }}>Fetching data for all stocks... this takes ~10 seconds</p>}

      {results.length > 0 && (
        <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}>
          <thead>
            <tr style={{ borderBottom:"1px solid #222", color:"#555", textAlign:"left" }}>
              <th style={{ padding:"8px 0" }}>Rank</th>
              <th>Ticker</th>
              <th>Company</th>
              <th>Sector</th>
              <th>Price</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => (
              <tr key={r.ticker} style={{ borderBottom:"1px solid #111" }}>
                <td style={{ padding:"10px 0", color:"#555" }}>#{i+1}</td>
                <td style={{ fontWeight:700, color:"#4ade80" }}>{r.ticker}</td>
                <td style={{ color:"#ccc", maxWidth:180, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{r.name}</td>
                <td style={{ color:"#555" }}>{r.sector}</td>
                <td style={{ color:"#fff" }}>${r.price?.toFixed(2)}</td>
                <td><ScoreChip score={r.total_score} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}