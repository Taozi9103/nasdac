import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    """
    ETF量化择时策略 - 强制交易版本
    """
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    
    set_order_cost(OrderCost(open_tax=0, close_tax=0.000, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='stock')
    
    # 更激进的参数
    g.rebalance_period = 5
    g.max_position_size = 0.95
    g.fund_count = 2  # 只选2只，更容易交易
    g.signal_threshold = 0.01  # 几乎任何信号都交易
    
    # ETF池 - 最常用的几只
    g.etf_pool = [
        '510300.XSHG',  # 沪深300ETF
        '159915.XSHE',  # 创业板ETF
    ]
    
    g.last_rebalance_date = None
    g.has_traded = False  # 标记是否已交易过
    
    # 启动时立即运行一次
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
    调仓主函数 - 强制交易
    """
    g.last_rebalance_date = context.current_dt
    
    # 1. 简化择时 - 每次都有信号
    macro_signal = 1.0  # 强制看多，确保有交易
    
    # 2. 总是满仓
    target_position = g.max_position_size
    
    # 3. 选所有ETF
    selected_etfs = g.etf_pool[:g.fund_count]
    
    log.info("选中ETF: %s, 目标仓位: %.2f", selected_etfs, target_position)
    
    # 4. 强制执行交易
    force_trade(context, selected_etfs, target_position)


def force_trade(context, selected_etfs, target_position):
    """
    强制交易函数
    """
    # 清仓所有持仓
    positions_list = list(context.portfolio.positions.values())
    for position in positions_list:
        try:
            log.info("清仓: %s, 当前持有: %d", position.security, position.total_amount)
            order_target(position.security, 0)
        except Exception as e:
            log.info("清仓失败: %s, 错误: %s", position.security, str(e))
    
    # 如果目标仓位为0，直接返回
    if target_position == 0:
        return
    
    # 强制买入
    weight = target_position / len(selected_etfs)
    for etf_code in selected_etfs:
        try:
            # 获取当前价格
            current_data = get_bars(etf_code, count=1, unit='1d', fields=['close'], include_now=True)
            if len(current_data) > 0:
                current_price = current_data['close'][-1]
                log.info("尝试买入: %s, 目标仓位: %.2f, 当前价格: %.2f", etf_code, weight, current_price)
                # 直接下单
                order_target_percent(etf_code, weight)
                g.has_traded = True
        except Exception as e:
            log.info("买入失败: %s, 错误: %s", etf_code, str(e))


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
