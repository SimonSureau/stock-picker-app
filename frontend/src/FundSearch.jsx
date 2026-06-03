import { useState } from "react"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

const PRESETS = ["VOO", "SPY", "QQQ", "VTI", "BND", "VXUS", "ARKK", "GLD"]

function ScoreBadge({ score }) {
  const color = score >= 70 ? "#4ade80" : score >= 50 ? "#f59e0b" : "#f87171"
  const label = score >= 70 ? "Strong" : score >= 50 ? "Fair" : "Weak"
  return (
    <div style={{ display:"flex", alignItems:"center", gap:12, margin:"12px 0" }}>
      <div style={{ fontSize:48, fontWeight:800, color }}>{score}</div>
      <div>
        <div style={{ fontSize:13, color, fontWeight:600 }}>{label}</div>
        <div style={{ fontSize:12, color:"#888" }}>out of 100</div>
      </div>
    </div>
  )
}

function ScoreBar({ label, score, value, weight }) {
  const color = score >= 70 ? "#4ade80" : score >= 50 ? "#f59e0b" : "#f87171"
  return (
    <div style={{ marginBottom:10 }}>
      <div style={{ display:"flex", justifyContent:"space-between", fontSize:12, marginBottom:4 }}>
        <span style={{ color:"#ccc" }}>{label} <span style={{ color:"#555" }}>({weight})</span></span>
        <span style={{ color, fontWeight:600 }}>{score}/100</span>
      </div>
      <div style={{ height:6, background:"#222", borderRadius:99 }}>
        <div style={{ width:`${score}%`, height:"100%", background:color, borderRadius:99, transition:"width 0.8s ease" }} />
      </div>
    </div>
  )
}

function StatRow({ label, value }) {
  return (
    <div style={{ display:"flex", justifyContent:"space-between", padding:"6px 0", borderBottom:"1px solid #1a1a1a", fontSize:13 }}>
      <span style={{ color:"#666" }}>{label}</span>
      <span style={{ color:"#fff", fontWeight:600 }}>{value ?? "—"}</span>
    </div>
  )
}

function fmt(val, type) {
  if (val == null) return "—"
  if (type === "pct")    return `${(val * 100).toFixed(2)}%`
  if (type === "ratio")  return `${(val * 100).toFixed(2)}%`
  if (type === "aum") {
    if (val >= 1e12) return `$${(val / 1e12).toFixed(2)}T`
    if (val >= 1e9)  return `$${(val / 1e9).toFixed(2)}B`
    if (val >= 1e6)  return `$${(val / 1e6).toFixed(2)}M`
    return `$${val.toLocaleString()}`
  }
  return val
}

