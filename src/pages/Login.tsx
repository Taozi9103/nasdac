import { useState } from 'react';
import { Link } from 'react-router-dom';
import { User, Lock } from 'lucide-react';

const Login = () => {
  const [activeTab, setActiveTab] = useState<'login' | 'register' | 'forgot'>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-lg overflow-hidden">
        <div className="p-6 text-center">
          <h1 className="text-3xl font-bold text-slate-800 mb-3">量化小助手</h1>
          <Link
            to="/help/user-manual"
            className="text-blue-500 hover:text-blue-600 text-sm"
          >
            使用说明
          </Link>
        </div>

        <div className="flex border-b border-slate-200">
          <button
            onClick={() => setActiveTab('login')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'login'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            登录
          </button>
          <button
            onClick={() => setActiveTab('register')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'register'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            注册
          </button>
          <button
            onClick={() => setActiveTab('forgot')}
            className={`flex-1 py-3 text-sm font-medium transition-colors ${
              activeTab === 'forgot'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-slate-500 hover:text-slate-700'
            }`}
          >
            忘记密码
          </button>
        </div>

        <div className="p-6">
          {activeTab === 'login' && (
            <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="请输入用户名或邮箱"
                  className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input
                  type="password"
                  placeholder="请输入密码"
                  className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
              </div>
              <button
                type="submit"
                className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
              >
                登 录
              </button>
              <div className="text-right">
                <button
                  type="button"
                  onClick={() => setActiveTab('forgot')}
                  className="text-blue-500 hover:text-blue-600 text-sm"
                >
                  忘记密码？
                </button>
              </div>
            </form>
          )}

          {activeTab === 'register' && <RegisterForm />}
          {activeTab === 'forgot' && <ForgotPasswordForm onBackToLogin={() => setActiveTab('login')} />}
        </div>

        <div className="p-6 bg-amber-50 border-t border-amber-100">
          <h3 className="text-amber-800 font-medium mb-2 text-center">研究与风险说明</h3>
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 w-8 h-8 bg-amber-400 rounded-full flex items-center justify-center text-white text-lg">
              !
            </div>
            <p className="text-amber-700 text-sm leading-relaxed">
              本工具基于业余爱好开发，功能与数据精度无法与商业级专业软件相比，目前定位为学习与研究辅助。界面展示、回测与统计结果不构成任何形式的投资建议，请勿作为实盘交易或资金管理的决策依据。
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const RegisterForm = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');

  return (
    <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
      <div className="relative">
        <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
        <input
          type="text"
          placeholder="设置用户名"
          className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
      </div>
      <div className="relative">
        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
        <input
          type="password"
          placeholder="设置密码（至少6位）"
          className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>
      <div className="relative">
        <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
        <input
          type="email"
          placeholder="输入邮箱"
          className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="6位验证码"
          className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <button
          type="button"
          className="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg transition-colors whitespace-nowrap"
        >
          获取验证码
        </button>
      </div>
      <button
        type="submit"
        className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
      >
        验证并注册
      </button>
    </form>
  );
};

const ForgotPasswordForm = ({ onBackToLogin }: { onBackToLogin: () => void }) => {
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [newPassword, setNewPassword] = useState('');

  return (
    <form className="space-y-4" onSubmit={(e) => e.preventDefault()}>
      <div className="relative">
        <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
        <input
          type="email"
          placeholder="请输入注册邮箱"
          className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="请输入邮箱验证码"
          className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <button
          type="button"
          className="px-4 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium rounded-lg transition-colors whitespace-nowrap"
        >
          获取验证码
        </button>
      </div>
      <div className="relative">
        <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
        <input
          type="password"
          placeholder="请输入新密码（至少6位）"
          className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
        />
      </div>
      <button
        type="submit"
        className="w-full py-3 bg-blue-500 hover:bg-blue-600 text-white font-medium rounded-lg transition-colors"
      >
        重置密码
      </button>
      <div className="text-center">
        <button
          type="button"
          onClick={onBackToLogin}
          className="text-blue-500 hover:text-blue-600 text-sm"
        >
          返回登录
        </button>
      </div>
    </form>
  );
};

export default Login;
