import express from 'express';
import cors from 'cors';
import portfolioRoutes from './routes/portfolio';
import assetRoutes from './routes/assets';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/assets', assetRoutes);
app.use('/api/portfolios', portfolioRoutes);

// Error handling middleware
app.use((err: any, req: express.Request, res: express.Response, next: express.NextFunction) => {
  console.error('Error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Not found' });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log(`API endpoints:`);
  console.log(`  GET  /health`);
  console.log(`  GET  /api/assets`);
  console.log(`  GET  /api/assets/search?q=`);
  console.log(`  GET  /api/assets/:id`);
  console.log(`  GET  /api/assets/:id/prices`);
  console.log(`  GET  /api/portfolios`);
  console.log(`  GET  /api/portfolios/:id`);
  console.log(`  POST /api/portfolios`);
  console.log(`  PUT  /api/portfolios/:id`);
  console.log(`  DELETE /api/portfolios/:id`);
  console.log(`  GET  /api/portfolios/:id/returns`);
  console.log(`  GET  /api/portfolios/:id/correlation`);
  console.log(`  GET  /api/portfolios/:id/frontier`);
  console.log(`  POST /api/portfolios/:id/optimize`);
});
