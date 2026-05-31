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
import datetime

def initialize(context):
    """初始化策略参数"""
    # 设置基准
    set_benchmark('000300.XSHG')
    
    # 设置手续费
    set_commission(Commission(buy_tax=0.001, sell_tax=0.001, 
                              min_commission=5))
    
    # 设置滑点
    set_slippage( SlippageFixed(0.002) )
    
    # 策略参数
    context.target_volatility = 0.15  # 目标波动率15%
    context.lookback_period = 60      # 回看窗口(交易日)
    context.rebalance_period = 20     # 再平衡周期(交易日)
    
    # 资产配置
    context.assets = {
        'stock_hs300': '000300.XSHG',  # 沪深300
        'stock_zz500': '000905.XSHG',  # 中证500
        'bond': 'H11001.XSHG',          # 国债指数
        'gold': '518880.XSHG',          # 黄金ETF
        'oil': '160416.XSHG',           # 原油基金
    }
    
    # 初始权重(等权重)
    context.initial_weights = {k: 1.0/len(context.assets) for k in context.assets.keys()}
    
    # 交易日期计数器
    context.trade_day_counter = 0
    
    # 记录日志
    log.info('策略初始化完成')
    log.info(f'目标波动率: {context.target_volatility*100:.1f}%')
    log.info(f'资产列表: {list(context.assets.values())}')


def handle_data(context, data):
    """每日交易逻辑"""
    context.trade_day_counter += 1
    
    # 按照再平衡周期调仓
    if context.trade_day_counter % context.rebalance_period == 1 or context.trade_day_counter == 1:
        rebalance(context, data)


def rebalance(context, data):
    """执行调仓逻辑"""
    try:
        # 获取历史数据计算风险指标
        prices = get_history_data(context, data)
        if prices is None or len(prices) < context.lookback_period:
            return
        
        # 计算收益率
        returns = calculate_returns(prices)
        
        # 计算协方差矩阵
        cov_matrix = calculate_covariance(returns, context.lookback_period)
        
        # 计算风险平价权重
        risk_parity_weights = calculate_risk_parity_weights(cov_matrix)
        
        # 计算当前组合波动率
        current_volatility = calculate_portfolio_volatility(risk_parity_weights, cov_matrix)
        
        # 计算目标波动率调整系数
        if current_volatility > 0:
            vol_adjustment = context.target_volatility / current_volatility
            vol_adjustment = min(max(vol_adjustment, 0.5), 2.0)  # 限制调整范围
        else:
            vol_adjustment = 1.0
        
        # 最终权重 = 风险平价权重 * 波动率调整系数
        final_weights = {k: v * vol_adjustment for k, v in risk_parity_weights.items()}
        
        # 归一化权重
        total_weight = sum(final_weights.values())
        if total_weight > 0:
            final_weights = {k: v/total_weight for k, v in final_weights.items()}
        
        # 执行交易
        execute_trades(context, data, final_weights)
        
        # 记录日志
        log_trades(context, final_weights, current_volatility, vol_adjustment)
        
    except Exception as e:
        log.error(f'调仓失败: {str(e)}')


def get_history_data(context, data):
    """获取历史价格数据"""
    symbols = list(context.assets.values())
    
    # 获取历史收盘价
    prices_dict = history(context.lookback_period + 1, 'close', symbols, skip_paused=True)
    
    if prices_dict is None or len(prices_dict) == 0:
        return None
    
    # 转换为DataFrame
    prices = pd.DataFrame(prices_dict)
    prices = prices.dropna()
    
    return prices


def calculate_returns(prices):
    """计算收益率"""
    returns = prices.pct_change().dropna()
    return returns


def calculate_covariance(returns, lookback):
    """计算协方差矩阵"""
    # 使用历史收益率计算协方差
    cov = returns.iloc[-lookback:].cov()
    return cov


def calculate_risk_parity_weights(cov_matrix):
    """
    计算风险平价权重
    风险平价的核心思想: 每个资产对组合总风险的贡献相等
    
    风险贡献 = 权重 * 边际风险贡献
    边际风险贡献 = 协方差矩阵 * 权重向量
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
    
    # 初始权重
    w0 = np.array([1.0/n_assets] * n_assets)
    
    # 协方差矩阵
    cov_array = cov_matrix.values
    
    # 优化约束条件
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1.0}  # 权重和为1
    ]
    
    # 边界条件
    bounds = [(0.0, 0.4) for _ in range(n_assets)]  # 单个资产权重不超过40%
    
    # 优化
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
    
    # 转换为字典
    weight_dict = {k: weights[i] for i, k in enumerate(context.assets.keys())}
    
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
        
        # 计算目标市值
        target_value = current_value * target_weight
        
        # 获取当前持仓
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
        
        # 计算需要交易的金额
        value_diff = target_value - current_value_holding
        
        # 设置最小交易阈值(避免小额交易)
        min_trade_value = current_value * 0.01
        
        # 买入
        if value_diff > min_trade_value:
            amount_to_buy = int(value_diff / (data.current(symbol, 'close') * 1.001))
            if amount_to_buy > 0:
                order_target(symbol, amount_to_buy, MarketOpenBuyStyle())
                log.info(f'买入 {symbol}: {amount_to_buy}股, 目标权重 {target_weight:.2%}')
        
        # 卖出
        elif value_diff < -min_trade_value:
            amount_to_sell = current_amount
            if amount_to_sell > 0:
                order_target(symbol, amount_to_sell, MarketOpenSellStyle())
                log.info(f'卖出 {symbol}: {amount_to_sell}股, 目标权重 {target_weight:.2%}')


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


def before_trading_start(context, data):
    """每日开盘前执行"""
    pass


def after_trading_end(context, data):
    """每日收盘后执行"""
    pass


# 聚宽平台特定配置
# g.t = text version for JoinQuant
g = globals()
