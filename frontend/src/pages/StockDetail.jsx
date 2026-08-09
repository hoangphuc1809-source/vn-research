import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

export default function StockDetail() {
  const { symbol } = useParams()
  const [tab, setTab] = useState('overview')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const endpoints = {
        overview: `/api/stock/${symbol}/overview`,
        history: `/api/stock/${symbol}/history?start=2025-01-01`,
        intraday: `/api/stock/${symbol}/intraday`,
        depth: `/api/stock/${symbol}/depth`,
        shareholders: `/api/stock/${symbol}/shareholders`,
        officers: `/api/stock/${symbol}/officers`,
        news: `/api/stock/${symbol}/news`,
        events: `/api/stock/${symbol}/events`,
        'financials/balance-sheet': `/api/stock/${symbol}/financials/balance-sheet`,
        'financials/income': `/api/stock/${symbol}/financials/income`,
        'financials/cashflow': `/api/stock/${symbol}/financials/cashflow`,
        'financials/ratios': `/api/stock/${symbol}/financials/ratios`,
      }
      const res = await fetch(endpoints[tab] || endpoints.overview)
      const json = await res.json()
      setData(json.data)
    } catch (e) {
      setData({ error: e.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [symbol, tab])

  const tabs = [
    ['overview', 'Overview'],
    ['history', 'History'],
    ['intraday', 'Intraday'],
    ['depth', 'Depth'],
    ['shareholders', 'Shareholders'],
    ['officers', 'Officers'],
    ['news', 'News'],
    ['events', 'Events'],
    ['financials/balance-sheet', 'Balance Sheet'],
    ['financials/income', 'Income'],
    ['financials/cashflow', 'Cashflow'],
    ['financials/ratios', 'Ratios'],
  ]

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white">Stock: {symbol}</h2>
      <div className="flex flex-wrap gap-2">
        {tabs.map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`px-3 py-1 rounded text-sm ${tab === key ? 'bg-sky-600 text-white' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
          >
            {label}
          </button>
        ))}
      </div>
      {loading && <div className="text-slate-400">Loading...</div>}
      {data && (
        <div className="bg-slate-800 rounded border border-slate-700 p-4 overflow-auto">
          <pre className="text-xs text-slate-300">{JSON.stringify(data, null, 2)}</pre>
        </div>
      )}
    </div>
  )
}
