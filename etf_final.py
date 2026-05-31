import pandas as pd
import numpy as np
from jqdata import *
import datetime


def initialize(context):
    log.info("策略初始化")
    
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    
    set_order_cost(OrderCost(open_tax=0, close_tax=0.000, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='stock')
    
    g.etf_pool = [
        ('510300.XSHG', '沪深300ETF'),
    ]
    
    g.last_trade_date = None
    
    run_daily(check_and_trade, time='09:35')


def check_and_trade(context):
    today = context.current_dt.strftime('%Y-%m-%d')
    
    if g.last_trade_date == today:
        return
    
    for etf_code, etf_name in g.etf_pool:
        order_target_percent(etf_code, 0.98)
        log.info("%s 买入 %s", today, etf_name)
    
    g.last_trade_date = today


def handle_data(context, data):
    pass


def after_trading_end(context):
    positions = context.portfolio.positions
    log.info("当前持仓数量: %d", len(positions))
    
    for pos in positions.values():
        log.info("持仓: %s, 数量: %d", pos.security, pos.total_amount)
