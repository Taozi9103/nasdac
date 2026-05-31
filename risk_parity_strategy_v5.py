import numpy as np
import pandas as pd
from scipy.optimize import minimize


def initialize(context):
    set_benchmark('000300.XSHG')
    
    set_slippage(FixedSlippage(0.002))
    
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
    
    log.info('Strategy initialized')
    log.info('Target volatility: 15%')


def handle_data(context, data):
    context.trade_day_counter += 1
    
    if context.trade_day_counter % context.rebalance_period == 1 or context.trade_day_counter == 1:
        rebalance(context, data)


def rebalance(context, data):
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
        log.error('Rebalance failed: %s' % str(e))


def get_history_data(context, data):
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
    returns = prices.pct_change().dropna()
    return returns


def calculate_covariance(returns, lookback):
    cov = returns.iloc[-lookback:].cov()
    return cov


def calculate_risk_parity_weights(cov_matrix, asset_keys):
    n_assets = len(cov_matrix)
    
    def risk_contribution(weights, cov):
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov, weights)))
        marginal_risk = np.dot(cov, weights)
        risk_contrib = weights * marginal_risk / portfolio_vol
        return risk_contrib
    
    def risk_parity_objective(weights, cov):
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
    weight_array = np.array(list(weights.values()))
    cov_array = cov_matrix.values
    portfolio_vol = np.sqrt(np.dot(weight_array.T, np.dot(cov_array, weight_array)))
    return portfolio_vol


def execute_trades(context, data, target_weights):
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


def log_trades(context, weights, volatility, adjustment):
    current_date = context.current_dt.strftime('%Y-%m-%d')
    
    log.info('===== Rebalance Report %s =====' % current_date)
    log.info('Portfolio volatility: %.2f%%' % (volatility * 100))
    log.info('Volatility adjustment: %.2f' % adjustment)
    log.info('Target volatility: 15.00%%')
    log.info('Asset allocation:')
    
    for asset_name, weight in weights.items():
        symbol = context.assets[asset_name]
        log.info('  %s: %.2f%%' % (symbol, weight * 100))
