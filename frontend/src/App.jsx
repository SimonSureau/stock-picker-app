import { useState } from "react"
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"

const API = "http://localhost:8000"

export default function App() {
  const [ticker, setTicker] = useState("")
  const [quote, setQuote] = useState(null)
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)

  async function search() {
    setLoading(true)
    const [q, h] = await Promise.all([
      fetch(`${API}/quote/${ticker}`).then(r => r.json()),
      fetch(`${API}/history/${ticker}`).then(r => r.json()),
    ])
    setQuote(q)
    setHistory(h.prices)
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 800, margin: "40px auto", padding: "0 20px", fontFamily: "sans-serif" }}>
      <h1>📈 Stock Picker</h1>

      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        <input
          value={ticker}
          onChange={e => setTicker(e.target.value)}
          placeholder="Enter ticker (e.g. AAPL)"
          style={{ flex: 1, padding: "10px 14px", fontSize: 16 }}
        />
        <button onClick={search} style={{ padding: "10px 24px", fontSize: 16 }}>
          {loading ? "Loading..." : "Search"}
        </button>
      </div>

      {quote && (
        <>
          <h2>{quote.name} ({quote.ticker})</h2>
          <p>Price: ${quote.price}   P/E: {quote.pe_ratio?.toFixed(1)}</p>

          <h3>1-Year Price History</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={history}>
              <XAxis dataKey="date" tick={{ fontSize: 10 }} tickCount={6} />
              <YAxis domain={["auto", "auto"]} />
              <Tooltip />
              <Line type="monotone" dataKey="close" dot={false} stroke="#4ade80" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  )
}