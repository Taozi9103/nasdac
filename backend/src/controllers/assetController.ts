import { Request, Response } from 'express';
import prisma from '../lib/prisma';

export const assetController = {
  async getAll(req: Request, res: Response) {
    try {
      const { type } = req.query;
      
      const whereClause: any = {};
      if (type) {
        whereClause.type = type;
      }
      
      const assets = await prisma.asset.findMany({
        where: whereClause,
        orderBy: { name: 'asc' },
      });
      
      res.json(assets);
    } catch (error) {
      console.error('Error fetching assets:', error);
      res.status(500).json({ error: 'Failed to fetch assets' });
    }
  },

  async getById(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const asset = await prisma.asset.findUnique({
        where: { id },
      });
      
      if (!asset) {
        return res.status(404).json({ error: 'Asset not found' });
      }
      
      res.json(asset);
    } catch (error) {
      console.error('Error fetching asset:', error);
      res.status(500).json({ error: 'Failed to fetch asset' });
    }
  },

  async getPrices(req: Request, res: Response) {
    try {
      const { id } = req.params;
      const { startDate, endDate, limit = '100' } = req.query;
      
      const whereClause: any = { assetId: id };
      if (startDate || endDate) {
        whereClause.date = {};
        if (startDate) {
          whereClause.date.gte = new Date(startDate as string);
        }
        if (endDate) {
          whereClause.date.lte = new Date(endDate as string);
        }
      }
      
      const prices = await prisma.assetPrice.findMany({
        where: whereClause,
        orderBy: { date: 'desc' },
        take: parseInt(limit as string),
      });
      
      res.json(prices.reverse());
    } catch (error) {
      console.error('Error fetching prices:', error);
      res.status(500).json({ error: 'Failed to fetch prices' });
    }
  },

  async search(req: Request, res: Response) {
    try {
      const { q } = req.query;
      
      if (!q || typeof q !== 'string') {
        return res.status(400).json({ error: 'Search query is required' });
      }
      
      const assets = await prisma.asset.findMany({
        where: {
          OR: [
            { name: { contains: q } },
            { code: { contains: q } },
          ],
        },
        take: 20,
      });
      
      res.json(assets);
    } catch (error) {
      console.error('Error searching assets:', error);
      res.status(500).json({ error: 'Failed to search assets' });
    }
  },
};
