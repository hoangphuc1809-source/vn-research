import { useEffect, useState } from 'react'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [vn30Res, symbolsRes] = await Promise.all([
          fetch('/api/symbols/group/VN30').then(r => r.json()),
          fetch('/api/symbols').then(r => r.json())
        ])
        setData({ vn30: vn30Res.data, symbols: symbolsRes.data })
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return <div className="text-slate-400">Loading market data...</div>
  if (error) return <div className="text-red-400">Error: {error}</div>

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">Market Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-800 rounded p-4 border border-slate-700">
          <div className="text-slate-400 text-sm">VN30 Symbols</div>
          <div className="text-2xl font-bold text-sky-400">{data?.vn30?.length ?? 0}</div>
        </div>
        <div className="bg-slate-800 rounded p-4 border border-slate-700">
          <div className="text-slate-400 text-sm">Total Listed</div>
          <div className="text-2xl font-bold text-sky-400">{data?.symbols?.length ?? 0}</div>
        </div>
        <div className="bg-slate-800 rounded p-4 border border-slate-700">
          <div className="text-slate-400 text-sm">Data Source</div>
          <div className="text-2xl font-bold text-sky-400">VCI</div>
        </div>
      </div>
      <div className="bg-slate-800 rounded border border-slate-700 p-4">
        <h3 className="text-lg font-semibold mb-3 text-white">VN30 Members</h3>
        <div className="overflow-auto max-h-96">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="text-slate-400 border-b border-slate-700">
                <th className="py-2">Symbol</th>
                <th className="py-2">Name</th>
              </tr>
            </thead>
            <tbody>
              {(data?.vn30 ?? []).map((item, i) => (
                <tr key={i} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-2 font-mono text-sky-300">{item.symbol}</td>
                  <td className="py-2 text-slate-300">{item.organ_name}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
