import { Request, Response } from 'express';
import prisma from '../lib/prisma';
import { createPortfolioSchema, updatePortfolioSchema } from '../lib/validators';

export const portfolioController = {
  async getAll(req: Request, res: Response) {
    try {
      const portfolios = await prisma.portfolio.findMany({
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      res.json(portfolios);
    } catch (error) {
      console.error('Error fetching portfolios:', error);
      res.status(500).json({ error: 'Failed to fetch portfolios' });
    }
  },

  async getById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const portfolio = await prisma.portfolio.findUnique({
        where: { id },
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
          correlations: true,
        },
      });
      
      if (!portfolio) {
        return res.status(404).json({ error: 'Portfolio not found' });
      }
      
      res.json(portfolio);
    } catch (error) {
      console.error('Error fetching portfolio:', error);
      res.status(500).json({ error: 'Failed to fetch portfolio' });
    }
  },

  async create(req: Request, res: Response) {
    try {
      const data = createPortfolioSchema.parse(req.body);
      
      const portfolio = await prisma.portfolio.create({
        data: {
          userId: data.userId || 'default-user',
          name: data.name,
          description: data.description,
          assets: {
            create: data.assets.map(asset => ({
              assetId: asset.assetId,
              weight: asset.weight,
            })),
          },
        },
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      
      res.status(201).json(portfolio);
    } catch (error: any) {
      console.error('Error creating portfolio:', error);
      if (error.name === 'ZodError') {
        return res.status(400).json({ error: 'Invalid input', details: error.errors });
      }
      res.status(500).json({ error: 'Failed to create portfolio' });
    }
  },

  async update(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const data = updatePortfolioSchema.parse(req.body);
      
      // Update basic info
      const updateData: any = {};
      if (data.name) updateData.name = data.name;
      if (data.description !== undefined) updateData.description = data.description;
      
      // Update assets if provided
      if (data.assets) {
        // Delete existing assets
        await prisma.portfolioAsset.deleteMany({
          where: { portfolioId: id },
        });
        
        // Create new assets
        await prisma.portfolioAsset.createMany({
          data: data.assets.map(asset => ({
            portfolioId: id,
            assetId: asset.assetId,
            weight: asset.weight,
          })),
        });
      }
      
      const portfolio = await prisma.portfolio.update({
        where: { id },
        data: updateData,
        include: {
          assets: {
            include: {
              asset: true,
            },
          },
        },
      });
      
      res.json(portfolio);
    } catch (error: any) {
      console.error('Error updating portfolio:', error);
      if (error.name === 'ZodError') {
        return res.status(400).json({ error: 'Invalid input', details: error.errors });
      }
      res.status(500).json({ error: 'Failed to update portfolio' });
    }
  },

  async delete(req: Request, res: Response) {
    try {
      const { id } = req.params;
      await prisma.portfolio.delete({
        where: { id },
      });
      res.status(204).send();
    } catch (error) {
      console.error('Error deleting portfolio:', error);
      res.status(500).json({ error: 'Failed to delete portfolio' });
    }
  },
};
