import { z } from 'zod';

export const createPortfolioSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  assets: z.array(z.object({
    assetId: z.string().uuid(),
    weight: z.number().min(0).max(1),
  })).min(1),
});

export const updatePortfolioSchema = z.object({
  name: z.string().min(1).max(100).optional(),
  description: z.string().optional(),
  assets: z.array(z.object({
    assetId: z.string().uuid(),
    weight: z.number().min(0).max(1),
  })).optional(),
});

export const createStrategySchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().optional(),
  rules: z.string(),
  parameters: z.string().optional(),
});

export const createBacktestSchema = z.object({
  strategyId: z.string().uuid(),
  startDate: z.string().transform(s => new Date(s)),
  endDate: z.string().transform(s => new Date(s)),
  initialCash: z.number().positive(),
});

export const createWatchlistSchema = z.object({
  name: z.string().min(1).max(100),
  assetIds: z.array(z.string().uuid()).optional(),
});

export type CreatePortfolioInput = z.infer<typeof createPortfolioSchema>;
export type UpdatePortfolioInput = z.infer<typeof updatePortfolioSchema>;
export type CreateStrategyInput = z.infer<typeof createStrategySchema>;
export type CreateBacktestInput = z.infer<typeof createBacktestSchema>;
export type CreateWatchlistInput = z.infer<typeof createWatchlistSchema>;
