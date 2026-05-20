# 量化小助手 - 后端 API 文档

## 快速开始

### 1. 安装依赖
```bash
cd backend
npm install
```

### 2. 初始化数据库
```bash
# 生成 Prisma Client
npm run db:generate

# 创建数据库表
npm run db:push

# 填充示例数据
npm run db:seed
```

### 3. 启动服务器
```bash
npm run dev
```

服务器将在 http://localhost:3000 运行。

## API 端点

### 健康检查
```
GET /health
```

### 资产相关 API

#### 获取所有资产
```
GET /api/assets
```

#### 搜索资产
```
GET /api/assets/search?q=关键词
```

#### 获取单个资产
```
GET /api/assets/:id
```

#### 获取资产价格历史
```
GET /api/assets/:id/prices?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&limit=100
```

### 投资组合相关 API

#### 获取所有投资组合
```
GET /api/portfolios
```

#### 获取单个投资组合
```
GET /api/portfolios/:id
```

#### 创建投资组合
```
POST /api/portfolios
Content-Type: application/json

{
  "name": "新组合",
  "description": "组合描述",
  "userId": "用户ID",
  "assets": [
    { "assetId": "资产UUID", "weight": 0.5 },
    { "assetId": "资产UUID", "weight": 0.5 }
  ]
}
```

#### 更新投资组合
```
PUT /api/portfolios/:id
Content-Type: application/json

{
  "name": "新名称",
  "description": "新描述",
  "assets": [
    { "assetId": "资产UUID", "weight": 0.3 },
    { "assetId": "资产UUID", "weight": 0.7 }
  ]
}
```

#### 删除投资组合
```
DELETE /api/portfolios/:id
```

### 组合分析 API

#### 获取资产收益率和统计
```
GET /api/portfolios/:id/returns?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD
```

响应示例：
```json
{
  "assetId": "资产UUID",
  "prices": [
    { "date": "2025-01-01", "price": 10.5 },
    { "date": "2025-01-02", "price": 10.8 }
  ],
  "returns": [0.0286, -0.015],
  "statistics": {
    "totalReturn": 0.15,
    "annualReturn": 0.12,
    "volatility": 0.18,
    "sharpeRatio": 0.65
  }
}
```

#### 计算相关性矩阵
```
GET /api/portfolios/:id/correlation?startDate=YYYY-MM-DD&endDate=YYYY-MM-DD&period=daily
```

响应示例：
```json
{
  "portfolioId": "组合UUID",
  "matrix": {
    "asset1_id": {
      "asset1_id": 1.0,
      "asset2_id": 0.65
    },
    "asset2_id": {
      "asset1_id": 0.65,
      "asset2_id": 1.0
    }
  },
  "saved": true
}
```

#### 计算有效前沿
```
GET /api/portfolios/:id/frontier?targetReturn=0.15
```

响应示例：
```json
{
  "portfolioId": "组合UUID",
  "assets": [
    {
      "assetId": "资产UUID",
      "assetName": "沪深300",
      "expectedReturn": 0.12,
      "volatility": 0.18
    }
  ],
  "efficientFrontier": [
    {
      "weights": [
        { "assetId": "UUID", "assetName": "名称", "weight": 0.5 }
      ],
      "expectedReturn": 0.15,
      "volatility": 0.12,
      "sharpeRatio": 1.0
    }
  ]
}
```

#### 优化组合权重
```
POST /api/portfolios/:id/optimize
Content-Type: application/json

{
  "optimizationType": "max-sharpe"
}
```

可选的优化类型：
- `max-sharpe`: 最大夏普比率
- `min-volatility`: 最小波动率
- `equal-weight`: 等权重

## 数据库结构

### 主要数据模型

1. **User** - 用户信息
2. **Asset** - 投资标的（基金、股票、指数等）
3. **AssetPrice** - 价格历史数据
4. **Portfolio** - 投资组合
5. **PortfolioAsset** - 组合中的资产及其权重
6. **Correlation** - 相关性数据
7. **Strategy** - 投资策略
8. **Backtest** - 回测结果
9. **Watchlist** - 自选列表
10. **WatchlistItem** - 自选列表中的标的

## 技术栈

- **运行时**: Node.js + TypeScript
- **框架**: Express.js
- **ORM**: Prisma
- **数据库**: SQLite（开发环境）
- **验证**: Zod

## 示例数据

种子脚本会创建：
- 1 个默认用户
- 7 个示例资产（沪深300、创业板指、科创50、3只基金、黄金ETF）
- 365 天的模拟价格数据
- 1 个示例投资组合
- 1 个示例自选列表
- 1 个示例投资策略
