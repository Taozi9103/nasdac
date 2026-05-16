import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('Starting database seed...');

  // Clear existing data
  await prisma.assetPrice.deleteMany();
  await prisma.portfolioAsset.deleteMany();
  await prisma.correlation.deleteMany();
  await prisma.portfolio.deleteMany();
  await prisma.asset.deleteMany();
  await prisma.watchlistItem.deleteMany();
  await prisma.watchlist.deleteMany();
  await prisma.backtest.deleteMany();
  await prisma.strategy.deleteMany();
  await prisma.user.deleteMany();

  // Create default user first
  console.log('Creating default user...');
  const user = await prisma.user.create({
    data: {
      email: 'user@example.com',
      username: '默认用户',
      password: 'password123',
    },
  });

  console.log('Creating assets...');

  // Create sample assets
  const assets = await Promise.all([
    prisma.asset.create({
      data: {
        code: 'CSI000300',
        name: '沪深300',
        type: '指数',
      },
    }),
    prisma.asset.create({
      data: {
        code: 'SZ399006',
        name: '创业板指',
        type: '指数',
      },
    }),
    prisma.asset.create({
      data: {
        code: 'SH000688',
        name: '科创50',
        type: '指数',
      },
    }),
    prisma.asset.create({
      data: {
        code: '000001',
        name: '华夏成长混合',
        type: '基金',
      },
    }),
    prisma.asset.create({
      data: {
        code: '161725',
        name: '招商中证白酒指数',
        type: '基金',
      },
    }),
    prisma.asset.create({
      data: {
        code: '513100',
        name: '纳斯达克100ETF',
        type: '基金',
      },
    }),
    prisma.asset.create({
      data: {
        code: '518880',
        name: '黄金ETF',
        type: '基金',
      },
    }),
  ]);

  console.log(`Created ${assets.length} assets`);

  // Generate price data for each asset
  console.log('Generating price data...');
  
  for (const asset of assets) {
    const prices = [];
    let price = Math.random() * 10 + 1; // Starting price between 1 and 11
    
    // Generate 365 days of data
    for (let i = 0; i < 365; i++) {
      const date = new Date();
      date.setDate(date.getDate() - (365 - i));
      
      // Random walk with drift
      const dailyReturn = (Math.random() - 0.48) * 0.02; // Slight upward bias
      price = price * (1 + dailyReturn);
      
      const volatility = Math.random() * 0.03;
      const open = price * (1 + (Math.random() - 0.5) * volatility);
      const close = price;
      const high = Math.max(open, close) * (1 + Math.random() * volatility);
      const low = Math.min(open, close) * (1 - Math.random() * volatility);
      const volume = Math.random() * 10000000;
      
      prices.push({
        assetId: asset.id,
        date,
        open,
        high,
        low,
        close,
        volume,
        adjClose: close,
      });
    }
    
    await prisma.assetPrice.createMany({
      data: prices,
    });
  }

  console.log('Created price data for all assets');

  // Create a sample portfolio
  console.log('Creating sample portfolio...');
  
  const portfolio = await prisma.portfolio.create({
    data: {
      userId: user.id,
      name: '示例投资组合',
      description: '一个包含多个资产类别的示例组合',
      assets: {
        create: [
          { assetId: assets[0].id, weight: 0.3 },
          { assetId: assets[1].id, weight: 0.3 },
          { assetId: assets[5].id, weight: 0.2 },
          { assetId: assets[6].id, weight: 0.2 },
        ],
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

  console.log(`Created portfolio: ${portfolio.name}`);

  // Create sample watchlist
  const watchlist = await prisma.watchlist.create({
    data: {
      userId: user.id,
      name: '我的自选',
      items: {
        create: assets.slice(0, 5).map(asset => ({
          assetId: asset.id,
        })),
      },
    },
  });

  console.log(`Created watchlist: ${watchlist.name}`);

  // Create sample strategy
  const strategy = await prisma.strategy.create({
    data: {
      userId: user.id,
      name: '简单均线策略',
      description: '使用50日和200日均线的金叉死叉策略',
      rules: JSON.stringify({
        type: 'moving_average_crossover',
        shortMA: 50,
        longMA: 200,
      }),
      parameters: JSON.stringify({
        rebalanceFrequency: 'monthly',
        positionSize: 0.1,
      }),
    },
  });

  console.log(`Created strategy: ${strategy.name}`);

  console.log('\n✅ Database seeded successfully!');
  console.log('\nSample data summary:');
  console.log(`- Assets: ${assets.length}`);
  console.log(`- Price records: ${365 * assets.length}`);
  console.log(`- Portfolio: ${portfolio.name}`);
  console.log(`- Watchlist: ${watchlist.name}`);
  console.log(`- Strategy: ${strategy.name}`);
}

main()
  .catch((e) => {
    console.error('Error seeding database:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
