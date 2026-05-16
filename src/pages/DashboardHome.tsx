import { Link } from 'react-router-dom';
import { TrendingUp, PieChart, BarChart3, Calendar, ArrowRight } from 'lucide-react';

const DashboardHome = () => {
  const quickActions = [
    {
      title: '组合分析',
      description: '构建和优化您的投资组合',
      icon: PieChart,
      path: '/app/analysis',
      color: 'bg-blue-500',
    },
    {
      title: '策略回测',
      description: '测试您的投资策略表现',
      icon: TrendingUp,
      path: '/app/strategy',
      color: 'bg-green-500',
    },
    {
      title: '数据概览',
      description: '查看市场数据和统计',
      icon: BarChart3,
      path: '/app/overview',
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="space-y-8">
      {/* 欢迎区域 */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">欢迎使用量化小助手</h1>
        <p className="text-blue-100 text-lg">让数据驱动您的投资决策</p>
      </div>

      {/* 快捷操作 */}
      <div>
        <h2 className="text-xl font-semibold text-slate-800 mb-4">快捷操作</h2>
        <div className="grid md:grid-cols-3 gap-4">
          {quickActions.map((action) => (
            <Link
              key={action.path}
              to={action.path}
              className="group bg-white rounded-xl p-6 border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all"
            >
              <div className={`w-12 h-12 ${action.color} rounded-lg flex items-center justify-center mb-4`}>
                <action.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900 mb-1">{action.title}</h3>
              <p className="text-sm text-slate-600 mb-4">{action.description}</p>
              <div className="flex items-center text-blue-600 text-sm font-medium group-hover:text-blue-700">
                开始使用
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* 最近活动 */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-slate-500" />
            最近活动
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-slate-700">创建了新的投资组合</p>
                <p className="text-xs text-slate-500">2025-05-15</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
              <div className="flex-1">
                <p className="text-sm text-slate-700">完成了策略回测</p>
                <p className="text-xs text-slate-500">2025-05-14</p>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-6">
          <h3 className="text-lg font-semibold text-slate-900 mb-4">系统提示</h3>
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
            <p className="text-sm text-amber-800">
              目前系统使用模拟数据，实际使用时需要连接真实的数据源。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
