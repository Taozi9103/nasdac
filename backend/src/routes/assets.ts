import { Router } from 'express';
import { assetController } from '../controllers/assetController';

const router = Router();

router.get('/', assetController.getAll);
router.get('/search', assetController.search);
router.get('/:id', assetController.getById);
router.get('/:id/prices', assetController.getPrices);

export default router;