export default function FundSearch() {
  const [ticker, setTicker]   = useState("")
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError]     = useState("")

  async function search(symbol) {
    const t = (symbol || ticker).trim().toUpperCase()
    if (!t) return
    setLoading(true)
    setError("")
    setData(null)
    try {
      const res = await fetch(`${API}/fund/${t}`)
      const json = await res.json()
      if (json.detail) throw new Error(json.detail)
      setData(json)
      setTicker(t)
    } catch {
      setError("Fund not found. Try a ticker like VOO, SPY, or QQQ.")
    }
    setLoading(false)
  }

  return (
    <div>
      <h2 style={{ fontSize:20, fontWeight:800, marginBottom:4 }}>Funds & ETFs</h2>
      <p style={{ color:"#666", fontSize:13, marginBottom:14 }}>Score ETFs, index funds, and mutual funds by expense ratio, returns, and more.</p>

      <div style={{ display:"flex", gap:6, flexWrap:"wrap", marginBottom:12 }}>
        {PRESETS.map(t => (
          <button key={t} onClick={() => search(t)}
            style={{ padding:"5px 12px", background:"#111", border:"1px solid #333", borderRadius:6, color:"#aaa", cursor:"pointer", fontSize:12 }}>
            {t}
          </button>
        ))}
      </div>

      <div style={{ display:"flex", gap:8, marginBottom:8 }}>
        <input
          value={ticker}
          onChange={e => setTicker(e.target.value.toUpperCase())}
          onKeyDown={e => e.key === "Enter" && search()}
          placeholder="Enter ticker (e.g. VOO, QQQ, VFIAX)"
          style={{ flex:1, padding:"12px 16px", fontSize:16, background:"#111", border:"1px solid #333", borderRadius:8, color:"#fff", textTransform:"uppercase" }}
        />
        <button onClick={() => search()} style={{ padding:"12px 28px", fontSize:15, background:"#818cf8", border:"none", borderRadius:8, fontWeight:700, cursor:"pointer", color:"#fff" }}>
          {loading ? "..." : "Score"}
        </button>
      </div>

      {error && <p style={{ color:"#f87171", fontSize:13 }}>{error}</p>}

      {data && (
        <div style={{ marginTop:28 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", flexWrap:"wrap", gap:16 }}>
            <div>
              <h2 style={{ fontSize:22, fontWeight:800 }}>{data.name}</h2>
              <p style={{ color:"#666", fontSize:13 }}>
                {data.ticker} · {data.quote_type} · {data.fund_family}
              </p>
              {data.category && <p style={{ color:"#555", fontSize:12 }}>{data.category}</p>}
              <ScoreBadge score={data.total_score} />
            </div>

            <div style={{ background:"#111", border:"1px solid #222", borderRadius:12, padding:16, minWidth:260 }}>
              <p style={{ fontSize:12, color:"#555", marginBottom:12, fontWeight:600, textTransform:"uppercase", letterSpacing:"0.06em" }}>Score Breakdown</p>
              <ScoreBar label="Expense Ratio"    {...data.breakdown.expense_ratio}     />
              <ScoreBar label="3-Year Return"    {...data.breakdown.three_year_return} />
              <ScoreBar label="vs S&P 500"       {...data.breakdown.vs_sp500}          />
              <ScoreBar label="Total Assets"     {...data.breakdown.total_assets}      />
              <ScoreBar label="Beta"             {...data.breakdown.beta}              />
              <ScoreBar label="Dividend Yield"   {...data.breakdown.dividend_yield}    />
            </div>
          </div>

          {data.fund_3yr_return != null && (
            <div style={{ fontSize:12, color:"#555", marginTop:8 }}>
              3yr annualised: <span style={{ color: data.fund_3yr_return >= 0 ? "#4ade80" : "#f87171" }}>
                {data.fund_3yr_return > 0 ? "+" : ""}{data.fund_3yr_return}%
              </span>
              {data.sp500_3yr_return != null && (
                <> vs S&P <span style={{ color:"#818cf8" }}>
                  {data.sp500_3yr_return > 0 ? "+" : ""}{data.sp500_3yr_return}%
                </span>
                {data.alpha != null && (
                  <span style={{ color: data.alpha >= 0 ? "#4ade80" : "#f87171", marginLeft:4 }}>
                    ({data.alpha > 0 ? "+" : ""}{data.alpha}% alpha)
                  </span>
                )}</>
              )}
            </div>
          )}

          <div style={{ marginTop:20, background:"#111", border:"1px solid #222", borderRadius:12, padding:16 }}>
            <p style={{ fontSize:12, color:"#555", marginBottom:12, fontWeight:600, textTransform:"uppercase", letterSpacing:"0.06em" }}>Fund Stats</p>
            <StatRow label="Price / NAV"        value={data.price ? `$${data.price.toFixed(2)}` : null} />
            <StatRow label="Total Assets (AUM)" value={fmt(data.total_assets, "aum")} />
            <StatRow label="Expense Ratio"      value={fmt(data.expense_ratio, "ratio")} />
            <StatRow label="3-Year Return"      value={fmt(data.three_year_return, "pct")} />
            <StatRow label="S&P 500 3-Year"     value={data.sp500_3yr_return != null ? `${data.sp500_3yr_return > 0 ? "+" : ""}${data.sp500_3yr_return}%` : null} />
            <StatRow label="Alpha (3yr)"        value={data.alpha != null ? `${data.alpha > 0 ? "+" : ""}${data.alpha}%` : null} />
            <StatRow label="5-Year Return"      value={fmt(data.five_year_return, "pct")} />
            <StatRow label="YTD Return"         value={fmt(data.ytd_return, "pct")} />
            <StatRow label="Dividend Yield"     value={fmt(data.dividend_yield, "pct")} />
            <StatRow label="Beta"               value={data.beta?.toFixed(2)} />
          </div>
        </div>
      )}
    </div>
  )
}
