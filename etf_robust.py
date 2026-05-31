import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    set_option('order_updater', True)
    
    set_order_cost(OrderCost(open_tax=0, close_tax=0.000, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='stock')
    
    g.etf_code = '510300.XSHG'
    g.init = True
    
    run_daily(rebalance, time='09:35')


def rebalance(context):
    try:
        positions = context.portfolio.positions
        
        try:
            etf_position = positions.get(g.etf_code)
            if etf_position is None or etf_position.total_amount == 0:
                order_target_percent(g.etf_code, 0.95)
                log.info("Buy order placed")
            else:
                log.info("Already holding position")
        except:
            order_target_percent(g.etf_code, 0.95)
            log.info("Buy order placed (position check skipped)")
            
    except Exception as e:
        log.info("Rebalance error: %s", str(e))


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
