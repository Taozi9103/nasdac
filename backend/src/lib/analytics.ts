export const calculateCorrelation = (x: number[], y: number[]): number => {
  if (x.length !== y.length || x.length === 0) {
    throw new Error('Data arrays must have the same length and be non-empty');
  }

  const n = x.length;
  
  const meanX = x.reduce((a, b) => a + b, 0) / n;
  const meanY = y.reduce((a, b) => a + b, 0) / n;

  let numerator = 0;
  let denomX = 0;
  let denomY = 0;

  for (let i = 0; i < n; i++) {
    const dx = x[i] - meanX;
    const dy = y[i] - meanY;
    numerator += dx * dy;
    denomX += dx * dx;
    denomY += dy * dy;
  }

  const denominator = Math.sqrt(denomX * denomY);
  
  if (denominator === 0) return 0;
  
  return numerator / denominator;
};

export const calculateReturns = (prices: number[]): number[] => {
  const returns: number[] = [];
  for (let i = 1; i < prices.length; i++) {
    returns.push((prices[i] - prices[i - 1]) / prices[i - 1]);
  }
  return returns;
};

export const calculateVolatility = (returns: number[]): number => {
  if (returns.length === 0) return 0;
  
  const mean = returns.reduce((a, b) => a + b, 0) / returns.length;
  const squaredDiffs = returns.map(r => Math.pow(r - mean, 2));
  const variance = squaredDiffs.reduce((a, b) => a + b, 0) / returns.length;
  
  return Math.sqrt(variance * 252); // Annualized volatility
};

export const calculateAnnualReturn = (returns: number[]): number => {
  if (returns.length === 0) return 0;
  
  const cumulativeReturn = returns.reduce((acc, r) => acc * (1 + r), 1) - 1;
  const years = returns.length / 252; // Assuming 252 trading days
  
  return Math.pow(1 + cumulativeReturn, 1 / years) - 1;
};

export const calculateSharpeRatio = (returns: number[], riskFreeRate: number = 0.03): number => {
  if (returns.length === 0) return 0;
  
  const annualReturn = calculateAnnualReturn(returns);
  const annualVolatility = calculateVolatility(returns);
  
  if (annualVolatility === 0) return 0;
  
  return (annualReturn - riskFreeRate) / annualVolatility;
};

export const calculateMaxDrawdown = (prices: number[]): number => {
  if (prices.length === 0) return 0;
  
  let maxDrawdown = 0;
  let peak = prices[0];
  
  for (const price of prices) {
    if (price > peak) {
      peak = price;
    }
    const drawdown = (peak - price) / peak;
    maxDrawdown = Math.max(maxDrawdown, drawdown);
  }
  
  return maxDrawdown;
};

export const generateCorrelationMatrix = (
  assetReturns: Map<string, number[]>
): Map<string, Map<string, number>> => {
  const assets = Array.from(assetReturns.keys());
  const matrix = new Map<string, Map<string, number>>();

  for (const asset1 of assets) {
    const row = new Map<string, number>();
    for (const asset2 of assets) {
      const returns1 = assetReturns.get(asset1)!;
      const returns2 = assetReturns.get(asset2)!;
      
      const correlation = calculateCorrelation(returns1, returns2);
      row.set(asset2, correlation);
    }
    matrix.set(asset1, row);
  }

  return matrix;
};

export const calculatePortfolioReturn = (
  weights: number[],
  returns: number[][]
): number[] => {
  const portfolioReturns: number[] = [];
  
  for (let i = 0; i < returns[0].length; i++) {
    let portReturn = 0;
    for (let j = 0; j < weights.length; j++) {
      portReturn += weights[j] * returns[j][i];
    }
    portfolioReturns.push(portReturn);
  }
  
  return portfolioReturns;
};

export const calculatePortfolioVolatility = (
  weights: number[],
  correlations: number[][],
  volatilities: number[]
): number => {
  const n = weights.length;
  let variance = 0;
  
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n; j++) {
      variance += weights[i] * weights[j] * correlations[i][j] * volatilities[i] * volatilities[j];
    }
  }
  
  return Math.sqrt(variance);
};

export const findEfficientFrontier = (
  expectedReturns: number[],
  volatilities: number[],
  correlations: number[][]
): Array<{weights: number[], expectedReturn: number, volatility: number, sharpe: number}> => {
  const n = expectedReturns.length;
  const frontier: Array<{weights: number[], expectedReturn: number, volatility: number, sharpe: number}> = [];
  
  // Generate random portfolios to find efficient frontier
  const numPortfolios = 1000;
  
  for (let i = 0; i < numPortfolios; i++) {
    // Generate random weights
    let weights = Array.from({length: n}, () => Math.random());
    const sum = weights.reduce((a, b) => a + b, 0);
    weights = weights.map(w => w / sum);
    
    // Calculate portfolio metrics
    let portReturn = 0;
    for (let j = 0; j < n; j++) {
      portReturn += weights[j] * expectedReturns[j];
    }
    
    const portVol = calculatePortfolioVolatility(weights, correlations, volatilities);
    const sharpe = portVol > 0 ? portReturn / portVol : 0;
    
    frontier.push({weights, expectedReturn: portReturn, volatility: portVol, sharpe});
  }
  
  // Sort by Sharpe ratio
  frontier.sort((a, b) => b.sharpe - a.sharpe);
  
  // Return top portfolios
  return frontier.slice(0, 50);
};
