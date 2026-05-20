import { Link } from 'react-router-dom';

const UserManual = () => {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="mb-8">
          <Link
            to="/"
            className="text-blue-500 hover:text-blue-600 text-sm flex items-center gap-1"
          >
            <span>←</span> 返回登录
          </Link>
        </div>

        <div className="bg-white rounded-2xl shadow-sm p-8">
          <h1 className="text-3xl font-bold text-slate-800 mb-8 text-center">量化小助手 — 用户手册</h1>

          <div className="mb-8">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-slate-100">
                  <th className="border border-slate-300 px-4 py-2 text-left">项</th>
                  <th className="border border-slate-300 px-4 py-2 text-left">说明</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td className="border border-slate-300 px-4 py-2 font-medium">风险提示</td>
                  <td className="border border-slate-300 px-4 py-2">本工具用于学习与研究；页面上任何数字、曲线都不构成投资建议</td>
                </tr>
              </tbody>
            </table>
          </div>

          <h2 className="text-2xl font-bold text-slate-700 mb-4">1. 这是款什么软件</h2>
          <ul className="list-disc list-inside space-y-2 mb-8 text-slate-600">
            <li>看一眼：系统里有多少基金、指数、股票等；数据更新到哪天了。</li>
            <li>整理名单：把自己的关注列表分成几个组（自选组），后面分析时一键选用。</li>
            <li>看现成的表：系统每日更新各种统计表格「谁涨得好、谁跌得多、基金榜单」等；需要时自己搜一搜、排排序。</li>
            <li>看几只标的一起动：涨跌有多像（相关性图、热力图）。</li>
            <li>自己配一篮子（组合分析）：按步骤做「数据对齐 → 相关性 → 有效前沿 →风险收益搭配」等分析。</li>
            <li>试策略：比如定投、再平衡、轮动规则，用历史数据模拟跑一遍（回测）；需要时还能开「影子」跟踪后续信号（实盘模拟）。</li>
            <li>看公开策略：排行榜里看别人公开的策略，会员在作者允许时可以关注或复制到自己的库里。</li>
          </ul>

          <h2 className="text-2xl font-bold text-slate-700 mb-4">2. 第一次上手</h2>
          <ol className="list-decimal list-inside space-y-4 mb-8 text-slate-600">
            <li>
              用邮箱注册，验证一下就能进。
            </li>
            <li>
              顶部的「首页」点一下，看看左侧的菜单，感受一下：
              <ul className="list-disc list-inside ml-6 mt-2 space-y-1">
                <li>先看「数据概览」，知道有哪些品种。</li>
                <li>再看「每日统计表」，这里列了所有可用的表格，挑感兴趣的点进去，注意表格上有排序、搜索。</li>
                <li>再点「自选管理」，随便建个自选组，加几只标的进去；后面会用到。</li>
              </ul>
            </li>
          </ol>

          <h2 className="text-2xl font-bold text-slate-700 mb-4">3. 概念说明</h2>
          <div className="space-y-4 mb-8 text-slate-600">
            <div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">3.1 品种、标的、资产</h3>
              <p className="ml-4">
                混用，指基金、指数、股票等；系统里会在不同页面按品种显示。
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">3.2 代码、ID</h3>
              <p className="ml-4">
                基金就是真实的6位基金代码，股票也一样。对于指数，为了不混淆，在原指数代码前加了字母前缀：
                <ul className="list-disc list-inside ml-6 mt-2 space-y-1">
                  <li>CSI：中证指数，比如 CSI000300（沪深300）。</li>
                  <li>SH：上证指数、科创50、上证180等，比如 SH000001（上证指数）、SH000688（科创50）。</li>
                  <li>SZ：深证成指、创业板指、深证100等，比如 SZ399001（深证成指）、SZ399006（创业板指）。</li>
                  <li>WIND：万得编制的指数（万得全A、万得偏股混等）。</li>
                  <li>GB：国债期货、十年期国债活跃券等，属于「自己编的」。</li>
                </ul>
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">3.3 自选组（自选）</h3>
              <p className="ml-4">
                自选组相当于「股池 / 基金池」。可以建多个，比如「指数宝」「主动鸡」「港股抄底」等，方便后面分析时一键选用。
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">3.4 复权、分红</h3>
              <p className="ml-4">
                看基金、股票的收益，分红再投是最自然的方式。系统里所有走势、计算都默认用「后复权 / 分红再投」。
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-700 mb-2">3.5 交易日、自然日</h3>
              <p className="ml-4">
                一般说「20个交易日」是指去除周末和节假日后的天数。系统里默认用交易日。
              </p>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-700 mb-4">4. 常见问题</h2>
          <div className="space-y-4 mb-8 text-slate-600">
            <div className="bg-slate-50 rounded-lg p-4">
              <h3 className="font-semibold text-slate-800 mb-2">Q：数据会不会不准？会不会有未来函数？会不会偷改历史？</h3>
              <p>
                A：（1）数据源主要是 Tushare 和 AkShare 公开采集的数据，另外有一部分指数（万得、恒生、纳斯达克、标普、德国DAX、日经225）来自其他公开渠道，我们做了清洗和补全，但不保证和Wind/东方财富完全一致；如果你发现某只标的走势或净值明显不对，请在群里或社区里告诉我们，我们排查一下。（2）系统在设计上极力避免未来函数，除了一个例外：「每日统计表」里的表格是用截至当日的全集算出来的（比如「近一年涨跌幅」），所以选基/选股逻辑如果基于这些表格，可能含有一定的未来信息；如果对此非常敏感，建议用策略（回测）功能。（3）历史不会偷改；系统在技术上保证，你上次看的结果和这次一样，除非你显式点了「重新生成」。
              </p>
            </div>
            <div className="bg-slate-50 rounded-lg p-4">
              <h3 className="font-semibold text-slate-800 mb-2">Q：策略是啥？能不能自动下单？</h3>
              <p>
                A：（1）策略 = 标的池 + 调仓规则 + 参数，在「策略/回测」里创建和运行。你可以理解成「一个公式化的交易计划」。举个例子：「标的池是我的自选组A，每个月看一眼，选近20天涨幅最高的3只，等权买入，满仓轮动」，这就是一个策略。（2）系统目前没有接入券商，不能自动下单；运行完策略会有交易记录，可以照着手动下单，或者用「影子跟踪」每天看信号。
              </p>
            </div>
            <div className="bg-slate-50 rounded-lg p-4">
              <h3 className="font-semibold text-slate-800 mb-2">Q：能看港股、美股、原油、黄金吗？</h3>
              <p>
                A：目前能看美股的纳斯达克100、标普500指数（代码NDX、SPX），以及港股的恒生指数（代码HSI）、恒生科技（代码HSTECH）。更多品种还在慢慢加。
              </p>
            </div>
            <div className="bg-slate-50 rounded-lg p-4">
              <h3 className="font-semibold text-slate-800 mb-2">Q：如何给建议/反馈？</h3>
              <p>
                A：在社区里发帖，或者在群里说。
              </p>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-700 mb-4">5. 下一步</h2>
          <ul className="list-disc list-inside space-y-2 text-slate-600">
            <li>开始使用：回到首页，建自选、翻表格、选标的、做组合、跑策略。</li>
            <li>如果有帮助，欢迎推荐给朋友。</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default UserManual;
