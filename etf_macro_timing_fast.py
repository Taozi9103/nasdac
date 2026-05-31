import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    """
    ETF量化择时策略 - 快速版
    """
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    
    # ETF交易成本 - 比普通基金低
    set_order_cost(OrderCost(open_tax=0, close_tax=0.000, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='stock')
    
    # 策略参数
    g.rebalance_period = 5
    g.max_position_size = 0.95
    g.fund_count = 3
    g.signal_threshold = 0.1
    
    # ETF池 - 常用宽基和行业ETF
    g.etf_pool = [
        '510300.XSHG',  # 沪深300ETF
        '159915.XSHE',  # 创业板ETF
        '510500.XSHG',  # 中证500ETF
        '512880.XSHG',  # 证券ETF
        '512690.XSHG',  # 酒ETF
        '512170.XSHG',  # 医疗ETF
    ]
    
    g.last_rebalance_date = None
    g.current_position = 0
    
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
    
    # 3. 筛选ETF
    selected_etfs = select_etfs(context)
    
    # 4. 执行交易
    execute_trade(context, selected_etfs, target_position)


def get_timing_signal(context):
    """
    简化择时信号 - 单均线穿越策略
    """
    prices = get_bars('000300.XSHG', count=30, unit='1d', fields=['close'], include_now=True)
    
    if len(prices) < 20:
        return 0.5
    
    closes = prices['close']
    ma_20 = closes[-20:].mean()
    current_price = closes[-1]
    
    if current_price > ma_20:
        return 1.0
    else:
        return -1.0


def calculate_position(macro_signal):
    """
    计算目标仓位
    """
    if macro_signal > g.signal_threshold:
        return g.max_position_size
    elif macro_signal < -g.signal_threshold:
        return 0.0
    else:
        return 0.5


def select_etfs(context):
    """
    选择ETF - 简单动量筛选
    """
    etf_mom = {}
    
    for etf_code in g.etf_pool:
        try:
            prices = get_bars(etf_code, count=21, unit='1d', fields=['close'], include_now=True)
            if len(prices) >= 21:
                closes = prices['close']
                mom = (closes[-1] - closes[0]) / closes[0]
                etf_mom[etf_code] = mom
            else:
                etf_mom[etf_code] = 0
        except Exception as e:
            log.info("获取ETF数据失败: %s, 错误: %s", etf_code, str(e))
            etf_mom[etf_code] = 0
    
    sorted_etfs = sorted(etf_mom.items(), key=lambda x: x[1], reverse=True)
    selected = [e[0] for e in sorted_etfs[:g.fund_count]]
    
    log.info("选中ETF: %s", selected)
    return selected


def execute_trade(context, selected_etfs, target_position):
    """
    执行交易 - ETF版本
    """
    log.info("目标仓位: %.2f", target_position)
    
    # 清仓所有持仓
    positions_list = list(context.portfolio.positions.values())
    for position in positions_list:
        try:
            log.info("清仓: %s", position.security)
            order_target(position.security, 0)
        except Exception as e:
            log.info("清仓失败: %s, 错误: %s", position.security, str(e))
    
    # 如果目标仓位为0，直接返回
    if target_position == 0:
        g.current_position = 0
        return
    
    # 买入选中的ETF
    weight = target_position / len(selected_etfs)
    for etf_code in selected_etfs:
        try:
            log.info("买入: %s, 目标仓位: %.2f", etf_code, weight)
            order_target_percent(etf_code, weight)
        except Exception as e:
            log.info("买入失败: %s, 错误: %s", etf_code, str(e))
    
    g.current_position = target_position


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
