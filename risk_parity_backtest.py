"""
大类资产风险平价目标波动率15%策略 - 模拟数据回测
基于真实市场波动率和相关性特征的模拟数据

策略: Risk Parity with Target Volatility 15%
资产: 沪深300、中证500、国债指数、黄金ETF、原油基金
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class RiskParityBacktest:
    """风险平价策略回测类"""
    
    def __init__(self):
        self.initial_capital = 1000000
        self.target_volatility = 0.15
        self.lookback_period = 60
        self.rebalance_period = 20
        
        self.assets = {
            'stock_hs300': '沪深300',
            'stock_zz500': '中证500',
            'bond': '国债指数',
            'gold': '黄金ETF',
            'oil': '原油基金',
        }
        
        self.data = None
        self.returns = None
        self.portfolio_value = None
        self.weights_history = None
        self.trades = []
    
    def generate_realistic_data(self, start_date='2019-01-01', end_date='2025-05-30'):
        """生成基于真实市场特征的模拟数据"""
        print("\n" + "="*60)
        print("生成模拟市场数据...")
        print("="*60)
        
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        dates = pd.date_range(start, end, freq='B')
        n_days = len(dates)
        
        np.random.seed(42)
        
        print("  资产配置特征:")
        print("    - 沪深300: 年化收益8%, 年化波动25%")
        print("    - 中证500: 年化收益10%, 年化波动30%")
        print("    - 国债指数: 年化收益4%, 年化波动3%")
        print("    - 黄金ETF: 年化收益6%, 年化波动18%")
        print("    - 原油基金: 年化收益5%, 年化波动35%")
        
        annual_returns = {
            'stock_hs300': 0.08,
            'stock_zz500': 0.10,
            'bond': 0.04,
            'gold': 0.06,
            'oil': 0.05,
        }
        
        annual_vol = {
            'stock_hs300': 0.25,
            'stock_zz500': 0.30,
            'bond': 0.03,
            'gold': 0.18,
            'oil': 0.35,
        }
        
        correlation_matrix = np.array([
            [1.00, 0.85, 0.10, 0.20, 0.40],
            [0.85, 1.00, 0.05, 0.15, 0.35],
            [0.10, 0.05, 1.00, 0.15, -0.10],
            [0.20, 0.15, 0.15, 1.00, 0.30],
            [0.40, 0.35, -0.10, 0.30, 1.00],
        ])
        
        daily_returns = {}
        for i, (asset, name) in enumerate(self.assets.items()):
            mu = annual_returns[asset] / 252
            sigma = annual_vol[asset] / np.sqrt(252)
            
            random_returns = np.random.normal(0, 1, n_days)
            
            correlated_returns = np.zeros(n_days)
            for j in range(i):
                corr = correlation_matrix[i, j]
                correlated_returns += corr * random_returns * 0.3
            correlated_returns += np.sqrt(1 - 0.3*0.3*sum(correlation_matrix[i, :i]**2)) * random_returns * 0.7
            
            returns = mu + sigma * correlated_returns
            
            if asset in ['stock_hs300', 'stock_zz500']:
                shock_dates = [500, 800, 1100, 1350]
                for shock_date in shock_dates:
                    if shock_date < n_days:
                        returns[shock_date] -= 0.03 + np.random.normal(0, 0.01)
            
            daily_returns[asset] = returns
        
        returns_df = pd.DataFrame(daily_returns, index=dates)
        
        prices_df = (1 + returns_df).cumprod() * 100
        
        self.data = prices_df
        self.returns = returns_df
        
        print(f"\n✓ 数据生成完成")
        print(f"  时间范围: {dates[0].strftime('%Y-%m-%d')} 至 {dates[-1].strftime('%Y-%m-%d')}")
        print(f"  交易日数: {n_days}")
        
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
            print("错误: 请先调用 generate_realistic_data() 生成数据")
            return
        
        dates = self.data.index
        n_days = len(dates)
        
        portfolio_values = [self.initial_capital]
        weights_history = []
        daily_rets = []
        
        current_weights = {k: 1.0/len(self.assets) for k in self.assets.keys()}
        
        for i in range(n_days):
            if i < self.lookback_period:
                weights_history.append(current_weights)
                daily_rets.append(0)
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
                    'volatility': current_volatility,
                    'adjustment': vol_adjustment
                })
            else:
                weights_history.append(current_weights)
            
            daily_return = sum(current_weights[k] * self.returns.iloc[i][k] for k in self.assets.keys())
            daily_rets.append(daily_return)
            new_value = portfolio_values[-1] * (1 + daily_return)
            portfolio_values.append(new_value)
            
            if (i+1) % 500 == 0:
                print(f"  进度: {i+1}/{n_days} 天 ({(i+1)/n_days*100:.1f}%)")
        
        self.portfolio_value = pd.Series(portfolio_values[1:], index=dates)
        self.daily_returns = pd.Series(daily_rets, index=dates)
        self.weights_history = pd.DataFrame(weights_history, index=dates[:len(weights_history)])
        
        print(f"\n✓ 回测完成")
        print(f"  总交易日: {n_days}")
        print(f"  调仓次数: {len(self.trades)}")
        
        return self.portfolio_value
    
    def calculate_metrics(self):
        """计算绩效指标"""
        if self.portfolio_value is None:
            return None
        
        returns = self.daily_returns
        
        total_return = (self.portfolio_value.iloc[-1] / self.portfolio_value.iloc[0] - 1) * 100
        annual_return = ((1 + total_return/100) ** (252/len(returns)) - 1) * 100
        
        annual_volatility = returns.std() * np.sqrt(252) * 100
        
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else 0
        
        cumulative_returns = (1 + returns).cumprod() - 1
        peak = self.portfolio_value.expanding().max()
        drawdown = (self.portfolio_value - peak) / peak
        max_drawdown = drawdown.min() * 100
        
        returns_sorted = returns.sort_values()
        var_95 = returns_sorted.iloc[int(len(returns_sorted) * 0.05)] * 100
        cvar_95 = returns_sorted.iloc[:int(len(returns_sorted) * 0.05)].mean() * 100
        
        win_rate = (returns > 0).sum() / len(returns) * 100
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_value': self.portfolio_value.iloc[-1],
            'cumulative_returns': cumulative_returns,
            'drawdown': drawdown,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'win_rate': win_rate
        }
    
    def generate_report(self):
        """生成详细回测报告"""
        metrics = self.calculate_metrics()
        
        print("\n" + "="*70)
        print("                    大类资产风险平价策略 - 回测报告")
        print("="*70)
        
        print(f"\n{'策略名称:':<25} {'风险平价目标波动率15%策略':>35}")
        print(f"{'回测期间:':<25} {self.data.index[0].strftime('%Y-%m-%d')} 至 {self.data.index[-1].strftime('%Y-%m-%d'):>35}")
        print(f"{'初始资金:':<25} {f'¥{self.initial_capital:,.2f}':>35}")
        print(f"{'目标波动率:':<25} {f'{self.target_volatility*100:.1f}%':>35}")
        print(f"{'回看窗口:':<25} {f'{self.lookback_period}个交易日':>35}")
        print(f"{'再平衡周期:':<25} {f'{self.rebalance_period}个交易日':>35}")
        
        print(f"\n{'='*70}")
        print("                         核心绩效指标")
        print(f"{'='*70}")
        
        print(f"\n  {'指标':<30} {'数值':>20} {'说明':<15}")
        print(f"  {'-'*70}")
        print(f"  {'总收益率:':<30} {metrics['total_return']:>15.2f}%")
        print(f"  {'年化收益率:':<30} {metrics['annual_return']:>15.2f}%")
        print(f"  {'年化波动率:':<30} {metrics['annual_volatility']:>15.2f}%")
        print(f"  {'夏普比率:':<30} {metrics['sharpe_ratio']:>15.2f}")
        print(f"  {'最大回撤:':<30} {metrics['max_drawdown']:>15.2f}%")
        print(f"  {'最终资产:':<30} {f'¥{metrics["final_value"]:,.2f}':>20}")
        
        print(f"\n{'='*70}")
        print("                         风险指标")
        print(f"{'='*70}")
        
        print(f"\n  {'指标':<30} {'数值':>20}")
        print(f"  {'-'*70}")
        print(f"  {'VaR (95%):':<30} {metrics['var_95']:>15.2f}%")
        print(f"  {'CVaR (95%):':<30} {metrics['cvar_95']:>15.2f}%")
        print(f"  {'胜率:':<30} {metrics['win_rate']:>15.2f}%")
        
        print(f"\n{'='*70}")
        print("                         交易统计")
        print(f"{'='*70}")
        
        print(f"\n  {'指标':<30} {'数值':>20}")
        print(f"  {'-'*70}")
        print(f"  {'调仓次数:':<30} {len(self.trades):>15}")
        print(f"  {'平均持仓天数:':<30} {len(self.portfolio_value)/len(self.trades) if self.trades else 0:>15.1f}")
        
        if len(self.trades) > 0:
            print(f"\n{'='*70}")
            print("                         典型调仓记录")
            print(f"{'='*70}")
            
            print(f"\n  {'日期':<15} {'波动率':<12} {'调整系数':<12} {'权重配置'}")
            print(f"  {'-'*70}")
            
            sample_trades = self.trades[::max(1, len(self.trades)//5)][:5]
            for trade in sample_trades:
                date_str = trade['date'].strftime('%Y-%m-%d')
                vol_str = f"{trade['volatility']*100:.2f}%"
                adj_str = f"{trade['adjustment']:.2f}"
                weights_str = ', '.join([f"{k}:{v*100:.1f}%" for k, v in list(trade['weights'].items())[:3]])
                print(f"  {date_str:<15} {vol_str:<12} {adj_str:<12} {weights_str}")
        
        print("\n" + "="*70)
        
        return metrics
    
    def plot_results(self):
        """绘制详细结果图表"""
        metrics = self.calculate_metrics()
        
        fig = plt.figure(figsize=(16, 14))
        fig.suptitle('Risk Parity Strategy with Target Volatility 15%\nBacktest Results (2019-2025)', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        ax1 = plt.subplot(3, 2, 1)
        ax1.plot(self.portfolio_value.index, self.portfolio_value.values, 'b-', linewidth=2, label='Portfolio Value')
        ax1.axhline(y=self.initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
        ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Value (CNY)', fontsize=11)
        ax1.grid(True, alpha=0.3)
        ax1.legend(loc='upper left')
        ax1.set_xlim(self.portfolio_value.index[0], self.portfolio_value.index[-1])
        
        y_min = self.portfolio_value.min() * 0.98
        y_max = self.portfolio_value.max() * 1.02
        ax1.set_ylim(y_min, y_max)
        
        ax2 = plt.subplot(3, 2, 2)
        ax2.fill_between(metrics['drawdown'].index, metrics['drawdown'].values * 100, 0, 
                         alpha=0.4, color='red', label='Drawdown')
        ax2.plot(metrics['drawdown'].index, metrics['drawdown'].values * 100, 'r-', linewidth=1)
        ax2.axhline(y=metrics['max_drawdown'], color='darkred', linestyle='--', alpha=0.7,
                   label=f'Max DD: {metrics["max_drawdown"]:.2f}%')
        ax2.set_title('Drawdown Over Time', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='lower left')
        ax2.set_xlim(metrics['drawdown'].index[0], metrics['drawdown'].index[-1])
        
        ax3 = plt.subplot(3, 2, 3)
        cumulative = (1 + self.daily_returns).cumprod() - 1
        ax3.plot(cumulative.index, cumulative.values * 100, 'g-', linewidth=2, label='Strategy')
        ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax3.set_title('Cumulative Returns', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Return (%)', fontsize=11)
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper left')
        ax3.set_xlim(cumulative.index[0], cumulative.index[-1])
        
        ax4 = plt.subplot(3, 2, 4)
        if len(self.trades) > 0:
            weights_df = pd.DataFrame([t['weights'] for t in self.trades])
            colors = plt.cm.Set2(np.linspace(0, 1, len(weights_df.columns)))
            ax4.stackplot(range(len(weights_df)), 
                         weights_df.T.values,
                         labels=[self.assets[k] for k in weights_df.columns],
                         colors=colors,
                         alpha=0.8)
            ax4.set_title('Portfolio Weights Over Time', fontsize=14, fontweight='bold')
            ax4.set_ylabel('Weight', fontsize=11)
            ax4.set_xlabel('Rebalance Period', fontsize=11)
            ax4.legend(loc='upper right', bbox_to_anchor=(1.25, 1), fontsize=9)
            ax4.set_xlim(0, len(weights_df))
            ax4.set_ylim(0, 1)
        
        ax5 = plt.subplot(3, 2, 5)
        rolling_vol = self.daily_returns.rolling(window=20).std() * np.sqrt(252) * 100
        ax5.plot(rolling_vol.index, rolling_vol.values, 'purple', linewidth=1.5, label='Rolling Volatility')
        ax5.axhline(y=self.target_volatility * 100, color='red', linestyle='--', 
                   linewidth=2, label=f'Target: {self.target_volatility*100}%')
        ax5.set_title('Rolling Volatility (20-day)', fontsize=14, fontweight='bold')
        ax5.set_ylabel('Volatility (%)', fontsize=11)
        ax5.grid(True, alpha=0.3)
        ax5.legend(loc='upper right')
        ax5.set_xlim(rolling_vol.index[0], rolling_vol.index[-1])
        ax5.set_ylim(0, rolling_vol.max() * 1.2)
        
        ax6 = plt.subplot(3, 2, 6)
        metrics_text = f"""
