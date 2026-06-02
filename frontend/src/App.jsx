import { useState } from "react"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import Screener from "./Screener"

const API = "http://localhost:8000"

function ScoreBadge({ score }) {
  const color = score >= 70 ? "#4ade80" : score >= 50 ? "#f59e0b" : "#f87171"
  const label = score >= 70 ? "Strong" : score >= 50 ? "Fair" : "Weak"
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 12, margin: "12px 0" }}>
      <div style={{ fontSize: 48, fontWeight: 800, color }}>{score}</div>
      <div>
        <div style={{ fontSize: 13, color, fontWeight: 600 }}>{label}</div>
        <div style={{ fontSize: 12, color: "#888" }}>out of 100</div>
      </div>
    </div>
  )
}

function ScoreBar({ label, score, value, weight }) {
  const color = score >= 70 ? "#4ade80" : score >= 50 ? "#f59e0b" : "#f87171"
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:4 }}>
        <span style={{ color: "#ccc" }}>{label} <span style={{color:"#555"}}>({weight})</span></span>
        <span style={{ color, fontWeight: 600 }}>{score}/100</span>
      </div>
      <div style={{ height:6, background:"#222", borderRadius:99 }}>
        <div style={{ width:`${score}%`, height:"100%", background:color, borderRadius:99, transition:"width 0.8s ease" }}/>
      </div>
    </div>
  )
}

export default function App() {
  const [ticker, setTicker] = useState("")
  const [data, setData] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [tab, setTab] = useState("search")

  async function search() {
    if (!ticker) return
    setLoading(true)
    setError("")
    try {
      const [scoreRes, histRes] = await Promise.all([
        fetch(`${API}/score/${ticker}`).then(r => r.json()),
        fetch(`${API}/history/${ticker}`).then(r => r.json()),
      ])
      if (scoreRes.detail) throw new Error(scoreRes.detail)
      setData(scoreRes)
      setHistory(histRes.prices)
    } catch(e) {
      setError("Ticker not found. Try AAPL, MSFT or TSLA.")
    }
    setLoading(false)
  }

  return (
    <div style={{ maxWidth:760, margin:"40px auto", padding:"0 20px", fontFamily:"sans-serif", background:"#0a0a0a", minHeight:"100vh", color:"#fff" }}>
      <h1 style={{ fontSize:28, fontWeight:800, marginBottom:8 }}>📈 Stock Picker</h1>
      <p style={{ color:"#666", marginBottom:16, fontSize:14 }}>AI-powered stock scoring using financial fundamentals</p>

      <div style={{ display:"flex", gap:8, marginBottom:24 }}>
        <button onClick={() => setTab("search")}
          style={{ padding:"8px 18px", background: tab==="search" ? "#4ade80" : "#111", border:"1px solid #333", borderRadius:6, color: tab==="search" ? "#000" : "#aaa", cursor:"pointer", fontWeight:600 }}>
          Single Stock
        </button>
        <button onClick={() => setTab("screener")}
          style={{ padding:"8px 18px", background: tab==="screener" ? "#4ade80" : "#111", border:"1px solid #333", borderRadius:6, color: tab==="screener" ? "#000" : "#aaa", cursor:"pointer", fontWeight:600 }}>
          Screener
        </button>
      </div>

      {tab === "search" && (
        <div>
          <div style={{ display:"flex", gap:8, marginBottom:8 }}>
            <input
              value={ticker}
              onChange={e => setTicker(e.target.value.toUpperCase())}
              onKeyDown={e => e.key === "Enter" && search()}
              placeholder="Enter ticker (e.g. AAPL)"
              style={{ flex:1, padding:"12px 16px", fontSize:16, background:"#111", border:"1px solid #333", borderRadius:8, color:"#fff" }}
            />
            <button onClick={search} style={{ padding:"12px 28px", fontSize:15, background:"#4ade80", border:"none", borderRadius:8, fontWeight:700, cursor:"pointer", color:"#000" }}>
              {loading ? "..." : "Score"}
            </button>
          </div>

          {error && <p style={{ color:"#f87171", fontSize:13 }}>{error}</p>}

          {data && (
            <div style={{ marginTop:28 }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", flexWrap:"wrap", gap:16 }}>
                <div>
                  <h2 style={{ fontSize:22, fontWeight:800 }}>{data.name}</h2>
                  <p style={{ color:"#666", fontSize:13 }}>{data.ticker} · {data.sector} · ${data.price?.toFixed(2)}</p>
                  <ScoreBadge score={data.total_score} />
                </div>

                <div style={{ background:"#111", border:"1px solid #222", borderRadius:12, padding:16, minWidth:260 }}>
                  <p style={{ fontSize:12, color:"#555", marginBottom:12, fontWeight:600, textTransform:"uppercase", letterSpacing:"0.06em" }}>Score Breakdown</p>
                  <ScoreBar label="P/E Ratio"      {...data.breakdown.pe_ratio}       />
                  <ScoreBar label="Profit Margin"  {...data.breakdown.profit_margin}  />
                  <ScoreBar label="Revenue Growth" {...data.breakdown.revenue_growth} />
                  <ScoreBar label="Debt/Equity"    {...data.breakdown.debt_to_equity} />
                </div>
              </div>

              <h3 style={{ marginTop:28, marginBottom:12, fontSize:15, color:"#999" }}>1-Year Price History</h3>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={history}>
                  <XAxis dataKey="date" tick={{ fontSize:10, fill:"#555" }} tickCount={6} />
                  <YAxis domain={["auto","auto"]} tick={{ fontSize:10, fill:"#555" }} />
                  <Tooltip contentStyle={{ background:"#111", border:"1px solid #333", borderRadius:8 }} />
                  <Line type="monotone" dataKey="close" dot={false} stroke="#4ade80" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {tab === "screener" && <Screener />}

    </div>
  )
}
