import { useState } from 'react';
import { Target, TrendingUp, Shield } from 'lucide-react';

interface PortfolioData {
  assets: any[];
  returns: any;
  correlations: any[];
}

interface EfficientFrontierProps {
  data: PortfolioData;
}

const EfficientFrontier = ({ data }: EfficientFrontierProps) => {
  const [selectedPortfolio, setSelectedPortfolio] = useState<'sharpe' | 'minVar' | 'balanced'>('sharpe');

  if (data.assets.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        请先在「数据对齐」步骤中选择投资标的
      </div>
    );
  }

  // 模拟的有效前沿组合数据
  const portfolios = {
    sharpe: {
      name: '最大夏普比率组合',
      description: '在给定风险水平下提供最高预期收益的组合',
      return: 0.152,
      volatility: 0.185,
      sharpe: 0.82,
      allocations: data.assets.map(asset => ({
        ...asset,
        weight: Math.random() * 0.5,
      })),
    },
    minVar: {
      name: '最小方差组合',
      description: '风险最低的有效组合，适合极度风险厌恶的投资者',
      return: 0.085,
      volatility: 0.123,
      sharpe: 0.69,
      allocations: data.assets.map(asset => ({
        ...asset,
        weight: Math.random() * 0.4,
      })),
    },
    balanced: {
      name: '均衡配置组合',
      description: '在风险和收益之间取得平衡的配置',
      return: 0.121,
      volatility: 0.158,
      sharpe: 0.77,
      allocations: data.assets.map(asset => ({
        ...asset,
        weight: 1 / data.assets.length,
      })),
    },
  };

  const currentPortfolio = portfolios[selectedPortfolio];

  // 归一化权重
  const totalWeight = currentPortfolio.allocations.reduce((sum, a) => sum + a.weight, 0);
  const normalizedAllocations = currentPortfolio.allocations.map(a => ({
    ...a,
    weight: a.weight / totalWeight,
  }));

  return (
    <div className="space-y-6">
      {/* 组合选择 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button
          onClick={() => setSelectedPortfolio('sharpe')}
          className={`p-4 rounded-xl border-2 text-left transition-all ${
            selectedPortfolio === 'sharpe'
              ? 'border-blue-500 bg-blue-50'
              : 'border-slate-200 hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-3 mb-2">
            <TrendingUp className={`w-5 h-5 ${selectedPortfolio === 'sharpe' ? 'text-blue-600' : 'text-slate-400'}`} />
            <span className="font-semibold text-slate-900">{portfolios.sharpe.name}</span>
          </div>
          <p className="text-sm text-slate-600">{portfolios.sharpe.description}</p>
        </button>

        <button
          onClick={() => setSelectedPortfolio('minVar')}
          className={`p-4 rounded-xl border-2 text-left transition-all ${
            selectedPortfolio === 'minVar'
              ? 'border-blue-500 bg-blue-50'
              : 'border-slate-200 hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-3 mb-2">
            <Shield className={`w-5 h-5 ${selectedPortfolio === 'minVar' ? 'text-blue-600' : 'text-slate-400'}`} />
            <span className="font-semibold text-slate-900">{portfolios.minVar.name}</span>
          </div>
          <p className="text-sm text-slate-600">{portfolios.minVar.description}</p>
        </button>

        <button
          onClick={() => setSelectedPortfolio('balanced')}
          className={`p-4 rounded-xl border-2 text-left transition-all ${
            selectedPortfolio === 'balanced'
              ? 'border-blue-500 bg-blue-50'
              : 'border-slate-200 hover:border-slate-300'
          }`}
        >
          <div className="flex items-center gap-3 mb-2">
            <Target className={`w-5 h-5 ${selectedPortfolio === 'balanced' ? 'text-blue-600' : 'text-slate-400'}`} />
            <span className="font-semibold text-slate-900">{portfolios.balanced.name}</span>
          </div>
          <p className="text-sm text-slate-600">{portfolios.balanced.description}</p>
        </button>
      </div>

      {/* 组合指标 */}
      <div className="bg-slate-50 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-slate-700 mb-4">{currentPortfolio.name} - 风险收益指标</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold text-slate-900">{(currentPortfolio.return * 100).toFixed(1)}%</p>
            <p className="text-sm text-slate-600">预期年化收益率</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-slate-900">{(currentPortfolio.volatility * 100).toFixed(1)}%</p>
            <p className="text-sm text-slate-600">年化波动率</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-slate-900">{currentPortfolio.sharpe.toFixed(2)}</p>
            <p className="text-sm text-slate-600">夏普比率</p>
          </div>
        </div>
      </div>

      {/* 资产配置 */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-4">资产配置权重</h3>
        <div className="space-y-3">
          {normalizedAllocations.sort((a, b) => b.weight - a.weight).map((allocation, index) => (
            <div key={allocation.id} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-700">{allocation.name}</span>
                <span className="font-medium text-slate-900">{(allocation.weight * 100).toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div
                  className="h-full bg-blue-500 rounded-full transition-all"
                  style={{ width: `${allocation.weight * 100}%` }}
                ></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default EfficientFrontier;
