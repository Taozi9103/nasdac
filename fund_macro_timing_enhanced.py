import pandas as pd
import numpy as np
import math
from jqdata import *
import datetime


def initialize(context):
    """
    增强版策略初始化函数
    """
    # 设置基本参数
    set_benchmark('000300.XSHG')
    set_option('use_real_price', True)
    set_order_cost(OrderCost(open_tax=0, close_tax=0.001, open_commission=0.0003, close_commission=0.0003, 
                             close_today_commission=0, min_commission=5), type='fund')
    
    # 策略参数
    g.lookback_period = 20
    g.rebalance_period = 5
    g.max_position_size = 0.95
    g.fund_count = 5
    g.signal_threshold = 0.5
    g.stop_loss_threshold = 0.08  # 止损阈值
    g.max_drawdown_threshold = 0.15  # 最大回撤阈值
    
    # 全局变量
    g.last_rebalance_date = None
    g.entry_prices = {}  # 记录入场价格
    g.portfolio_high = 0  # 组合历史最高净值
    
    # 基金池（更丰富的指数基金池）
    g.fund_pool = get_fund_pool()
    
    # 每日运行
    run_daily(daily_check, time='09:30')
    run_daily(check_risk, time='14:30')


def get_fund_pool():
    """
    获取基金池，包含各类指数基金
    """
    return [
        # 宽基指数基金
        '160706.OF',  # 嘉实沪深300ETF联接(LOF)A
        '000311.OF',  # 景顺长城沪深300增强
        '110020.OF',  # 易方达沪深300ETF联接
        # 行业指数基金
        '161725.OF',  # 招商中证白酒指数分级
        '161024.OF',  # 富国中证军工指数分级
        '161726.OF',  # 招商国证生物医药指数分级
        '001594.OF',  # 天弘中证银行ETF联接A
        '001556.OF',  # 天弘中证证券保险指数A
        '163110.OF',  # 申万菱信量化小盘股票(LOF)
        '160632.OF',  # 鹏华中证酒指数分级
        # 海外指数基金
        '513050.OF',  # 易方达中证海外中国互联网50ETF联接
        '000043.OF',  # 嘉实纳斯达克100指数(QDII)
        # 混合基金
        '163406.OF',  # 兴全合润分级混合
        '161810.OF',  # 银华中小盘精选混合
        '519732.OF'   # 交银双息平衡混合
    ]


def daily_check(context):
    """
    每日检查函数
    """
    if g.last_rebalance_date is None:
        g.last_rebalance_date = context.current_dt
        rebalance(context)
    else:
        days_passed = (context.current_dt - g.last_rebalance_date).days
        if days_passed >= g.rebalance_period:
            rebalance(context)


def check_risk(context):
    """
    风险检查函数：止损和最大回撤控制
    """
    current_value = context.portfolio.total_value
    
    # 更新组合历史最高净值
    if current_value > g.portfolio_high:
        g.portfolio_high = current_value
    
    # 检查最大回撤
    drawdown = (g.portfolio_high - current_value) / g.portfolio_high
    if drawdown > g.max_drawdown_threshold:
        log.info("触发最大回撤控制：当前回撤%.2f%%，清仓", drawdown * 100)
        for position in context.portfolio.positions.values():
            order_target(position.security, 0)
        return
    
    # 检查个股止损
    for fund_code, position in context.portfolio.positions.items():
        if fund_code in g.entry_prices:
            entry_price = g.entry_prices[fund_code]
            current_price = position.value / position.total_amount if position.total_amount > 0 else 0
            if current_price > 0:
                loss_ratio = (entry_price - current_price) / entry_price
                if loss_ratio > g.stop_loss_threshold:
                    log.info("触发止损：%s，亏损%.2f%%", fund_code, loss_ratio * 100)
                    order_target(fund_code, 0)


def rebalance(context):
    """
    调仓主函数
    """
    g.last_rebalance_date = context.current_dt
    
    # 1. 获取宏观择时信号
    macro_signal = get_macro_timing_signal(context)
    
    # 2. 根据宏观信号决定仓位
    target_position = calculate_target_position(macro_signal)
    
    # 3. 筛选基金
    selected_funds = select_funds(context)
    
    # 4. 调整组合
    adjust_portfolio(context, selected_funds, target_position)


def get_macro_timing_signal(context):
    """
    获取宏观择时信号（增强版）
    """
    signals = []
    
    # 信号1：趋势跟踪
    trend_signal = get_trend_signal(context, '000300.XSHG')
    signals.append(trend_signal)
    
    # 信号2：动量信号
    momentum_signal = get_momentum_signal(context, '000300.XSHG')
    signals.append(momentum_signal)
    
    # 信号3：波动率信号
    volatility_signal = get_volatility_signal(context, '000300.XSHG')
    signals.append(volatility_signal)
    
    # 信号4：量价配合信号
    volume_signal = get_volume_signal(context, '000300.XSHG')
    signals.append(volume_signal)
    
    # 综合信号（加权平均）
    weights = [0.3, 0.25, 0.25, 0.2]
    composite_signal = np.average(signals, weights=weights)
    
    # 记录信号
    record(trend_signal=trend_signal, 
           momentum_signal=momentum_signal, 
           volatility_signal=volatility_signal,
           volume_signal=volume_signal,
           composite_signal=composite_signal,
           target_position=calculate_target_position(composite_signal))
    
    return composite_signal


