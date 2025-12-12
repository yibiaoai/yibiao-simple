/**
 * 主应用组件
 */
import React from 'react';
import { useAppState } from './hooks/useAppState';
import ConfigPanel from './components/ConfigPanel';
import StepBar from './components/StepBar';
import DocumentAnalysis from './pages/DocumentAnalysis';
import OutlineEdit from './pages/OutlineEdit';
import ContentEdit from './pages/ContentEdit';

function App() {
  const {
    state,
    updateConfig,
    updateStep,
    updateFileContent,
    updateAnalysisResults,
    updateOutline,
    updateSelectedChapter,
    nextStep,
    prevStep,
  } = useAppState();

  const steps = ['标书解析', '目录编辑', '正文编辑'];

  const renderCurrentPage = () => {
    switch (state.currentStep) {
      case 0:
        return (
          <DocumentAnalysis
            fileContent={state.fileContent}
            projectOverview={state.projectOverview}
            techRequirements={state.techRequirements}
            onFileUpload={updateFileContent}
            onAnalysisComplete={updateAnalysisResults}
          />
        );
      case 1:
        return (
          <OutlineEdit
            projectOverview={state.projectOverview}
            techRequirements={state.techRequirements}
            outlineData={state.outlineData}
            onOutlineGenerated={updateOutline}
          />
        );
      case 2:
        return (
          <ContentEdit
            outlineData={state.outlineData}
            selectedChapter={state.selectedChapter}
            onChapterSelect={updateSelectedChapter}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-screen overflow-hidden bg-gray-50 flex">
      {/* 左侧配置面板 */}
      <ConfigPanel
        config={state.config}
        onConfigChange={updateConfig}
      />

      {/* 主内容区域 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 步骤导航 */}
        <div className="sticky top-0 z-50 bg-white shadow-sm px-6">
          <StepBar steps={steps} currentStep={state.currentStep} />
        </div>

        {/* 页面内容 */}
        <div id="app-main-scroll" className="flex-1 p-6 overflow-y-auto">
          {renderCurrentPage()}
        </div>

        {/* 底部导航按钮 */}
        <div className="sticky bottom-0 z-50 bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => updateStep(0)}
                disabled={state.currentStep === 0}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400 disabled:text-white disabled:cursor-not-allowed"
              >
                首页
              </button>

              <button
                onClick={prevStep}
                disabled={state.currentStep === 0}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
              >
                上一步
              </button>
            </div>

            <button
              onClick={nextStep}
              disabled={state.currentStep === steps.length - 1}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              下一步
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
