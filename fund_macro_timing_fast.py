import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    """
    简化版策略 - 快速回测
    """
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    
    # 优化参数 - 提高回测速度
    g.rebalance_period = 10  # 调仓周期延长至10天
    g.max_position_size = 0.95
    g.fund_count = 3  # 减少持仓基金数量
    g.signal_threshold = 0.4
    
    # 简化基金池 - 只保留几只主流宽基指数基金
    g.fund_pool = [
        '160706.OF',  # 嘉实沪深300ETF联接
        '110020.OF',  # 易方达沪深300ETF联接
        '000311.OF',  # 景顺长城沪深300增强
    ]
    
    g.last_rebalance_date = None
    
    # 简化运行频率
    run_daily(daily_check, time='09:30')


def daily_check(context):
    """
    简化每日检查
    """
    if g.last_rebalance_date is None:
        g.last_rebalance_date = context.current_dt
        rebalance(context)
    else:
        days_passed = (context.current_dt - g.last_rebalance_date).days
        if days_passed >= g.rebalance_period:
            rebalance(context)


def rebalance(context):
    """
    简化调仓逻辑
    """
    g.last_rebalance_date = context.current_dt
    
    # 1. 简化宏观择时信号
    macro_signal = get_simple_timing_signal(context)
    
    # 2. 计算仓位
    target_position = calculate_position(macro_signal)
    
    # 3. 简化基金筛选
    selected_funds = select_simple_funds(context)
    
    # 4. 调整组合
    adjust_simple_portfolio(context, selected_funds, target_position)


def get_simple_timing_signal(context):
    """
    简化择时信号 - 只用双均线系统
    """
    # 获取沪深300数据 - 减少回看周期
    prices = get_bars('000300.XSHG', count=40, unit='1d', fields=['close'], include_now=True)
    closes = prices['close']
    
    # 双均线系统
    ma_short = closes[-10:].mean()  # 10日均线
    ma_long = closes[-30:].mean()   # 30日均线
    current_price = closes[-1]
    
    # 简单信号判断
    if current_price > ma_short and ma_short > ma_long:
        return 1.0
    elif current_price < ma_short and ma_short < ma_long:
        return -1.0
    else:
        return 0.0


def calculate_position(macro_signal):
    """
    简化仓位计算
    """
    if macro_signal >= g.signal_threshold:
        return g.max_position_size
    elif macro_signal <= -g.signal_threshold:
        return 0.0
    else:
        return 0.5  # 中间状态半仓


def select_simple_funds(context):
    """
    简化基金筛选 - 只用短期动量
    """
    fund_mom = {}
    
    for fund_code in g.fund_pool:
        try:
            # 只用20日动量
            prices = get_bars(fund_code, count=21, unit='1d', fields=['close'], include_now=True)
            if len(prices) >= 21:
                closes = prices['close']
                mom = (closes[-1] - closes[0]) / closes[0]
                fund_mom[fund_code] = mom
        except:
            continue
    
    # 选表现最好的前N只
    sorted_funds = sorted(fund_mom.items(), key=lambda x: x[1], reverse=True)
    return [f[0] for f in sorted_funds[:g.fund_count]]


def adjust_simple_portfolio(context, selected_funds, target_position):
    """
    简化组合调整
    """
    # 清空所有持仓
    for position in context.portfolio.positions.values():
        order_target(position.security, 0)
    
    # 等权买入选中的基金
    if len(selected_funds) > 0 and target_position > 0:
        weight = target_position / len(selected_funds)
        for fund_code in selected_funds:
            order_target_percent(fund_code, weight)


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
