import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    """
    简化版策略 - 确保产生交易信号
    """
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='fund')
    
    # 优化参数 - 提高交易频率
    g.rebalance_period = 5  # 调仓周期5天
    g.max_position_size = 0.95
    g.fund_count = 3
    g.signal_threshold = 0.1  # 降低阈值，更容易触发交易
    
    # 基金池 - 确保数据可用
    g.fund_pool = [
        '160706.OF',  # 嘉实沪深300ETF联接(LOF)A
        '110020.OF',  # 易方达沪深300ETF联接
        '000311.OF',  # 景顺长城沪深300增强
    ]
    
    g.last_rebalance_date = None
    g.current_position = 0  # 记录当前仓位状态
    
    run_daily(daily_check, time='09:30')


def daily_check(context):
    """
    每日检查
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
    调仓主函数
    """
    g.last_rebalance_date = context.current_dt
    
    # 1. 获取择时信号
    macro_signal = get_timing_signal(context)
    
    # 2. 计算目标仓位
    target_position = calculate_position(macro_signal)
    
    # 3. 筛选基金
    selected_funds = select_funds(context)
    
    # 4. 执行交易
    execute_trade(context, selected_funds, target_position)


def get_timing_signal(context):
    """
    简化择时信号 - 单均线穿越策略
    """
    # 获取沪深300数据
    prices = get_bars('000300.XSHG', count=30, unit='1d', fields=['close'], include_now=True)
    
    if len(prices) < 20:
        return 0.5  # 默认半仓
    
    closes = prices['close']
    ma_20 = closes[-20:].mean()
    current_price = closes[-1]
    
    # 简单均线穿越
    if current_price > ma_20:
        return 1.0  # 看多
    else:
        return -1.0  # 看空


def calculate_position(macro_signal):
    """
    计算目标仓位 - 简化版
    """
    if macro_signal > g.signal_threshold:
        return g.max_position_size  # 满仓
    elif macro_signal < -g.signal_threshold:
        return 0.0  # 空仓
    else:
        return 0.5  # 半仓


def select_funds(context):
    """
    选择基金 - 简单动量筛选
    """
    fund_mom = {}
    
    for fund_code in g.fund_pool:
        try:
            prices = get_bars(fund_code, count=21, unit='1d', fields=['close'], include_now=True)
            if len(prices) >= 21:
                closes = prices['close']
                mom = (closes[-1] - closes[0]) / closes[0]
                fund_mom[fund_code] = mom
            else:
                fund_mom[fund_code] = 0
        except Exception as e:
            log.info("获取基金数据失败: %s, 错误: %s", fund_code, str(e))
            fund_mom[fund_code] = 0
    
    # 按动量排序，选前N只
    sorted_funds = sorted(fund_mom.items(), key=lambda x: x[1], reverse=True)
    selected = [f[0] for f in sorted_funds[:g.fund_count]]
    
    log.info("选中基金: %s", selected)
    return selected


def execute_trade(context, selected_funds, target_position):
    """
    执行交易 - 确保有交易发生
    """
    log.info("目标仓位: %.2f", target_position)
    
    # 如果目标仓位为0，清仓所有
    if target_position == 0:
        for position in context.portfolio.positions.values():
            log.info("清仓: %s", position.security)
            order_target(position.security, 0)
        g.current_position = 0
        return
    
    # 卖出不在选中列表的基金
    for position in context.portfolio.positions.values():
        if position.security not in selected_funds:
            log.info("卖出非选中基金: %s", position.security)
            order_target(position.security, 0)
    
    # 买入选中的基金
    weight = target_position / len(selected_funds)
    for fund_code in selected_funds:
        current_hold = 0
        if fund_code in context.portfolio.positions:
            current_hold = context.portfolio.positions[fund_code].value / context.portfolio.total_value
        
        # 只有当仓位差异大于5%时才调仓
        if abs(weight - current_hold) > 0.05:
            log.info("调仓: %s, 目标仓位: %.2f", fund_code, weight)
            order_target_percent(fund_code, weight)
    
    g.current_position = target_position


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