def get_trend_signal(context, index_code):
    """
    趋势跟踪信号：基于均线系统
    """
    prices = get_bars(index_code, count=80, unit='1d', fields=['close'], include_now=True)
    closes = prices['close']
    
    ma_short = closes[-20:].mean()
    ma_mid = closes[-40:].mean()
    ma_long = closes[-60:].mean()
    current_price = closes[-1]
    
    score = 0
    if current_price > ma_short:
        score += 0.4
    if ma_short > ma_mid:
        score += 0.3
    if ma_mid > ma_long:
        score += 0.3
    
    return score * 2 - 1  # 归一化到 [-1, 1]


def get_momentum_signal(context, index_code):
    """
    动量信号：基于多周期收益率
    """
    prices = get_bars(index_code, count=61, unit='1d', fields=['close'], include_now=True)
    closes = prices['close']
    
    # 多周期动量
    mom_5 = (closes[-1] - closes[-6]) / closes[-6]
    mom_20 = (closes[-1] - closes[-21]) / closes[-21]
    mom_60 = (closes[-1] - closes[0]) / closes[0]
    
    # 加权综合
    momentum = 0.4 * mom_5 + 0.35 * mom_20 + 0.25 * mom_60
    
    # 标准化
    if momentum > 0.08:
        return 1.0
    elif momentum < -0.08:
        return -1.0
    else:
        return momentum / 0.08


def get_volatility_signal(context, index_code):
    """
    波动率信号：基于标准差和VIX类指标
    """
    prices = get_bars(index_code, count=61, unit='1d', fields=['close'], include_now=True)
    closes = prices['close']
    
    returns = np.diff(closes) / closes[:-1]
    
    # 短期和长期波动率
    vol_short = np.std(returns[-20:]) * np.sqrt(252)
    vol_long = np.std(returns) * np.sqrt(252)
    
    # 波动率相对水平
    vol_ratio = vol_short / vol_long if vol_long > 0 else 1
    
    # 低波动率看多，高波动率看空
    if vol_short < 0.12:
        return 1.0
    elif vol_short > 0.28:
        return -1.0
    else:
        return (0.28 - vol_short) / 0.16


def get_volume_signal(context, index_code):
    """
    量价配合信号
    """
    bars = get_bars(index_code, count=41, unit='1d', fields=['close', 'volume'], include_now=True)
    closes = bars['close']
    volumes = bars['volume']
    
    # 价格变化
    price_change = (closes[-1] - closes[-21]) / closes[-21]
    
    # 成交量变化
    vol_current = volumes[-5:].mean()
    vol_past = volumes[-25:-5].mean()
    vol_change = (vol_current - vol_past) / vol_past if vol_past > 0 else 0
    
    # 量价配合判断
    if price_change > 0.02 and vol_change > 0.1:
        return 1.0  # 放量上涨，看多
    elif price_change < -0.02 and vol_change > 0.1:
        return -1.0  # 放量下跌，看空
    elif price_change > 0:
        return 0.3
    else:
        return -0.3


def calculate_target_position(macro_signal):
    """
    根据宏观信号计算目标仓位
    """
    if macro_signal >= g.signal_threshold:
        return g.max_position_size
    elif macro_signal <= -g.signal_threshold:
        return 0.0
    else:
        position_ratio = (macro_signal + g.signal_threshold) / (2 * g.signal_threshold)
        return position_ratio * g.max_position_size


def select_funds(context):
    """
    筛选基金：基于多因子模型
    """
    fund_scores = {}
    
    for fund_code in g.fund_pool:
        try:
            prices = get_bars(fund_code, count=61, unit='1d', fields=['close'], include_now=True)
            if len(prices) >= 61:
                closes = prices['close']
                
                # 因子1：动量因子（过去20日）
                mom_20 = (closes[-1] - closes[-21]) / closes[-21]
                
                # 因子2：动量因子（过去60日）
                mom_60 = (closes[-1] - closes[0]) / closes[0]
                
                # 因子3：波动率因子（越低越好）
                returns = np.diff(closes) / closes[:-1]
                volatility = np.std(returns)
                
                # 综合评分
                score = 0.4 * mom_20 + 0.3 * mom_60 - 0.3 * volatility
                fund_scores[fund_code] = score
        except:
            continue
    
    # 按评分排序
    sorted_funds = sorted(fund_scores.items(), key=lambda x: x[1], reverse=True)
    selected = [fund[0] for fund in sorted_funds[:g.fund_count]]
    
    return selected


def adjust_portfolio(context, selected_funds, target_position):
    """
    调整投资组合
    """
    # 卖出不在选中列表的基金
    for position in context.portfolio.positions.values():
        if position.security not in selected_funds:
            order_target(position.security, 0)
    
    # 调整选中基金的仓位
    if len(selected_funds) > 0:
        fund_position = target_position / len(selected_funds)
        
        for fund_code in selected_funds:
            # 获取当前持仓
            current_position = 0
            if fund_code in context.portfolio.positions:
                pos = context.portfolio.positions[fund_code]
                current_position = pos.value / context.portfolio.total_value if context.portfolio.total_value > 0 else 0
            
            # 如果目标仓位与当前差异较大，调仓
            if abs(fund_position - current_position) > 0.05:
                order_target_percent(fund_code, fund_position)
                
                # 记录入场价格
                if fund_position > 0:
                    prices = get_bars(fund_code, count=1, unit='1d', fields=['close'], include_now=True)
                    if len(prices) > 0:
                        g.entry_prices[fund_code] = prices['close'][-1]


def handle_data(context, data):
    pass


def after_trading_end(context):
    pass
