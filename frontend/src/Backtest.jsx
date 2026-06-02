import { useState } from "react"
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from "recharts"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

const PRESETS = {
  "Tech":    ["AAPL", "MSFT", "GOOGL", "META", "AMZN"],
  "Finance": ["JPM", "BAC", "GS", "MS", "BLK"],
  "Mixed":   ["AAPL", "JPM", "JNJ", "PG", "MSFT"],
}

export default function Backtest() {
  const [input, setInput] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  async function runBacktest(tickers) {
    setLoading(true)
    setResult(null)
    const res = await fetch(`${API}/backtest`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(tickers)
    })
    setResult(await res.json())
    setLoading(false)
  }

  function handleRun() {
    const tickers = input.split(",").map(t => t.trim().toUpperCase()).filter(Boolean)
    if (tickers.length) runBacktest(tickers)
  }

  const chartData = result?.yearly_results.map(r => ({
    year: r.year,
    "My Strategy": r.strategy_return,
    "S&P 500": r.sp500_return,
  }))

  return (
    <div>
      <h2 style={{ fontSize:20, fontWeight:800, marginBottom:8 }}>Backtesting Engine</h2>
      <p style={{ color:"#666", fontSize:13, marginBottom:16 }}>
        Test how your scoring model would have performed from 2020–2024 vs the S&P 500.
      </p>

      <div style={{ display:"flex", gap:8, flexWrap:"wrap", marginBottom:12 }}>
        {Object.entries(PRESETS).map(([name, tickers]) => (
          <button key={name} onClick={() => { setInput(tickers.join(", ")); runBacktest(tickers); }}
            style={{ padding:"6px 14px", background:"#111", border:"1px solid #333", borderRadius:6, color:"#aaa", cursor:"pointer", fontSize:13 }}>
            {name}
          </button>
        ))}
      </div>

      <div style={{ display:"flex", gap:8, marginBottom:24 }}>
        <input value={input} onChange={e => setInput(e.target.value)} placeholder="AAPL, MSFT, JPM, JNJ, PG"
          style={{ flex:1, padding:"10px 14px", background:"#111", border:"1px solid #333", borderRadius:8, color:"#fff", fontSize:14 }} />
        <button onClick={handleRun}
          style={{ padding:"10px 22px", background:"#818cf8", border:"none", borderRadius:8, fontWeight:700, cursor:"pointer", color:"#fff" }}>
          {loading ? "Running..." : "Run Backtest"}
        </button>
      </div>

      {loading && (
        <div style={{ color:"#555", fontSize:13, padding:"20px 0" }}>
          ⏳ Fetching 5 years of historical data... this takes about 30–60 seconds.
        </div>
      )}

      {result && (
        <div>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr 1fr", gap:12, marginBottom:28 }}>
            {[
              { label:"Strategy Total", val:`${result.total_strategy_return}%`, color: result.total_strategy_return > 0 ? "#4ade80" : "#f87171" },
              { label:"S&P 500 Total",  val:`${result.total_sp500_return}%`,    color:"#818cf8" },
              { label:"Outperformance", val:`${result.outperformance > 0 ? "+" : ""}${result.outperformance}%`, color: result.outperformance > 0 ? "#4ade80" : "#f87171" },
            ].map(s => (
              <div key={s.label} style={{ background:"#111", border:"1px solid #222", borderRadius:10, padding:16 }}>
                <div style={{ fontSize:11, color:"#555", textTransform:"uppercase", marginBottom:6 }}>{s.label}</div>
                <div style={{ fontSize:26, fontWeight:800, color:s.color }}>{s.val}</div>
              </div>
            ))}
          </div>

          <h3 style={{ fontSize:14, color:"#999", marginBottom:12 }}>Year-by-Year Performance</h3>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={chartData}>
              <XAxis dataKey="year" tick={{ fontSize:12, fill:"#555" }} />
              <YAxis tick={{ fontSize:11, fill:"#555" }} tickFormatter={v => `${v}%`} />
              <Tooltip formatter={v => `${v}%`} contentStyle={{ background:"#111", border:"1px solid #333", borderRadius:8 }} />
              <Legend />
              <ReferenceLine y={0} stroke="#333" />
              <Bar dataKey="My Strategy" fill="#4ade80" radius={[4,4,0,0]} />
              <Bar dataKey="S&P 500"     fill="#818cf8" radius={[4,4,0,0]} />
            </BarChart>
          </ResponsiveContainer>

          <h3 style={{ fontSize:14, color:"#999", margin:"24px 0 12px" }}>Year-by-Year Picks</h3>
          <table style={{ width:"100%", borderCollapse:"collapse", fontSize:13 }}>
            <thead>
              <tr style={{ borderBottom:"1px solid #222", color:"#555", textAlign:"left" }}>
                <th style={{ padding:"8px 0" }}>Year</th>
                <th>Top Picks</th>
                <th>Strategy</th>
                <th>S&P 500</th>
                <th>Result</th>
              </tr>
            </thead>
            <tbody>
              {result.yearly_results.map(r => (
                <tr key={r.year} style={{ borderBottom:"1px solid #111" }}>
                  <td style={{ padding:"10px 0", fontWeight:700 }}>{r.year}</td>
                  <td style={{ color:"#818cf8" }}>{r.top_picks.map(p => p.ticker).join(", ")}</td>
                  <td style={{ color: r.strategy_return > 0 ? "#4ade80" : "#f87171", fontWeight:600 }}>{r.strategy_return}%</td>
                  <td style={{ color:"#818cf8" }}>{r.sp500_return}%</td>
                  <td>{r.outperformed ? "✅ Beat market" : "❌ Lagged"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}