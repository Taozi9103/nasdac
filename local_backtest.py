import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import akshare as ak
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

sns.set_style('whitegrid')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def get_etf_data(etf_code, start_date, end_date):
    """
    使用akshare获取ETF历史数据
    """
    print(f"正在获取 {etf_code} 数据...")
    try:
        # 获取ETF历史行情
        df = ak.fund_etf_hist_em(symbol=etf_code, period="daily", 
                                   start_date=start_date, end_date=end_date, 
                                   adjust="qfq")
        
        df = df.rename(columns={
            '日期': 'date',
            '收盘': 'close',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '成交额': 'amount'
        })
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()
        
        print(f"成功获取数据，共 {len(df)} 条记录")
        return df
    except Exception as e:
        print(f"获取数据失败: {e}")
        return None


def get_index_data(index_code, start_date, end_date):
    """
    获取指数数据作为基准
    """
    print(f"正在获取 {index_code} 指数数据...")
    try:
        df = ak.stock_zh_index_daily_em(symbol=index_code)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        df = df.sort_index()
        df = df.loc[start_date:end_date]
        
        print(f"成功获取指数数据，共 {len(df)} 条记录")
        return df
    except Exception as e:
        print(f"获取指数数据失败: {e}")
        return None


class MacroTimingStrategy:
    """
    宏观择时策略类
    """
    
    def __init__(self, etf_codes, initial_cash=1000000):
        self.etf_codes = etf_codes
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions = {}
        self.portfolio_value = []
        self.dates = []
        self.signals = []
        
    def get_timing_signal(self, prices):
        """
        择时信号：基于均线系统
        """
        if len(prices) < 30:
            return 0.5  # 数据不足时半仓
        
        closes = prices['close'].values
        
        # 计算均线
        ma_short = np.mean(closes[-10:])
        ma_long = np.mean(closes[-30:])
        current_price = closes[-1]
        
        # 信号生成
        if current_price > ma_short and ma_short > ma_long:
            return 1.0  # 看多
        elif current_price < ma_short and ma_short < ma_long:
            return 0.0  # 看空
        else:
            return 0.5  # 中性
    
    def select_etfs(self, etf_data_dict):
        """
        选择ETF：基于动量
        """
        etf_scores = {}
        
        for code, df in etf_data_dict.items():
            if len(df) >= 21:
                returns_20 = (df['close'].iloc[-1] - df['close'].iloc[-21]) / df['close'].iloc[-21]
                etf_scores[code] = returns_20
            else:
                etf_scores[code] = 0
        
        # 选择得分最高的2只
        sorted_etfs = sorted(etf_scores.items(), key=lambda x: x[1], reverse=True)
        selected = [etf[0] for etf in sorted_etfs[:2]]
        
        return selected
    
    def backtest(self, etf_data_dict, index_data, start_date, end_date):
        """
        回测主函数
        """
        print("\n开始回测...")
        
        # 获取所有交易日期
        all_dates = sorted(list(set().union(*[df.index for df in etf_data_dict.values()])))
        all_dates = [d for d in all_dates if start_date <= d <= end_date]
        
        for i, date in enumerate(all_dates):
            if i < 30:  # 前30天用于计算指标
                continue
                
            self.dates.append(date)
            
            # 获取当前时点的数据
            current_etf_data = {}
            for code, df in etf_data_dict.items():
                if date in df.index:
                    current_etf_data[code] = df.loc[:date]
            
            if len(current_etf_data) == 0:
                continue
            
            # 获取择时信号（用指数数据）
            if index_data is not None and date in index_data.index:
                timing_signal = self.get_timing_signal(index_data.loc[:date])
            else:
                timing_signal = 0.5
            
            self.signals.append(timing_signal)
            
            # 计算目标仓位
            target_position_ratio = timing_signal
            
            # 选择ETF
            selected_etfs = self.select_etfs(current_etf_data)
            
            # 调仓
            self.rebalance(current_etf_data, selected_etfs, target_position_ratio, date)
            
            # 计算当前组合价值
            current_value = self.calculate_portfolio_value(current_etf_data, date)
            self.portfolio_value.append(current_value)
            
            if i % 30 == 0:
                print(f"{date.strftime('%Y-%m-%d')}: 组合价值 {current_value:,.2f}")
        
        print("\n回测完成！")
    
    def rebalance(self, etf_data_dict, selected_etfs, target_ratio, date):
        """
        调仓
        """
        # 计算目标价值
        target_value = self.cash + sum([
            self.positions.get(code, 0) * etf_data_dict[code].loc[date, 'close'] 
            for code in self.positions if code in etf_data_dict and date in etf_data_dict.index
        ])
        target_value = max(target_value, self.initial_cash)
        
        target_amount = target_value * target_ratio
        
        # 先清仓不在选中列表的
        for code in list(self.positions.keys()):
            if code not in selected_etfs and code in etf_data_dict and date in etf_data_dict.index:
                price = etf_data_dict[code].loc[date, 'close']
                self.cash += self.positions[code] * price
                del self.positions[code]
        
        # 再买入选中的
        if len(selected_etfs) > 0 and target_amount > 0:
            per_etf_amount = target_amount / len(selected_etfs)
            
            for code in selected_etfs:
                if code in etf_data_dict and date in etf_data_dict.index:
                    price = etf_data_dict[code].loc[date, 'close']
                    if self.cash > per_etf_amount:
                        shares = int(per_etf_amount / price / 100) * 100  # 100股起买
                        if shares > 0:
                            cost = shares * price
                            self.positions[code] = self.positions.get(code, 0) + shares
                            self.cash -= cost
    
    def calculate_portfolio_value(self, etf_data_dict, date):
        """
        计算组合价值
        """
        value = self.cash
        for code, shares in self.positions.items():
            if code in etf_data_dict and date in etf_data_dict.index:
                value += shares * etf_data_dict[code].loc[date, 'close']
        return value
    
    def analyze_results(self, index_data):
        """
        分析回测结果
        """
        print("\n" + "="*50)
        print("回测结果分析")
        print("="*50)
        
        if len(self.portfolio_value) == 0:
            print("无交易记录")
            return None
        
        # 计算收益率
        returns = pd.Series(self.portfolio_value, index=self.dates).pct_change().dropna()
        
        total_return = (self.portfolio_value[-1] / self.initial_cash - 1) * 100
        
        # 计算年化收益
        years = (self.dates[-1] - self.dates[0]).days / 365
        annual_return = ((self.portfolio_value[-1] / self.initial_cash) ** (1/years) - 1) * 100 if years > 0 else 0
        
        # 计算最大回撤
        portfolio_series = pd.Series(self.portfolio_value, index=self.dates)
        rolling_max = portfolio_series.cummax()
        drawdown = (portfolio_series - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        
        print(f"初始资金: {self.initial_cash:,.2f}")
        print(f"最终资金: {self.portfolio_value[-1]:,.2f}")
        print(f"总收益率: {total_return:.2f}%")
        print(f"年化收益率: {annual_return:.2f}%")
        print(f"最大回撤: {max_drawdown:.2f}%")
        print(f"交易天数: {len(self.portfolio_value)}")
        
        return {
            'portfolio_value': portfolio_series,
            'returns': returns,
            'max_drawdown': max_drawdown,
            'total_return': total_return
        }
    
    def visualize_results(self, index_data):
        """
        可视化结果
        """
        results = self.analyze_results(index_data)
        if results is None:
            return
        
        portfolio_series = results['portfolio_value']
        
        fig = plt.figure(figsize=(15, 10))
        
        # 子图1: 净值曲线
        ax1 = plt.subplot(3, 1, 1)
        portfolio_series.plot(ax=ax1, label='策略净值', linewidth=2)
        ax1.set_title('策略净值曲线', fontsize=14, fontweight='bold')
        ax1.set_ylabel('净值')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 子图2: 择时信号
        ax2 = plt.subplot(3, 1, 2, sharex=ax1)
        pd.Series(self.signals, index=self.dates).plot(ax=ax2, label='择时信号', color='orange', linewidth=1.5)
        ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.5)
        ax2.set_title('择时信号', fontsize=12, fontweight='bold')
        ax2.set_ylabel('信号强度')
        ax2.set_ylim(-0.1, 1.1)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 子图3: 回撤
        ax3 = plt.subplot(3, 1, 3, sharex=ax1)
        rolling_max = portfolio_series.cummax()
        drawdown = (portfolio_series - rolling_max) / rolling_max * 100
        drawdown.plot(ax=ax3, label='回撤', color='red', linewidth=1.5)
        ax3.fill_between(drawdown.index, 0, drawdown.values, color='red', alpha=0.2)
        ax3.set_title('回撤曲线', fontsize=12, fontweight='bold')
        ax3.set_xlabel('日期')
        ax3.set_ylabel('回撤(%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('/workspace/backtest_results.png', dpi=300, bbox_inches='tight')
        print("\n结果图表已保存为 backtest_results.png")
        plt.show()


def main():
    """
    主函数
    """
    print("="*60)
    print("ETF宏观择时策略 - 本地回测系统")
    print("="*60)
    
    # 参数设置
    etf_codes = ['510300', '159915']  # 沪深300ETF, 创业板ETF
    start_date = '20200101'
    end_date = '20231231'
    initial_cash = 1000000
    
    # 获取数据
    print("\n正在获取数据...")
    etf_data_dict = {}
    for code in etf_codes:
        df = get_etf_data(code, start_date, end_date)
        if df is not None:
            etf_data_dict[code] = df
    
    # 获取指数数据
    index_data = get_index_data('sh000300', start_date, end_date)
    
    if len(etf_data_dict) == 0:
        print("没有获取到任何数据！")
        return
    
    # 创建策略实例
    strategy = MacroTimingStrategy(etf_codes, initial_cash)
    
    # 运行回测
    strategy.backtest(etf_data_dict, index_data, 
                      pd.to_datetime(start_date), pd.to_datetime(end_date))
    
    # 可视化结果
    strategy.visualize_results(index_data)


if __name__ == "__main__":
    main()
