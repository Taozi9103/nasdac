import pandas as pd
import numpy as np
from jqdata import *


def initialize(context):
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    
    set_order_cost(OrderCost(open_tax=0, close_tax=0.000, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='stock')
    
    g.etf_code = '510300.XSHG'
    
    run_daily(before_trading, time='09:30')


def before_trading(context):
    try:
        positions = list(context.portfolio.positions)
        has_position = g.etf_code in positions
        
        if not has_position:
            order_target_percent(g.etf_code, 0.95)
    except Exception as e:
        log.info("Error: %s", str(e))


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
