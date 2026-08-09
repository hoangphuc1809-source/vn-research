import { useEffect, useState } from 'react'

export default function Watchlist() {
  const [symbols, setSymbols] = useState('VNM,FPT,VCB,ACB,MBB')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)

  const load = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/stock/VNM/price-board?symbols=${encodeURIComponent(symbols)}`)
      const json = await res.json()
      setData(json.data)
    } catch (e) {
      setData({ error: e.message })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [symbols])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-white">Watchlist</h2>
      <div className="flex gap-2">
        <input
          className="flex-1 bg-slate-800 border border-slate-700 rounded px-3 py-2 text-white"
          value={symbols}
          onChange={e => setSymbols(e.target.value)}
          placeholder="VNM,FPT,VCB"
        />
        <button onClick={load} className="bg-sky-600 hover:bg-sky-500 text-white px-4 py-2 rounded">
          Refresh
        </button>
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
