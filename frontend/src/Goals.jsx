import { useState } from "react"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

const GOALS = [
  {
    id:          "growth",
    label:       "Growth",
    icon:        "🚀",
    description: "Stocks with the strongest growth potential and upward momentum",
    color:       "#4ade80",
    darkText:    true,
  },
  {
    id:          "passive_income",
    label:       "Passive Income",
    icon:        "💰",
    description: "High-dividend stocks and ETFs that pay you regularly",
    color:       "#f59e0b",
    darkText:    true,
  },
  {
    id:          "balanced",
    label:       "Balanced",
    icon:        "⚖️",
    description: "A mix of stability, income and steady long-term growth",
    color:       "#818cf8",
    darkText:    false,
  },
  {
    id:          "value",
    label:       "Value Investing",
    icon:        "💎",
    description: "Undervalued stocks with low P/E ratios and strong fundamentals",
    color:       "#f97316",
    darkText:    true,
  },
  {
    id:          "international",
    label:       "International",
    icon:        "🌍",
    description: "Top companies outside the U.S. — diversify your portfolio globally",
    color:       "#38bdf8",
    darkText:    true,
  },
  {
    id:          "consumer_staples",
    label:       "Consumer Staples",
    icon:        "🛒",
    description: "Everyday consumer goods companies with stable, defensive returns",
    color:       "#a78bfa",
    darkText:    false,
  },
]

function ScoreChip({ score }) {
  const bg    = score >= 70 ? "#14532d" : score >= 50 ? "#422006" : "#450a0a"
  const color = score >= 70 ? "#4ade80" : score >= 50 ? "#f59e0b" : "#f87171"
  return (
    <span style={{ background: bg, color, padding: "3px 10px", borderRadius: 99, fontWeight: 700, fontSize: 13 }}>
      {score}
    </span>
  )
}

export default function Goals() {
  const [goal,    setGoal]    = useState(null)
  const [amount,  setAmount]  = useState("")
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState("")

  async function getRecommendations() {
    if (!goal || !amount) return
    setLoading(true)
    setError("")
    setResults(null)
    try {
      const res  = await fetch(`${API}/recommend?goal=${goal}&amount=${amount}`)
      const data = await res.json()
      if (data.detail) throw new Error(data.detail)
      setResults(data)
    } catch {
      setError("Something went wrong. Please try again.")
    }
    setLoading(false)
  }

  const selectedGoal = GOALS.find(g => g.id === goal)

  return (
    <div>
      <h2 style={{ fontSize: 20, fontWeight: 800, marginBottom: 4 }}>Investment Goals</h2>
      <p style={{ color: "#666", fontSize: 13, marginBottom: 24 }}>
        Tell us what you're looking for and how much you want to invest — we'll score and rank the best options.
      </p>

      {/* Goal cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 24 }}>
        {GOALS.map(g => (
          <div key={g.id} onClick={() => setGoal(g.id)} style={{
            border:        `2px solid ${goal === g.id ? g.color : "#222"}`,
            background:    goal === g.id ? `${g.color}18` : "#111",
            borderRadius:  12,
            padding:       16,
            cursor:        "pointer",
            transition:    "border-color 0.15s",
          }}>
            <div style={{ fontSize: 28, marginBottom: 6 }}>{g.icon}</div>
            <div style={{ fontWeight: 700, fontSize: 14, color: goal === g.id ? g.color : "#fff", marginBottom: 4 }}>
              {g.label}
            </div>
            <div style={{ fontSize: 12, color: "#555", lineHeight: 1.4 }}>{g.description}</div>
          </div>
        ))}
      </div>

      {/* Amount input */}
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <div style={{ position: "relative", flex: 1 }}>
          <span style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#555", fontSize: 16 }}>$</span>
          <input
            type="number"
            min="1"
            value={amount}
            onChange={e => setAmount(e.target.value)}
            onKeyDown={e => e.key === "Enter" && getRecommendations()}
            placeholder="Amount to invest (e.g. 5000)"
            style={{ width: "100%", padding: "12px 16px 12px 28px", fontSize: 15, background: "#111", border: "1px solid #333", borderRadius: 8, color: "#fff", boxSizing: "border-box" }}
          />
        </div>
        <button
          onClick={getRecommendations}
          disabled={!goal || !amount || loading}
          style={{
            padding:       "12px 24px",
            fontSize:      15,
            background:    !goal || !amount ? "#1a1a1a" : selectedGoal?.color || "#4ade80",
            border:        "none",
            borderRadius:  8,
            fontWeight:    700,
            cursor:        !goal || !amount ? "not-allowed" : "pointer",
            color:         selectedGoal?.darkText ? "#000" : "#fff",
            whiteSpace:    "nowrap",
          }}>
          {loading ? "Analysing..." : "Get Recommendations"}
        </button>
      </div>

      {!goal && <p style={{ fontSize: 12, color: "#444", marginBottom: 16 }}>Pick a goal above first</p>}

      {loading && (
        <p style={{ color: "#555", fontSize: 13, marginTop: 16 }}>
          Scoring candidates across the market — this takes about 30 seconds...
        </p>
      )}

      {error && <p style={{ color: "#f87171", fontSize: 13, marginTop: 12 }}>{error}</p>}

      {results && results.recommendations.length > 0 && (
        <div style={{ marginTop: 28 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: 16 }}>
            <h3 style={{ fontSize: 16, fontWeight: 800, margin: 0 }}>
              Top picks for <span style={{ color: selectedGoal?.color }}>{selectedGoal?.label}</span>
            </h3>
            <span style={{ fontSize: 13, color: "#555" }}>
              ${Number(results.amount).toLocaleString()} to invest
            </span>
          </div>

          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ borderBottom: "1px solid #222", color: "#555", textAlign: "left" }}>
                <th style={{ padding: "8px 0" }}>Rank</th>
                <th>Ticker</th>
                <th>Name</th>
                <th>Category</th>
                <th>Score</th>
                <th style={{ textAlign: "right" }}>Allocation</th>
                <th style={{ textAlign: "right" }}>Shares</th>
              </tr>
            </thead>
            <tbody>
              {results.recommendations.map((r, i) => (
                <tr key={r.ticker} style={{ borderBottom: "1px solid #111" }}>
                  <td style={{ padding: "12px 0", color: "#555" }}>#{i + 1}</td>
                  <td>
                    <span style={{ fontWeight: 700, color: selectedGoal?.color }}>{r.ticker}</span>
                    <span style={{
                      marginLeft: 6, fontSize: 10, padding: "1px 6px", borderRadius: 4,
                      background: r.type === "ETF" ? "rgba(56,189,248,0.15)" : "rgba(74,222,128,0.1)",
                      color:      r.type === "ETF" ? "#38bdf8" : "#4ade80",
                    }}>{r.type}</span>
                  </td>
                  <td style={{ color: "#ccc", maxWidth: 180, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {r.name}
                  </td>
                  <td style={{ color: "#555" }}>{r.category}</td>
                  <td><ScoreChip score={r.total_score} /></td>
                  <td style={{ textAlign: "right", color: "#fff", fontWeight: 600 }}>
                    ${r.allocation?.toLocaleString()}
                  </td>
                  <td style={{ textAlign: "right", color: "#555" }}>
                    {r.shares > 0 ? `~${r.shares}` : "<1"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <p style={{ fontSize: 11, color: "#333", marginTop: 20, lineHeight: 1.5 }}>
            Allocation is score-weighted across top picks. For educational purposes only — not financial advice.
          </p>
        </div>
      )}
    </div>
  )
}
