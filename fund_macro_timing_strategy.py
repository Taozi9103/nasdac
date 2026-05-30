import pandas as pd
import numpy as np
import math
from jqdata import *
import datetime


def initialize(context):
    """
    策略初始化函数
    """
    # 设置基本参数
    set_benchmark('000300.XSHG')  # 基准指数：沪深300
    set_option('use_real_price', True)  # 使用真实价格
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='fund')
    
    # 策略参数
    g.lookback_period = 20  # 宏观指标回看周期
    g.rebalance_period = 5  # 调仓周期（交易日）
    g.max_position_size = 0.95  # 最大仓位
    g.fund_count = 5  # 持仓基金数量
    g.signal_threshold = 0.5  # 择时信号阈值
    
    # 全局变量
    g.macro_indicators = {}
    g.last_rebalance_date = None
    
    # 基金池（宽基指数基金）
    g.fund_pool = [
        '161725.OF',  # 招商中证白酒指数分级
        '161024.OF',  # 富国中证军工指数分级
        '513050.OF',  # 易方达中证海外中国互联网50ETF联接
        '163406.OF',  # 兴全合润分级混合
        '161726.OF',  # 招商国证生物医药指数分级
        '001594.OF',  # 天弘中证银行ETF联接A
        '001556.OF',  # 天弘中证证券保险指数A
        '161810.OF',  # 银华中小盘精选混合
        '163110.OF',  # 申万菱信量化小盘股票(LOF)
        '160632.OF'   # 鹏华中证酒指数分级
    ]
    
    # 每日运行
    run_daily(daily_check, time='09:30')


def daily_check(context):
    """
    每日检查函数
    """
    # 判断是否需要调仓
    if g.last_rebalance_date is None:
        g.last_rebalance_date = context.current_dt
        rebalance(context)
    else:
        days_passed = (context.current_dt - g.last_rebalance_date).days
        if days_passed >= g.rebalance_period:
            rebalance(context)


def rebalance(context):
    """
    调仓主函数
    """
    g.last_rebalance_date = context.current_dt
    
    # 1. 获取宏观指标信号
    macro_signal = get_macro_timing_signal(context)
    
    # 2. 根据宏观信号决定仓位
    target_position = calculate_target_position(macro_signal)
    
    # 3. 筛选基金
    selected_funds = select_funds(context)
    
    # 4. 调整组合
    adjust_portfolio(context, selected_funds, target_position)


def get_macro_timing_signal(context):
    """
    获取宏观择时信号
    返回值：-1（看空）到 1（看多）之间的数值
    """
    signals = []
    
    # 信号1：趋势跟踪信号（基于沪深300）
    trend_signal = get_trend_signal(context, '000300.XSHG')
    signals.append(trend_signal)
    
    # 信号2：动量信号
    momentum_signal = get_momentum_signal(context, '000300.XSHG')
    signals.append(momentum_signal)
    
    # 信号3：波动率信号
    volatility_signal = get_volatility_signal(context, '000300.XSHG')
    signals.append(volatility_signal)
    
    # 综合信号（简单平均）
    composite_signal = np.mean(signals)
    
    # 记录信号
    record(trend_signal=trend_signal, 
           momentum_signal=momentum_signal, 
           volatility_signal=volatility_signal,
           composite_signal=composite_signal)
    
    return composite_signal


def get_trend_signal(context, index_code):
    """
    趋势跟踪信号：基于均线系统
    """
    # 获取历史数据
    prices = get_bars(index_code, count=g.lookback_period + 60, unit='1d', 
                      fields=['close'], include_now=True)
    closes = prices['close']
    
    # 计算均线
    ma_short = closes[-20:].mean()  # 20日均线
    ma_long = closes[-60:].mean()   # 60日均线
    
    # 趋势判断
    current_price = closes[-1]
    
    if current_price > ma_short and ma_short > ma_long:
        return 1.0  # 强势多头
    elif current_price > ma_short and ma_short < ma_long:
        return 0.5  # 震荡偏多
    elif current_price < ma_short and ma_short > ma_long:
        return -0.5  # 震荡偏空
    else:
        return -1.0  # 强势空头


def get_momentum_signal(context, index_code):
    """
    动量信号：基于收益率
    """
    # 获取历史数据
    prices = get_bars(index_code, count=g.lookback_period + 1, unit='1d', 
                      fields=['close'], include_now=True)
    closes = prices['close']
    
    # 计算动量（过去20日收益率）
    momentum = (closes[-1] - closes[0]) / closes[0]
    
    # 标准化到 [-1, 1] 范围
    # 使用经验阈值：过去20日收益率在 [-5%, 5%] 之间线性映射
    if momentum > 0.05:
        return 1.0
    elif momentum < -0.05:
        return -1.0
    else:
        return momentum / 0.05


def get_volatility_signal(context, index_code):
    """
    波动率信号：基于标准差
    """
    # 获取历史数据
    prices = get_bars(index_code, count=g.lookback_period + 1, unit='1d', 
                      fields=['close'], include_now=True)
    closes = prices['close']
    
    # 计算日收益率
    returns = np.diff(closes) / closes[:-1]
    
    # 计算波动率（年化）
    volatility = np.std(returns) * np.sqrt(252)
    
    # 波动率信号：低波动率看多，高波动率看空
    # 使用经验阈值：波动率在 [10%, 30%] 之间线性映射
    if volatility < 0.1:
        return 1.0
    elif volatility > 0.3:
        return -1.0
    else:
        return (0.3 - volatility) / 0.2


def calculate_target_position(macro_signal):
    """
    根据宏观信号计算目标仓位
    """
    # 信号从 [-1, 1] 映射到 [0, max_position_size]
    if macro_signal >= g.signal_threshold:
        return g.max_position_size
    elif macro_signal <= -g.signal_threshold:
        return 0.0
    else:
        # 线性插值
        position_ratio = (macro_signal + g.signal_threshold) / (2 * g.signal_threshold)
        return position_ratio * g.max_position_size


def select_funds(context):
    """
    筛选基金：基于动量因子
    """
    fund_data = {}
    
    # 获取每只基金的历史表现
    for fund_code in g.fund_pool:
        try:
            # 获取基金净值数据
            prices = get_bars(fund_code, count=g.lookback_period + 1, unit='1d', 
                              fields=['close'], include_now=True)
            if len(prices) >= g.lookback_period + 1:
                closes = prices['close']
                # 计算过去20日收益率
                returns = (closes[-1] - closes[0]) / closes[0]
                fund_data[fund_code] = returns
        except:
            continue
    
    # 按收益率排序，选择表现最好的前N只
    sorted_funds = sorted(fund_data.items(), key=lambda x: x[1], reverse=True)
    selected = [fund[0] for fund in sorted_funds[:g.fund_count]]
    
    return selected


def adjust_portfolio(context, selected_funds, target_position):
    """
    调整投资组合
    """
    # 1. 卖出不在选中列表的基金
    for position in context.portfolio.positions.values():
        if position.security not in selected_funds:
            order_target(position.security, 0)
    
    # 2. 计算单只基金的目标仓位
    if len(selected_funds) > 0:
        fund_position = target_position / len(selected_funds)
        
        # 3. 买入选中的基金
        for fund_code in selected_funds:
            order_target_percent(fund_code, fund_position)


def handle_data(context, data):
    """
    盘中数据处理函数（可选）
    """
    pass


def after_trading_end(context):
    """
    交易结束后的处理
    """
    pass