Strategy Performance Summary
═══════════════════════════════════

Total Return:     {metrics['total_return']:>10.2f}%
Annual Return:    {metrics['annual_return']:>10.2f}%
Annual Volatility:{metrics['annual_volatility']:>10.2f}%
Sharpe Ratio:     {metrics['sharpe_ratio']:>10.2f}
Max Drawdown:     {metrics['max_drawdown']:>10.2f}%
Final Value:      ¥{metrics['final_value']:>10,.0f}

Risk Metrics
═══════════════════════════════════

VaR (95%):        {metrics['var_95']:>10.2f}%
CVaR (95%):       {metrics['cvar_95']:>10.2f}%
Win Rate:         {metrics['win_rate']:>10.2f}%

Trading Stats
═══════════════════════════════════

Rebalances:       {len(self.trades):>10}
"""
        ax6.text(0.1, 0.5, metrics_text, fontsize=11, family='monospace',
                verticalalignment='center', horizontalalignment='left',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
        ax6.axis('off')
        ax6.set_title('Performance Summary', fontsize=14, fontweight='bold')
        
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        plt.savefig('/workspace/backtest_results.png', dpi=150, bbox_inches='tight', facecolor='white')
        print("\n✓ 图表已保存至: /workspace/backtest_results.png")
        
        plt.show()
        
        return fig


def main():
    """主函数"""
    print("\n" + "="*70)
    print("        大类资产风险平价目标波动率15%策略 - 本地回测系统")
    print("="*70)
    
    backtest = RiskParityBacktest()
    
    try:
        backtest.generate_realistic_data(start_date='2019-01-01', end_date='2025-05-30')
        
        backtest.run_backtest()
        
        metrics = backtest.generate_report()
        
        backtest.plot_results()
        
        print("\n" + "="*70)
        print("                     回测完成！")
        print("="*70)
        
        return backtest, metrics
        
    except Exception as e:
        print(f"\n✗ 回测过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    backtest, metrics = main()
