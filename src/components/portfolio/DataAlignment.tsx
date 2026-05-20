import { useState } from 'react';
import { Plus, X, Search, Calendar, TrendingUp } from 'lucide-react';

// 模拟数据 - 可选的投资标的
const availableAssets = [
  { id: 'CSI000300', name: '沪深300', type: '指数', code: 'CSI000300' },
  { id: 'SZ399006', name: '创业板指', type: '指数', code: 'SZ399006' },
  { id: 'SH000688', name: '科创50', type: '指数', code: 'SH000688' },
  { id: '000001', name: '华夏成长混合', type: '基金', code: '000001' },
  { id: '161725', name: '招商中证白酒指数', type: '基金', code: '161725' },
  { id: '007339', name: '易方达中小盘混合', type: '基金', code: '007339' },
  { id: '513100', name: '纳斯达克100ETF', type: '基金', code: '513100' },
  { id: '518880', name: '黄金ETF', type: '基金', code: '518880' },
];

interface PortfolioData {
  assets: any[];
  returns: any;
  correlations: any[];
}

interface DataAlignmentProps {
  onDataUpdate: (data: PortfolioData) => void;
  data: PortfolioData;
}

const DataAlignment = ({ onDataUpdate, data }: DataAlignmentProps) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedAssets, setSelectedAssets] = useState<any[]>([
    availableAssets[0],
    availableAssets[1],
    availableAssets[6],
  ]);
  const [startDate, setStartDate] = useState('2020-01-01');
  const [endDate, setEndDate] = useState('2025-05-16');

  const filteredAssets = availableAssets.filter(asset =>
    asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    asset.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const addAsset = (asset: any) => {
    if (!selectedAssets.find(a => a.id === asset.id)) {
      const newAssets = [...selectedAssets, asset];
      setSelectedAssets(newAssets);
      updateData(newAssets);
    }
  };

  const removeAsset = (assetId: string) => {
    const newAssets = selectedAssets.filter(a => a.id !== assetId);
    setSelectedAssets(newAssets);
    updateData(newAssets);
  };

  const updateData = (assets: any[]) => {
    // 模拟生成收益率数据
    const mockReturns: any = {};
    assets.forEach(asset => {
      mockReturns[asset.id] = {
        name: asset.name,
        annualReturn: (Math.random() * 0.3 - 0.05).toFixed(4),
        volatility: (Math.random() * 0.3 + 0.1).toFixed(4),
      };
    });

    onDataUpdate({
      assets,
      returns: mockReturns,
      correlations: [],
    });
  };

  return (
    <div className="space-y-6">
      {/* 日期选择 */}
      <div className="bg-slate-50 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          时间范围
        </h3>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
          <label className="text-sm text-slate-600">开始日期</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
          />
          </div>
          <div className="flex items-center gap-2">
          <label className="text-sm text-slate-600">结束日期</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
          />
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* 可选标的 */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-3">可选标的</h3>
          <div className="relative mb-3">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="搜索标的名称或代码..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg text-sm"
            />
          </div>
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <div className="max-h-64 overflow-y-auto">
              {filteredAssets.map(asset => (
                <button
                  key={asset.id}
                  onClick={() => addAsset(asset)}
                  disabled={selectedAssets.find(a => a.id === asset.id)}
                  className="w-full text-left px-4 py-3 hover:bg-slate-50 border-b border-slate-100 last:border-b-0 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-slate-900">{asset.name}</p>
                      <p className="text-xs text-slate-500">{asset.code} · {asset.type}</p>
                    </div>
                    {selectedAssets.find(a => a.id === asset.id) ? (
                      <span className="text-xs text-blue-600">已添加</span>
                    ) : (
                      <Plus className="w-4 h-4 text-slate-400" />
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* 已选标的 */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-3">已选标的 ({selectedAssets.length})</h3>
          {selectedAssets.length === 0 ? (
            <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center">
              <p className="text-slate-500 text-sm">请从左侧添加投资标的</p>
            </div>
          ) : (
            <div className="space-y-2">
              {selectedAssets.map(asset => (
                <div key={asset.id} className="flex items-center justify-between bg-slate-50 rounded-lg px-4 py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                      <TrendingUp className="w-4 h-4 text-blue-600" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-slate-900">{asset.name}</p>
                      <p className="text-xs text-slate-500">{asset.code}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeAsset(asset.id)}
                    className="p-1 hover:bg-slate-200 rounded transition-colors"
                  >
                    <X className="w-4 h-4 text-slate-400" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* 数据预览 */}
      {selectedAssets.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-3">数据预览</h3>
          <div className="overflow-x-auto border border-slate-200 rounded-xl">
            <table className="w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-3 text-left font-medium text-slate-700">标的名称</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-700">代码</th>
                  <th className="px-4 py-3 text-left font-medium text-slate-700">类型</th>
                  <th className="px-4 py-3 text-right font-medium text-slate-700">年化收益 (模拟)</th>
                  <th className="px-4 py-3 text-right font-medium text-slate-700">波动率 (模拟)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {selectedAssets.map(asset => {
                  const returns = data.returns[asset.id];
                  return (
                    <tr key={asset.id}>
                      <td className="px-4 py-3 text-slate-900">{asset.name}</td>
                      <td className="px-4 py-3 text-slate-600">{asset.code}</td>
                      <td className="px-4 py-3 text-slate-600">{asset.type}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{returns ? `${(parseFloat(returns.annualReturn) * 100).toFixed(2)}%` : '-'}</td>
                      <td className="px-4 py-3 text-right text-slate-900">{returns ? `${(parseFloat(returns.volatility) * 100).toFixed(2)}%` : '-'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataAlignment;
