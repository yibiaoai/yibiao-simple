/**
 * 应用状态管理Hook
 */
import { useState, useCallback } from 'react';
import { AppState, ConfigData, OutlineData } from '../types';

const initialState: AppState = {
  currentStep: 0,
  config: {
    api_key: '',
    base_url: '',
    model_name: 'gpt-3.5-turbo',
  },
  fileContent: '',
  projectOverview: '',
  techRequirements: '',
  outlineData: null,
  selectedChapter: '',
};

export const useAppState = () => {
  const [state, setState] = useState<AppState>(initialState);

  const updateConfig = useCallback((config: ConfigData) => {
    setState(prev => ({ ...prev, config }));
  }, []);

  const updateStep = useCallback((step: number) => {
    setState(prev => ({ ...prev, currentStep: step }));
  }, []);

  const updateFileContent = useCallback((fileContent: string) => {
    setState(prev => ({ ...prev, fileContent }));
  }, []);

  const updateAnalysisResults = useCallback((overview: string, requirements: string) => {
    setState(prev => ({ 
      ...prev, 
      projectOverview: overview,
      techRequirements: requirements 
    }));
  }, []);

  const updateOutline = useCallback((outlineData: OutlineData) => {
    setState(prev => ({ ...prev, outlineData }));
  }, []);

  const updateSelectedChapter = useCallback((chapterId: string) => {
    setState(prev => ({ ...prev, selectedChapter: chapterId }));
  }, []);

  const nextStep = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      currentStep: Math.min(prev.currentStep + 1, 2) 
    }));
  }, []);

  const prevStep = useCallback(() => {
    setState(prev => ({ 
      ...prev, 
      currentStep: Math.max(prev.currentStep - 1, 0) 
    }));
  }, []);

  return {
    state,
    updateConfig,
    updateStep,
    updateFileContent,
    updateAnalysisResults,
    updateOutline,
    updateSelectedChapter,
    nextStep,
    prevStep,
  };
};