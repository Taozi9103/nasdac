import { useEffect, useState } from 'react';
import { Info } from 'lucide-react';

interface PortfolioData {
  assets: any[];
  returns: any;
  correlations: any[];
}

interface CorrelationAnalysisProps {
  data: PortfolioData;
}

const CorrelationAnalysis = ({ data }: CorrelationAnalysisProps) => {
  const [correlationMatrix, setCorrelationMatrix] = useState<number[][]>([]);

  useEffect(() => {
    if (data.assets.length > 0) {
      // 生成模拟的相关性矩阵
      const n = data.assets.length;
      const matrix: number[][] = [];
      for (let i = 0; i < n; i++) {
        matrix[i] = [];
        for (let j = 0; j < n; j++) {
          if (i === j) {
            matrix[i][j] = 1;
          } else {
            // 生成 -0.3 到 0.8 之间的随机相关性
            matrix[i][j] = parseFloat((Math.random() * 1.1 - 0.3).toFixed(2));
            matrix[j][i] = matrix[i][j]; // 保持对称性
          }
        }
      }
      setCorrelationMatrix(matrix);
    }
  }, [data.assets]);

  const getCorrelationColor = (value: number) => {
    if (value >= 0.7) return 'bg-red-500';
    if (value >= 0.4) return 'bg-red-300';
    if (value >= 0.1) return 'bg-yellow-200';
    if (value >= -0.1) return 'bg-slate-100';
    if (value >= -0.4) return 'bg-blue-200';
    return 'bg-blue-500';
  };

  const getTextColor = (value: number) => {
    if (Math.abs(value) >= 0.7) return 'text-white';
    return 'text-slate-700';
  };

  if (data.assets.length === 0) {
    return (
      <div className="text-center py-8 text-slate-500">
        请先在「数据对齐」步骤中选择投资标的
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* 说明 */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex gap-3">
          <Info className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">相关性说明</p>
            <p>相关性系数范围为 -1 到 1。数值越接近 1，表示两个标的同向波动越强；越接近 -1，表示反向波动越强；接近 0 表示相关性较弱。</p>
          </div>
        </div>
      </div>

      {/* 相关性热力图 */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-4">相关性矩阵</h3>
        <div className="overflow-x-auto">
          <div className="inline-block min-w-full">
            <table className="text-sm">
              <thead>
                <tr>
                  <th className="p-2 w-24"></th>
                  {data.assets.map((asset) => (
                    <th key={asset.id} className="p-2 font-medium text-slate-700 text-xs">
                      {asset.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.assets.map((rowAsset, i) => (
                  <tr key={rowAsset.id}>
                    <td className="p-2 font-medium text-slate-700 text-xs">
                      {rowAsset.name}
                    </td>
                    {data.assets.map((colAsset, j) => (
                      <td key={`${rowAsset.id}-${colAsset.id}`} className="p-0">
                        <div className={`
                          w-16 h-16 flex items-center justify-center
                          ${getCorrelationColor(correlationMatrix[i]?.[j] || 0)}
                          ${getTextColor(correlationMatrix[i]?.[j] || 0)}
                          font-medium text-sm
                        `}>
                          {correlationMatrix[i]?.[j]?.toFixed(2)}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* 图例 */}
      <div>
        <h3 className="text-sm font-semibold text-slate-700 mb-3">图例</h3>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-6 bg-blue-500 rounded"></div>
            <span className="text-sm text-slate-600">强负相关 (-1 ~ -0.4)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-6 bg-blue-200 rounded"></div>
            <span className="text-sm text-slate-600">负相关 (-0.4 ~ -0.1)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-6 bg-slate-100 rounded"></div>
            <span className="text-sm text-slate-600">弱相关 (-0.1 ~ 0.1)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-6 bg-yellow-200 rounded"></div>
            <span className="text-sm text-slate-600">正相关 (0.1 ~ 0.4)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-6 bg-red-300 rounded"></div>
            <span className="text-sm text-slate-600">较强正相关 (0.4 ~ 0.7)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-6 bg-red-500 rounded"></div>
            <span className="text-sm text-slate-600">强正相关 (0.7 ~ 1)</span>
          </div>
        </div>
      </div>

      {/* 分析建议 */}
      <div className="bg-slate-50 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-slate-700 mb-3">分析建议</h3>
        <ul className="space-y-2 text-sm text-slate-600">
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
            <span>组合中包含不同类型的资产（股票指数、海外ETF等），有助于分散风险</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
            <span>相关性较低的资产组合可以有效降低整体波动率</span>
          </li>
          <li className="flex items-start gap-2">
            <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></span>
            <span>建议避免将过高比例配置在相关性极强的资产上</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default CorrelationAnalysis;
