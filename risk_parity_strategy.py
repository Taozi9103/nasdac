"""
大类资产风险平价目标波动率15%策略
Risk Parity with Target Volatility 15% Strategy

策略说明:
- 风险平价策略的核心思想是让每个资产对组合总风险的贡献相等
- 目标波动率控制将组合波动率维持在15%左右
- 使用动态杠杆调整实现目标波动率

资产池:
- 沪深300指数 (000300.XSHG) - 股票
- 中证500指数 (000905.XSHG) - 股票
- 国债指数 (H11001.XSHG) - 债券
- 黄金ETF (518880.XSHG) - 黄金
- 原油基金 (160416.XSHG) - 商品

聚宽平台: https://www.joinquant.com
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize


def initialize(context):
    """初始化策略参数"""
    set_benchmark('000300.XSHG')
    
    set_order_cost(OrderCost(closed=10000, min_cost=5), type='stock')
    set_slippage(0.002)
    
    context.target_volatility = 0.15
    context.lookback_period = 60
    context.rebalance_period = 20
    
    context.assets = {
        'stock_hs300': '000300.XSHG',
        'stock_zz500': '000905.XSHG',
        'bond': 'H11001.XSHG',
        'gold': '518880.XSHG',
        'oil': '160416.XSHG',
    }
    
    context.initial_weights = {k: 1.0/len(context.assets) for k in context.assets.keys()}
    context.trade_day_counter = 0
    
    log.info('策略初始化完成')
    log.info(f'目标波动率: {context.target_volatility*100:.1f}%')
    log.info(f'资产列表: {list(context.assets.values())}')


def handle_data(context, data):
    """每日交易逻辑"""
    context.trade_day_counter += 1
    
    if context.trade_day_counter % context.rebalance_period == 1 or context.trade_day_counter == 1:
        rebalance(context, data)


def rebalance(context, data):
    """执行调仓逻辑"""
    try:
        prices = get_history_data(context, data)
        if prices is None or len(prices) < context.lookback_period:
            return
        
        returns = calculate_returns(prices)
        cov_matrix = calculate_covariance(returns, context.lookback_period)
        
        asset_keys = list(context.assets.keys())
        risk_parity_weights = calculate_risk_parity_weights(cov_matrix, asset_keys)
        
        current_volatility = calculate_portfolio_volatility(risk_parity_weights, cov_matrix)
        
        if current_volatility > 0:
            vol_adjustment = context.target_volatility / current_volatility
            vol_adjustment = min(max(vol_adjustment, 0.5), 2.0)
        else:
            vol_adjustment = 1.0
        
        final_weights = {k: v * vol_adjustment for k, v in risk_parity_weights.items()}
        
        total_weight = sum(final_weights.values())
        if total_weight > 0:
            final_weights = {k: v/total_weight for k, v in final_weights.items()}
        
        execute_trades(context, data, final_weights)
        log_trades(context, final_weights, current_volatility, vol_adjustment)
        
    except Exception as e:
        log.error(f'调仓失败: {str(e)}')


def get_history_data(context, data):
    """获取历史价格数据"""
    symbols = list(context.assets.values())
    prices_dict = history(context.lookback_period + 1, 'close', symbols)
    
    if prices_dict is None or len(prices_dict) == 0:
        return None
    
    prices = pd.DataFrame(prices_dict)
    prices = prices.dropna(axis=1, how='any')
    
    if len(prices) < context.lookback_period:
        return None
    
    return prices


def calculate_returns(prices):
    """计算收益率"""
    returns = prices.pct_change().dropna()
    return returns


def calculate_covariance(returns, lookback):
    """计算协方差矩阵"""
    cov = returns.iloc[-lookback:].cov()
    return cov


def calculate_risk_parity_weights(cov_matrix, asset_keys):
    """
    计算风险平价权重
    核心思想: 每个资产对组合总风险的贡献相等
    """
    n_assets = len(cov_matrix)
    
    def risk_contribution(weights, cov):
        """计算每个资产的风险贡献"""
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
        marginal_risk = np.dot(cov, weights)
        risk_contrib = weights * marginal_risk / portfolio_vol
        return risk_contrib
    
    def risk_parity_objective(weights, cov):
        """风险平价目标函数: 最小化风险贡献方差"""
        target_risk = np.sum(risk_contribution(weights, cov)) / len(weights)
        actual_risks = risk_contribution(weights, cov)
        return np.sum((actual_risks - target_risk) ** 2)
    
    w0 = np.array([1.0/n_assets] * n_assets)
    cov_array = cov_matrix.values
    
    constraints = [{'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}]
    bounds = [(0.0, 0.4) for _ in range(n_assets)]
    
    result = minimize(
        risk_parity_objective,
        w0,
        args=(cov_array,),
        method='SLSQP',
        bounds=bounds,
        constraints=constraints,
        options={'maxiter': 1000}
    )
    
    if result.success:
        weights = result.x
    else:
        weights = w0
    
    weight_dict = {k: weights[i] for i, k in enumerate(asset_keys)}
    return weight_dict


def calculate_portfolio_volatility(weights, cov_matrix):
    """计算组合波动率"""
    weight_array = np.array(list(weights.values()))
    cov_array = cov_matrix.values
    portfolio_vol = np.sqrt(np.dot(weight_array.T, np.dot(cov_array, weight_array)))
    return portfolio_vol


def execute_trades(context, data, target_weights):
    """执行交易"""
    current_positions = context.portfolio.positions
    
    for asset_name, symbol in context.assets.items():
        target_weight = target_weights.get(asset_name, 0)
        current_value = context.portfolio.portfolio_value
        target_value = current_value * target_weight
        
        if symbol in current_positions:
            current_amount = current_positions[symbol].amount
            current_price = data.current(symbol, 'close')
            
            if current_price > 0:
                current_value_holding = current_amount * current_price
            else:
                current_value_holding = 0
        else:
            current_amount = 0
            current_value_holding = 0
        
        value_diff = target_value - current_value_holding
        min_trade_value = current_value * 0.01
        
        if abs(value_diff) > min_trade_value:
            order_target_value(symbol, target_value)
            log.info(f'{symbol}: 目标市值 {target_value:.2f}, 目标权重 {target_weight:.2%}')


def log_trades(context, weights, volatility, adjustment):
    """记录交易信息"""
    current_date = context.current_dt.strftime('%Y-%m-%d')
    
    log.info(f'\n===== {current_date} 调仓报告 =====')
    log.info(f'组合波动率: {volatility:.2%}')
    log.info(f'波动率调整系数: {adjustment:.2f}')
    log.info(f'目标波动率: {context.target_volatility:.2%}')
    log.info('资产配置:')
    
    for asset_name, weight in weights.items():
        symbol = context.assets[asset_name]
        log.info(f'  {asset_name} ({symbol}): {weight:.2%}')
