import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    """
    ETF简单测试策略 - 确保能买入
    """
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    
    set_order_cost(OrderCost(open_tax=0, close_tax=0.000, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='stock')
    
    # 只选1只ETF测试
    g.etf_code = '510300.XSHG'  # 沪深300ETF
    
    # 每个交易日都调仓，确保交易发生
    run_daily(trade, time='09:30')


def trade(context):
    """
    简单交易函数
    """
    log.info("开始交易函数")
    
    # 检查当前持仓
    if g.etf_code in context.portfolio.positions:
        position = context.portfolio.positions[g.etf_code]
        log.info("当前持有: %s, 数量: %d, 价值: %.2f", g.etf_code, position.total_amount, position.value)
    
    # 如果没有持仓，买入
    if g.etf_code not in context.portfolio.positions or context.portfolio.positions[g.etf_code].total_amount == 0:
        log.info("尝试买入: %s", g.etf_code)
        
        # 获取当前价格
        current_data = get_bars(g.etf_code, count=1, unit='1d', fields=['close'], include_now=True)
        if len(current_data) > 0:
            current_price = current_data['close'][-1]
            log.info("当前价格: %.2f", current_price)
            
            # 计算可以买多少股
            cash = context.portfolio.available_cash
            log.info("可用资金: %.2f", cash)
            
            # 用95%的资金买入
            value = cash * 0.95
            log.info("计划买入金额: %.2f", value)
            
            # 直接下单买入
            if value > 1000:  # 至少1000元
                order_value(g.etf_code, value)
                log.info("下单成功")
            else:
                log.info("资金不足")
        else:
            log.info("获取价格失败")
    else:
        log.info("已持有，不再买入")


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
