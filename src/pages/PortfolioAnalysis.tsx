import { useState } from 'react';
import { Check, ChevronRight, PieChart, TrendingUp, BarChart3, Target } from 'lucide-react';
import DataAlignment from '../components/portfolio/DataAlignment';
import CorrelationAnalysis from '../components/portfolio/CorrelationAnalysis';
import EfficientFrontier from '../components/portfolio/EfficientFrontier';
import RiskReturn from '../components/portfolio/RiskReturn';

const steps = [
  { id: 1, name: '数据对齐', icon: BarChart3, description: '选择投资标的并对齐数据' },
  { id: 2, name: '相关性分析', icon: TrendingUp, description: '分析标的间的相关性' },
  { id: 3, name: '有效前沿', icon: Target, description: '计算有效前沿和最优组合' },
  { id: 4, name: '风险收益搭配', icon: PieChart, description: '确定最终的资产配置' },
];

const PortfolioAnalysis = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [portfolioData, setPortfolioData] = useState({
    assets: [],
    returns: {},
    correlations: [],
  });

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrev = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <DataAlignment onDataUpdate={setPortfolioData} data={portfolioData} />;
      case 2:
        return <CorrelationAnalysis data={portfolioData} />;
      case 3:
        return <EfficientFrontier data={portfolioData} />;
      case 4:
        return <RiskReturn data={portfolioData} />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-800 mb-2">组合分析</h1>
        <p className="text-slate-600">按步骤完成投资组合的构建和分析</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <nav aria-label="Progress">
          <ol role="list" className="overflow-hidden">
            <li className="relative md:flex md:flex-1">
              <div className="flex items-center px-6 py-4 md:px-0">
                {steps.map((step, index) => (
                  <div key={step.id} className="flex items-center">
                    {/* Step connector */}
                    {index > 0 && (
                      <div className={`
                        flex-1 h-0.5 md:w-20 md:h-0.5 mx-4
                        ${index < currentStep ? 'bg-blue-500' : 'bg-slate-200'}
                      `} />
                    )}
                    
                    {/* Step indicator */}
                    <div className="relative z-10">
                      <button
                        onClick={() => setCurrentStep(step.id)}
                        className={`
                          flex items-center justify-center w-10 h-10 rounded-full border-2 font-semibold transition-all
                          ${step.id < currentStep
                            ? 'bg-blue-500 border-blue-500 text-white'
                            : step.id === currentStep
                            ? 'bg-blue-50 border-blue-500 text-blue-600'
                            : 'bg-white border-slate-300 text-slate-500 hover:border-slate-400'
                          }
                        `}
                      >
                        {step.id < currentStep ? (
                          <Check className="w-5 h-5" />
                        ) : (
                          <step.icon className="w-5 h-5" />
                        )}
                      </button>
                      
                      {/* Step label (desktop) */}
                      <div className="hidden md:block absolute top-12 left-1/2 -translate-x-1/2 whitespace-nowrap">
                        <p className={`
                          text-sm font-medium
                          ${step.id <= currentStep ? 'text-slate-900' : 'text-slate-500'}
                        `}>
                          {step.name}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </li>
          </ol>
        </nav>

        {/* Mobile step labels */}
        <div className="mt-6 flex justify-between md:hidden">
          {steps.map((step) => (
            <div
              key={step.id}
              className={`
                w-20 text-center text-xs
                ${step.id <= currentStep ? 'text-slate-900' : 'text-slate-500'}
              `}
            >
              {step.name}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-xl font-semibold text-slate-800">
            {steps[currentStep - 1].name}
          </h2>
          <p className="text-slate-600 text-sm">
            {steps[currentStep - 1].description}
          </p>
        </div>

        <div className="p-6">
          {renderStepContent()}
        </div>

        {/* Navigation Buttons */}
        <div className="px-6 py-4 bg-slate-50 border-t border-slate-200 flex justify-between">
          <button
            onClick={handlePrev}
            disabled={currentStep === 1}
            className={`
              px-6 py-2.5 rounded-lg text-sm font-medium transition-colors
              ${currentStep === 1
                ? 'text-slate-400 cursor-not-allowed'
                : 'text-slate-700 hover:bg-slate-200'
              }
            `}
          >
            上一步
          </button>
          <button
            onClick={handleNext}
            disabled={currentStep === steps.length}
            className={`
              px-6 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2
              ${currentStep === steps.length
                ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-600 text-white'
              }
            `}
          >
            {currentStep === steps.length ? '完成' : '下一步'}
            {currentStep < steps.length && <ChevronRight className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </div>
  );
};

export default PortfolioAnalysis;
