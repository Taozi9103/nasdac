"""
大类资产风险平价目标波动率15%策略 - 本地回测版本
使用akshare获取真实市场数据

策略: Risk Parity with Target Volatility 15%
资产: 沪深300、中证500、国债指数、黄金ETF、原油基金
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

try:
    import akshare as ak
    print("✓ akshare 已安装")
except ImportError:
    print("正在安装 akshare...")
    import subprocess
    subprocess.check_call(['pip3', 'install', 'akshare', '-q'])
    import akshare as ak
    print("✓ akshare 安装完成")


class RiskParityStrategy:
    """风险平价策略回测类"""
    
    def __init__(self):
        self.initial_capital = 1000000
        self.target_volatility = 0.15
        self.lookback_period = 60
        self.rebalance_period = 20
        
        self.assets = {
            'stock_hs300': '000300.XSHG',
            'stock_zz500': '000905.XSHG',
            'bond': 'H11001.XSHG',
            'gold': '518880.XSHG',
            'oil': '160416.XSHG',
        }
        
        self.data = None
        self.returns = None
        self.portfolio_value = None
        self.weights_history = None
        self.trades = []
    
    def fetch_data(self, start_date='20190101', end_date='20250530'):
        """获取历史数据"""
        print("\n" + "="*60)
        print("正在获取市场数据...")
        print("="*60)
        
        data_dict = {}
        
        symbols = {
            'stock_hs300': 'sh000300',
            'stock_zz500': 'sh000905',
            'bond': 'sh000012',
            'gold': 'sh518880',
            'oil': 'lof_160416',
        }
        
        for name, symbol in symbols.items():
            try:
                print(f"  获取 {name} ({symbol})...")
                
                if name in ['stock_hs300', 'stock_zz500', 'bond']:
                    df = ak.stock_zh_index_daily(symbol=symbol)
                    df['date'] = pd.to_datetime(df['date'])
                    df = df.set_index('date')
                    data_dict[name] = df['close']
                elif name == 'gold':
                    df = ak.fund_etf_hist_em(symbol='518880', period="daily", start_date=start_date, end_date=end_date)
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.set_index('日期')
                    data_dict[name] = df['收盘']
                elif name == 'oil':
                    df = ak.fund_open_fund_info_em(symbol='160416', indicator="累计净值走势")
                    df['日期'] = pd.to_datetime(df['日期'])
                    df = df.set_index('日期')
                    data_dict[name] = df['累计净值']
                
                print(f"    ✓ 成功获取 {len(data_dict[name])} 条数据")
                
            except Exception as e:
                print(f"    ✗ 获取失败: {e}")
                data_dict[name] = pd.Series()
        
        self.data = pd.DataFrame(data_dict)
        self.data = self.data.dropna()
        self.data = self.data.sort_index()
        
        print(f"\n数据时间范围: {self.data.index[0]} 至 {self.data.index[-1]}")
        print(f"总交易日数: {len(self.data)}")
        
        self.returns = self.data.pct_change().dropna()
        
        return self.data
    
    def calculate_risk_parity_weights(self, cov_matrix, asset_keys):
        """计算风险平价权重"""
        n_assets = len(cov_matrix)
        
        def risk_contribution(weights, cov):
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
            marginal_risk = np.dot(cov, weights)
            risk_contrib = weights * marginal_risk / portfolio_vol
            return risk_contrib
        
        def risk_parity_objective(weights, cov):
            target_risk = np.sum(risk_contribution(weights, cov)) / len(weights)
            actual_risks = risk_contribution(weights, cov)
            return np.sum((actual_risks - target_risk) ** 2)
        
        w0 = np.array([1.0/n_assets] * n_assets)
        cov_array = cov_matrix.values
        
        constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
        bounds = [(0.0, 0.4) for _ in range(n_assets)]
        
        try:
            result = minimize(
                risk_parity_objective,
                w0,
                args=(cov_array,),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000}
            )
            weights = result.x if result.success else w0
        except:
            weights = w0
        
        weight_dict = {k: weights[i] for i, k in enumerate(asset_keys)}
        return weight_dict
    
    def calculate_portfolio_volatility(self, weights, cov_matrix):
        """计算组合波动率"""
        weight_array = np.array(list(weights.values()))
        cov_array = cov_matrix.values
        portfolio_vol = np.sqrt(np.dot(weight_array.T, np.dot(cov_array, weight_array)))
        return portfolio_vol
    
    def run_backtest(self):
        """运行回测"""
        print("\n" + "="*60)
        print("开始运行回测...")
        print("="*60)
        
        if self.data is None:
            print("错误: 请先调用 fetch_data() 获取数据")
            return
        
        dates = self.data.index
        n_days = len(dates)
        
        portfolio_values = [self.initial_capital]
        weights_history = []
        
        current_weights = {k: 1.0/len(self.assets) for k in self.assets.keys()}
        
        for i in range(1, n_days):
            if i < self.lookback_period:
                weights_history.append(current_weights)
                portfolio_values.append(portfolio_values[-1])
                continue
            
            if (i - self.lookback_period) % self.rebalance_period == 1 or (i - self.lookback_period) == 1:
                lookback_data = self.returns.iloc[i-self.lookback_period:i]
                cov_matrix = lookback_data.cov()
                
                asset_keys = list(self.assets.keys())
                risk_parity_weights = self.calculate_risk_parity_weights(cov_matrix, asset_keys)
                
                current_volatility = self.calculate_portfolio_volatility(risk_parity_weights, cov_matrix)
                
                if current_volatility > 0:
                    vol_adjustment = self.target_volatility / current_volatility
                    vol_adjustment = min(max(vol_adjustment, 0.5), 2.0)
                else:
                    vol_adjustment = 1.0
                
                current_weights = {k: v * vol_adjustment for k, v in risk_parity_weights.items()}
                total_weight = sum(current_weights.values())
                if total_weight > 0:
                    current_weights = {k: v/total_weight for k, v in current_weights.items()}
                
                self.trades.append({
                    'date': dates[i],
                    'weights': current_weights.copy(),
                    'volatility': current_volatility
                })
            else:
                weights_history.append(current_weights)
            
            daily_returns = self.returns.iloc[i]
            portfolio_return = sum(current_weights[k] * daily_returns[k] for k in self.assets.keys())
            new_value = portfolio_values[-1] * (1 + portfolio_return)
            portfolio_values.append(new_value)
        
        self.portfolio_value = pd.Series(portfolio_values, index=dates[:len(portfolio_values)])
        self.weights_history = pd.DataFrame(weights_history, index=dates[:len(weights_history)])
        
        print(f"✓ 回测完成")
        print(f"  总交易日: {n_days}")
        print(f"  调仓次数: {len(self.trades)}")
        
        return self.portfolio_value
    
    def calculate_metrics(self):
        """计算绩效指标"""
        if self.portfolio_value is None:
            return None
        
        returns = self.portfolio_value.pct_change().dropna()
        
        total_return = (self.portfolio_value[-1] / self.portfolio_value[0] - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(returns)) - 1) * 100
        
        annual_volatility = returns.std() * np.sqrt(252) * 100
        
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        cumulative_returns = (1 + returns).cumprod() - 1
        peak = self.portfolio_value.expanding().max()
        drawdown = (self.portfolio_value - peak) / peak
        max_drawdown = drawdown.min() * 100
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_value': self.portfolio_value[-1],
            'cumulative_returns': cumulative_returns,
            'drawdown': drawdown
        }
    
    def generate_report(self):
        """生成回测报告"""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*60)
        print("              回 测 报 告")
        print("="*60)
        
        print(f"\n{'策略名称:':<20} {'风险平价目标波动率15%策略':>25}")
        print(f"{'回测期间:':<20} {self.data.index[0].strftime('%Y-%m-%d')} 至 {self.data.index[-1].strftime('%Y-%m-%d'):>25}")
        print(f"{'初始资金:':<20} {self.initial_capital:>25,.2f}")
        
        print(f"\n{'-'*60}")
        print("                       核心指标")
        print(f"{'-'*60}")
        
        print(f"{'总收益率:':<20} {metrics['total_return']:>15.2f} %")
        print(f"{'年化收益率:':<20} {metrics['annual_return']:>15.2f} %")
        print(f"{'年化波动率:':<20} {metrics['annual_volatility']:>15.2f} %")
        print(f"{'夏普比率:':<20} {metrics['sharpe_ratio']:>15.2f}")
        print(f"{'最大回撤:':<20} {metrics['max_drawdown']:>15.2f} %")
        print(f"{'最终资产:':<20} {metrics['final_value']:>15,.2f}")
        
        print(f"\n{'-'*60}")
        print("                       交易统计")
        print(f"{'-'*60}")
        
        print(f"{'调仓次数:':<20} {len(self.trades):>15}")
        print(f"{'平均持仓天数:':<20} {len(self.portfolio_value)/len(self.trades) if self.trades else 0:>15.1f}")
        
        print("\n" + "="*60)
        
        return metrics
    
    def plot_results(self):
        """绘制结果图表"""
        metrics = self.calculate_metrics()
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        fig.suptitle('Risk Parity Strategy with Target Volatility 15%\nBacktest Results', fontsize=16, fontweight='bold')
        
        ax1 = axes[0]
        ax1.plot(self.portfolio_value.index, self.portfolio_value.values, 'b-', linewidth=2, label='Portfolio Value')
        ax1.set_title('Portfolio Value Over Time', fontsize=14)
        ax1.set_ylabel('Value (CNY)')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        ax1.set_xlim(self.portfolio_value.index[0], self.portfolio_value.index[-1])
        
        y_min = self.portfolio_value.min() * 0.95
        y_max = self.portfolio_value.max() * 1.05
        ax1.set_ylim(y_min, y_max)
        
        ax2 = axes[1]
        ax2.fill_between(metrics['drawdown'].index, metrics['drawdown'].values * 100, 0, alpha=0.3, color='red')
        ax2.plot(metrics['drawdown'].index, metrics['drawdown'].values * 100, 'r-', linewidth=1)
        ax2.set_title('Drawdown Over Time', fontsize=14)
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(metrics['drawdown'].index[0], metrics['drawdown'].index[-1])
        
        ax3 = axes[2]
        if len(self.trades) > 0:
            weights_df = pd.DataFrame([t['weights'] for t in self.trades])
            colors = plt.cm.Set2(np.linspace(0, 1, len(weights_df.columns)))
            ax3.stackplot(range(len(weights_df)), 
                         weights_df.T.values,
                         labels=weights_df.columns,
                         colors=colors,
                         alpha=0.8)
            ax3.set_title('Portfolio Weights Over Time', fontsize=14)
            ax3.set_ylabel('Weight')
            ax3.set_xlabel('Rebalance Period')
            ax3.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
            ax3.set_xlim(0, len(weights_df))
            ax3.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig('/workspace/backtest_results.png', dpi=150, bbox_inches='tight')
        print("\n✓ 图表已保存至: /workspace/backtest_results.png")
        
        plt.show()
        
        return fig


def main():
    """主函数"""
    print("\n" + "="*60)
    print("     大类资产风险平价目标波动率15%策略")
    print("              本地回测系统")
    print("="*60)
    
    strategy = RiskParityStrategy()
    
    try:
        strategy.fetch_data(start_date='20190101', end_date='20250530')
        
        strategy.run_backtest()
        
        metrics = strategy.generate_report()
        
        strategy.plot_results()
        
        print("\n" + "="*60)
        print("                   回测完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 回测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
