import { useState } from 'react';
import { PieChart, TrendingUp, Download, Save, RefreshCw } from 'lucide-react';

interface PortfolioData {
  assets: any[];
  returns: any;
  correlations: any[];
}

interface RiskReturnProps {
  data: PortfolioData;
}

const RiskReturn = ({ data }: RiskReturnProps) => {
  const [weights, setWeights] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {};
    const equalWeight = data.assets.length > 0 ? 1 / data.assets.length : 0;
    data.assets.forEach(asset => {
      initial[asset.id] = equalWeight;
    });
    return initial;
  });

  if (data.assets.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        请先在「数据对齐」步骤中选择投资标的
      </div>
    );
  }

  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);

  const updateWeight = (assetId: string, newWeight: number) => {
    setWeights(prev => ({
      ...prev,
      [assetId]: Math.max(0, newWeight),
    }));
  };

  const normalizeWeights = () => {
    const sum = Object.values(weights).reduce((s, w) => s + w, 0);
    if (sum > 0) {
      const normalized: Record<string, number> = {};
      Object.entries(weights).forEach(([id, w]) => {
        normalized[id] = w / sum;
      });
      setWeights(normalized);
    }
  };

  // 模拟组合指标计算
  const portfolioReturn = data.assets.reduce((sum, asset) => {
    const assetReturn = (Math.random() * 0.3 - 0.05);
    return sum + (weights[asset.id] || 0) * assetReturn;
  }, 0);

  const portfolioVolatility = 0.1 + Math.random() * 0.15;

  return (
    <div className="space-y-6">
      {/* 配置说明 */}
      <div className="bg-green-50 border border-green-200 rounded-xl p-4">
        <div className="flex gap-3">
          <Save className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-green-800">
            <p className="font-medium mb-1">配置完成</p>
            <p>您可以手动调整各资产的配置权重，或保存当前配置用于后续的回测分析。</p>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* 权重调整 */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-4">权重配置</h3>
          <div className="space-y-4">
            {data.assets.map(asset => (
              <div key={asset.id} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-slate-900">{asset.name}</span>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      value={(weights[asset.id] * 100).toFixed(1)}
                      onChange={(e) => updateWeight(asset.id, parseFloat(e.target.value) / 100)}
                      min="0"
                      max="100"
                      className="w-20 px-2 py-1 border border-slate-300 rounded text-sm text-right"
                    />
                    <span className="text-sm text-slate-600">%</span>
                  </div>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={weights[asset.id] || 0}
                  onChange={(e) => updateWeight(asset.id, parseFloat(e.target.value))}
                  className="w-full"
                />
              </div>
            ))}
          </div>
          
          <div className="mt-4 flex items-center justify-between">
            <div className={`text-sm font-medium ${Math.abs(totalWeight - 1) < 0.01 ? 'text-green-600' : 'text-orange-600'}`}>
              合计: {(totalWeight * 100).toFixed(1)}%
              {Math.abs(totalWeight - 1) >= 0.01 && ' (需归一化)'}
            </div>
            <button
              onClick={normalizeWeights}
              className="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm text-slate-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              归一化
            </button>
          </div>
        </div>

        {/* 组合概览 */}
        <div>
          <h3 className="text-sm font-semibold text-slate-700 mb-4">组合概览</h3>
          
          {/* 风险收益指标 */}
          <div className="bg-slate-50 rounded-xl p-4 mb-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-slate-900">{(portfolioReturn * 100).toFixed(1)}%</p>
                <p className="text-sm text-slate-600">预期年化收益</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-slate-900">{(portfolioVolatility * 100).toFixed(1)}%</p>
                <p className="text-sm text-slate-600">预期波动率</p>
              </div>
            </div>
          </div>

          {/* 可视化饼图占位 */}
          <div className="border-2 border-dashed border-slate-200 rounded-xl p-6 text-center">
            <PieChart className="w-12 h-12 text-slate-300 mx-auto mb-3" />
            <p className="text-sm text-slate-500">资产配置可视化</p>
            <p className="text-xs text-slate-400 mt-1">（可集成 ECharts 或 Recharts 实现）</p>
          </div>
        </div>
      </div>

      {/* 操作按钮 */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-200">
        <button className="flex items-center gap-2 px-6 py-2.5 bg-blue-500 hover:bg-blue-600 text-white rounded-lg text-sm font-medium transition-colors">
          <Save className="w-4 h-4" />
          保存配置
        </button>
        <button className="flex items-center gap-2 px-6 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-colors">
          <Download className="w-4 h-4" />
          导出报告
        </button>
        <button className="flex items-center gap-2 px-6 py-2.5 bg-green-500 hover:bg-green-600 text-white rounded-lg text-sm font-medium transition-colors">
          <TrendingUp className="w-4 h-4" />
          开始回测
        </button>
      </div>
    </div>
  );
};

export default RiskReturn;
