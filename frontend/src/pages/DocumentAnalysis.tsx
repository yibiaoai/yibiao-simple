/**
 * 文档分析页面
 */
import React, { useState, useRef } from 'react';
import { documentApi } from '../services/api';
import { CloudArrowUpIcon, DocumentIcon } from '@heroicons/react/24/outline';

interface DocumentAnalysisProps {
  fileContent: string;
  projectOverview: string;
  techRequirements: string;
  onFileUpload: (content: string) => void;
  onAnalysisComplete: (overview: string, requirements: string) => void;
}

const DocumentAnalysis: React.FC<DocumentAnalysisProps> = ({
  fileContent,
  projectOverview,
  techRequirements,
  onFileUpload,
  onAnalysisComplete,
}) => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState<'overview' | 'requirements' | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [localOverview, setLocalOverview] = useState(projectOverview);
  const [localRequirements, setLocalRequirements] = useState(techRequirements);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true);
      setMessage(null);

      const response = await documentApi.uploadFile(file);
      
      if (response.data.success && response.data.file_content) {
        onFileUpload(response.data.file_content);
        setMessage({ type: 'success', text: response.data.message });
      } else {
        setMessage({ type: 'error', text: response.data.message });
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || '文件上传失败' });
    } finally {
      setUploading(false);
    }
  };

  const handleAnalysis = async (type: 'overview' | 'requirements') => {
    if (!fileContent) {
      setMessage({ type: 'error', text: '请先上传文档' });
      return;
    }

    try {
      setAnalyzing(type);
      setMessage(null);

      const response = await documentApi.analyzeDocumentStream({
        file_content: fileContent,
        analysis_type: type,
      });

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应流');
      }

      let result = '';
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              break;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                result += parsed.chunk;
                if (type === 'overview') {
                  setLocalOverview(result);
                } else {
                  setLocalRequirements(result);
                }
              }
            } catch (e) {
              // 忽略JSON解析错误
            }
          }
        }
      }

      // 完成后更新父组件状态
      if (type === 'overview') {
        onAnalysisComplete(result, localRequirements);
      } else {
        onAnalysisComplete(localOverview, result);
      }

      setMessage({ type: 'success', text: `${type === 'overview' ? '项目概述' : '技术评分要求'}分析完成` });
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || '分析失败' });
    } finally {
      setAnalyzing(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 文件上传区域 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">📄 文档上传</h2>
        
        <div 
          className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-gray-400 transition-colors cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
          <div className="mt-4">
            <p className="text-lg text-gray-600">
              {uploadedFile ? uploadedFile.name : '点击选择文件或拖拽文件到这里'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              支持 PDF 和 Word 文档，最大 10MB
            </p>
          </div>
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
        
        {uploading && (
          <div className="mt-4 text-center">
            <div className="inline-flex items-center px-4 py-2 text-sm text-blue-600">
              <div className="animate-spin -ml-1 mr-3 h-5 w-5 text-blue-600">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              正在上传和处理文件...
            </div>
          </div>
        )}
      </div>

      {/* 文档分析区域 */}
      {fileContent && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">🔍 文档分析</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <button
              onClick={() => handleAnalysis('overview')}
              disabled={analyzing !== null}
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
            >
              {analyzing === 'overview' ? (
                <>
                  <div className="animate-spin -ml-1 mr-3 h-4 w-4 text-white">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                  正在分析项目概述...
                </>
              ) : (
                '分析项目概述'
              )}
            </button>

            <button
              onClick={() => handleAnalysis('requirements')}
              disabled={analyzing !== null}
              className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400"
            >
              {analyzing === 'requirements' ? (
                <>
                  <div className="animate-spin -ml-1 mr-3 h-4 w-4 text-white">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                  正在分析技术评分要求...
                </>
              ) : (
                '分析技术评分要求'
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 项目概述 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                项目概述
              </label>
              <textarea
                value={localOverview}
                onChange={(e) => {
                  setLocalOverview(e.target.value);
                  onAnalysisComplete(e.target.value, localRequirements);
                }}
                rows={12}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
                placeholder="项目概述将在这里显示..."
              />
            </div>

            {/* 技术评分要求 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                技术评分要求
              </label>
              <textarea
                value={localRequirements}
                onChange={(e) => {
                  setLocalRequirements(e.target.value);
                  onAnalysisComplete(localOverview, e.target.value);
                }}
                rows={12}
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-green-500 focus:border-green-500 text-sm"
                placeholder="技术评分要求将在这里显示..."
              />
            </div>
          </div>
        </div>
      )}

      {/* 消息提示 */}
      {message && (
        <div className={`p-4 rounded-md ${
          message.type === 'success' 
            ? 'bg-green-100 text-green-700 border border-green-200' 
            : 'bg-red-100 text-red-700 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}
    </div>
  );
};

export default DocumentAnalysis;