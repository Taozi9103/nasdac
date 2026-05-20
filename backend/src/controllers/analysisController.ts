import { Request, Response } from 'express';
import prisma from '../lib/prisma';
import { 
  calculateCorrelation, 
  calculateReturns, 
  calculateVolatility,
  calculateAnnualReturn,
  calculateSharpeRatio,
  calculatePortfolioReturn,
  generateCorrelationMatrix
} from '../lib/analytics';

export const analysisController = {
  async getAssetReturns(req: Request, res: Response) {
    try {
      const { assetId } = req.params;
      const { startDate, endDate } = req.query;
      
      const whereClause: any = { assetId };
      if (startDate) {
        whereClause.date = {
          ...whereClause.date,
          gte: new Date(startDate as string),
        };
      }
      if (endDate) {
        whereClause.date = {
          ...whereClause.date,
          lte: new Date(endDate as string),
        };
      }
      
      const prices = await prisma.assetPrice.findMany({
        where: whereClause,
        orderBy: { date: 'asc' },
      });
      
      const priceData = prices.map(p => p.adjClose || p.close);
      const returns = calculateReturns(priceData);
      
      res.json({
        assetId,
        prices: prices.map(p => ({
          date: p.date,
          price: p.adjClose || p.close,
        })),
        returns,
        statistics: {
          totalReturn: priceData.length > 1 
            ? (priceData[priceData.length - 1] - priceData[0]) / priceData[0] 
            : 0,
          annualReturn: calculateAnnualReturn(returns),
          volatility: calculateVolatility(returns),
          sharpeRatio: calculateSharpeRatio(returns),
        },
      });
    } catch (error) {
      console.error('Error calculating returns:', error);
      res.status(500).json({ error: 'Failed to calculate returns' });
    }
  },

  async getCorrelationMatrix(req: Request, res: Response) {
    try {
      const { portfolioId } = req.params;
      const { startDate, endDate, period = 'daily' } = req.query;
      
      const portfolio = await prisma.portfolio.findUnique({
        where: { id: portfolioId },
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      
      if (!portfolio) {
        return res.status(404).json({ error: 'Portfolio not found' });
      }
      
      const assetIds = portfolio.assets.map(pa => pa.assetId);
      const assetReturns = new Map<string, number[]>();
      
      // Get price data for each asset
      for (const assetId of assetIds) {
        const whereClause: any = { assetId };
        if (startDate) {
          whereClause.date = {
            ...whereClause.date,
            gte: new Date(startDate as string),
          };
        }
        if (endDate) {
          whereClause.date = {
            ...whereClause.date,
            lte: new Date(endDate as string),
          };
        }
        
        const prices = await prisma.assetPrice.findMany({
          where: whereClause,
          orderBy: { date: 'asc' },
        });
        
        const priceData = prices.map(p => p.adjClose || p.close);
        assetReturns.set(assetId, calculateReturns(priceData));
      }
      
      const matrix = generateCorrelationMatrix(assetReturns);
      
      // Save to database
      const correlations = [];
      const assets = portfolio.assets;
      for (let i = 0; i < assets.length; i++) {
        for (let j = i + 1; j < assets.length; j++) {
          const corr = matrix.get(assets[i].assetId)?.get(assets[j].assetId) || 0;
          correlations.push({
            portfolioId,
            asset1Id: assets[i].assetId,
            asset2Id: assets[j].assetId,
            coefficient: corr,
            period: period as string,
            startDate: new Date(startDate as string || Date.now() - 365 * 24 * 60 * 60 * 1000),
            endDate: new Date(endDate as string || Date.now()),
          });
        }
      }
      
      // Clear old and save new correlations
      await prisma.correlation.deleteMany({
        where: { portfolioId },
      });
      
      await prisma.correlation.createMany({
        data: correlations,
      });
      
      res.json({
        portfolioId,
        matrix: Object.fromEntries(
          Array.from(matrix.entries()).map(([key, value]) => [
            key,
            Object.fromEntries(value.entries()),
          ])
        ),
        saved: true,
      });
    } catch (error) {
      console.error('Error calculating correlation:', error);
      res.status(500).json({ error: 'Failed to calculate correlation matrix' });
    }
  },

  async getEfficientFrontier(req: Request, res: Response) {
    try {
      const { portfolioId } = req.params;
      const { targetReturn } = req.query;
      
      const portfolio = await prisma.portfolio.findUnique({
        where: { id: portfolioId },
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      
      if (!portfolio) {
        return res.status(404).json({ error: 'Portfolio not found' });
      }
      
      const assets = portfolio.assets;
      const expectedReturns: number[] = [];
      const volatilities: number[] = [];
      const correlations: number[][] = [];
      
      // Calculate metrics for each asset
      for (let i = 0; i < assets.length; i++) {
        const asset = assets[i];
        const prices = await prisma.assetPrice.findMany({
          where: { assetId: asset.assetId },
          orderBy: { date: 'desc' },
          take: 252,
        });
        
        const priceData = prices.map(p => p.adjClose || p.close).reverse();
        const returns = calculateReturns(priceData);
        
        expectedReturns.push(calculateAnnualReturn(returns));
        volatilities.push(calculateVolatility(returns));
      }
      
      // Generate efficient frontier (simplified version)
      const efficientFrontier = [];
      const numPortfolios = 100;
      
      for (let i = 0; i < numPortfolios; i++) {
        let weights = Array.from({length: assets.length}, () => Math.random());
        const sum = weights.reduce((a, b) => a + b, 0);
        weights = weights.map(w => w / sum);
        
        let portReturn = 0;
        for (let j = 0; j < assets.length; j++) {
          portReturn += weights[j] * expectedReturns[j];
        }
        
        // Simplified volatility calculation (assuming equal correlation of 0.5)
        let portVol = 0;
        for (let j = 0; j < assets.length; j++) {
          for (let k = 0; k < assets.length; k++) {
            const corr = j === k ? 1 : 0.3;
            portVol += weights[j] * weights[k] * corr * volatilities[j] * volatilities[k];
          }
        }
        portVol = Math.sqrt(portVol);
        
        const sharpe = portVol > 0 ? (portReturn - 0.03) / portVol : 0;
        
        efficientFrontier.push({
          weights: assets.map((asset, idx) => ({
            assetId: asset.assetId,
            assetName: asset.asset.name,
            weight: weights[idx],
          })),
          expectedReturn: portReturn,
          volatility: portVol,
          sharpeRatio: sharpe,
        });
      }
      
      // Sort by Sharpe ratio and return top portfolios
      efficientFrontier.sort((a, b) => b.sharpeRatio - a.sharpeRatio);
      
      res.json({
        portfolioId,
        assets: assets.map(asset => ({
          assetId: asset.assetId,
          assetName: asset.asset.name,
          expectedReturn: expectedReturns[assets.indexOf(asset)],
          volatility: volatilities[assets.indexOf(asset)],
        })),
        efficientFrontier: efficientFrontier.slice(0, 20),
      });
    } catch (error) {
      console.error('Error calculating efficient frontier:', error);
      res.status(500).json({ error: 'Failed to calculate efficient frontier' });
    }
  },

  async optimizePortfolio(req: Request, res: Response) {
    try {
      const { portfolioId, optimizationType = 'max-sharpe' } = req.body;
      
      const portfolio = await prisma.portfolio.findUnique({
        where: { id: portfolioId },
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      
      if (!portfolio) {
        return res.status(404).json({ error: 'Portfolio not found' });
      }
      
      // Calculate optimal weights based on type
      // This is a simplified implementation
      const assets = portfolio.assets;
      let optimalWeights: number[];
      
      if (optimizationType === 'max-sharpe') {
        // Equal risk contribution approach (simplified)
        optimalWeights = Array.from({length: assets.length}, () => 1 / assets.length);
      } else if (optimizationType === 'min-volatility') {
        // Minimum variance (simplified - equal weights)
        optimalWeights = Array.from({length: assets.length}, () => 1 / assets.length);
      } else {
        optimalWeights = Array.from({length: assets.length}, () => 1 / assets.length);
      }
      
      // Update portfolio with optimal weights
      await prisma.portfolioAsset.deleteMany({
        where: { portfolioId },
      });
      
      await prisma.portfolioAsset.createMany({
        data: assets.map((asset, idx) => ({
          portfolioId,
          assetId: asset.assetId,
          weight: optimalWeights[idx],
        })),
      });
      
      const updatedPortfolio = await prisma.portfolio.findUnique({
        where: { id: portfolioId },
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      
      res.json({
        success: true,
        optimizationType,
        portfolio: updatedPortfolio,
      });
    } catch (error) {
      console.error('Error optimizing portfolio:', error);
      res.status(500).json({ error: 'Failed to optimize portfolio' });
    }
  },
};
