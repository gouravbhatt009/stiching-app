import React, { useState, useMemo } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer, ScatterChart, Scatter, ZAxis, Cell 
} from 'recharts';
import { Download, Filter, Search, ArrowUpRight, ArrowDownRight, AlertCircle } from 'lucide-react';

// --- MOCK DATA (Simulating your Master vs Salary sheets) ---
const MOCK_STYLES = [
  { id: 'ST-001', name: 'Classic Denim', cost: 450, created: '2026-01-10', masterCost: 420, efficiency: 92, category: 'Bottoms' },
  { id: 'ST-002', name: 'Cotton Tee', cost: 120, created: '2026-01-15', masterCost: 150, efficiency: 110, category: 'Tops' },
  { id: 'ST-003', name: 'Silk Scarf', cost: 890, created: '2026-01-22', masterCost: 850, efficiency: 75, category: 'Accessories' },
  { id: 'ST-004', name: 'Winter Parka', cost: 1200, created: '2026-02-01', masterCost: 1150, efficiency: 88, category: 'Outerwear' },
];

const RECONCILIATION_DATA = {
  'ST-001': {
    karigarSheet: [
      { worker: 'Ahmed', role: 'Stitching', time: '1.2hr', pay: 200 },
      { worker: 'Sita', role: 'Finishing', time: '0.5hr', pay: 100 },
    ],
    masterSheet: [
      { op: 'Fabric', cost: 100 },
      { op: 'Stitching Labor', cost: 180 },
      { op: 'Overhead', cost: 140 },
    ]
  }
};

const CostingDashboard = () => {
  const [selectedStyle, setSelectedStyle] = useState(null);
  const [filter, setFilter] = useState('');

  const filteredStyles = MOCK_STYLES.filter(s => 
    s.name.toLowerCase().includes(filter.toLowerCase()) || s.id.includes(filter)
  );

  return (
    <div className="p-6 bg-gray-50 min-h-screen font-sans">
      {/* HEADER */}
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Style Costing & Reconciliation</h1>
          <p className="text-gray-500">Analyze production variances and master data alignment.</p>
        </div>
        <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          <Download size={18} /> Export Report
        </button>
      </div>

      {/* TOP CHARTS SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Cost Creation Timeline</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={MOCK_STYLES}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="created" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="cost" stroke="#4f46e5" strokeWidth={3} dot={{ r: 6 }} />
                <Line type="monotone" dataKey="masterCost" stroke="#94a3b8" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold mb-4 text-gray-700">Cost Bracket vs Efficiency</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart>
                <XAxis type="number" dataKey="cost" name="Actual Cost" unit="$" />
                <YAxis type="number" dataKey="efficiency" name="Efficiency" unit="%" />
                <ZAxis range={[100, 500]} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Scatter name="Styles" data={MOCK_STYLES}>
                  {MOCK_STYLES.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.efficiency > 100 ? '#22c55e' : '#6366f1'} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* FILTER & LIST */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-100 mb-8">
        <div className="p-4 border-b border-gray-100 flex items-center gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Filter by Style ID or Name..." 
              className="pl-10 pr-4 py-2 w-full border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              onChange={(e) => setFilter(e.target.value)}
            />
          </div>
        </div>

        <table className="w-full text-left">
          <thead>
            <tr className="bg-gray-50 text-gray-600 uppercase text-xs">
              <th className="p-4">Style Info</th>
              <th className="p-4">Actual Cost</th>
              <th className="p-4">Master Cost</th>
              <th className="p-4">Variance</th>
              <th className="p-4">Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredStyles.map(style => (
              <tr key={style.id} className="border-t border-gray-50 hover:bg-gray-50 transition">
                <td className="p-4">
                  <div className="font-bold">{style.name}</div>
                  <div className="text-xs text-gray-400">{style.id} | {style.category}</div>
                </td>
                <td className="p-4 font-semibold">${style.cost}</td>
                <td className="p-4 text-gray-500">${style.masterCost}</td>
                <td className="p-4">
                  {style.cost > style.masterCost ? (
                    <span className="text-red-500 flex items-center gap-1 text-sm">
                      <ArrowUpRight size={14} /> +${style.cost - style.masterCost}
                    </span>
                  ) : (
                    <span className="text-green-500 flex items-center gap-1 text-sm">
                      <ArrowDownRight size={14} /> -${style.masterCost - style.cost}
                    </span>
                  )}
                </td>
                <td className="p-4">
                  <button 
                    onClick={() => setSelectedStyle(style)}
                    className="text-blue-600 hover:underline text-sm font-medium"
                  >
                    View Reconciliation
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* DRILL-DOWN MODAL (Simple overlay) */}
      {selectedStyle && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto p-8 relative">
            <button onClick={() => setSelectedStyle(null)} className="absolute top-4 right-4 text-gray-400 hover:text-black text-xl">×</button>
            <h2 className="text-2xl font-bold mb-2">Reconciliation: {selectedStyle.name}</h2>
            <p className="text-gray-500 mb-6">Auditing Master Data vs. Karigar Salary Sheet</p>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* SALARY SHEET TRACKING */}
              <div>
                <h4 className="font-bold text-gray-700 mb-3 flex items-center gap-2">
                  <AlertCircle size={18} className="text-orange-500" /> Worker (Karigar) Salary Sheet
                </h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  {RECONCILIATION_DATA[selectedStyle.id]?.karigarSheet.map((item, i) => (
                    <div key={i} className="flex justify-between border-b py-2 last:border-0">
                      <span>{item.worker} ({item.role})</span>
                      <span className="font-mono">${item.pay} / {item.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* MASTER SHEET DATA */}
              <div>
                <h4 className="font-bold text-gray-700 mb-3">Master Sheet Components</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  {RECONCILIATION_DATA[selectedStyle.id]?.masterSheet.map((item, i) => (
                    <div key={i} className="flex justify-between border-b py-2 last:border-0">
                      <span>{item.op}</span>
                      <span className="font-mono">${item.cost}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-8 p-4 bg-blue-50 text-blue-800 rounded-xl">
              <strong>Observation:</strong> This style's stitching cost exceeded the master sheet by 11% due to increased time taken in the finishing step.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CostingDashboard;
