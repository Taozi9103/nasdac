import { Router } from 'express';
import { portfolioController } from '../controllers/portfolioController';
import { analysisController } from '../controllers/analysisController';

const router = Router();

router.get('/', portfolioController.getAll);
router.get('/:id', portfolioController.getById);
router.post('/', portfolioController.create);
router.put('/:id', portfolioController.update);
router.delete('/:id', portfolioController.delete);

// Analysis endpoints
router.get('/:id/returns', analysisController.getAssetReturns);
router.get('/:id/correlation', analysisController.getCorrelationMatrix);
router.get('/:id/frontier', analysisController.getEfficientFrontier);
router.post('/:id/optimize', analysisController.optimizePortfolio);

export default router;
