/**
 * 目录编辑页面
 */
import React, { useState } from 'react';
import { OutlineData, OutlineItem } from '../types';
import { outlineApi } from '../services/api';
import { ChevronRightIcon, ChevronDownIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

interface OutlineEditProps {
  projectOverview: string;
  techRequirements: string;
  outlineData: OutlineData | null;
  onOutlineGenerated: (outline: OutlineData) => void;
}

const OutlineEdit: React.FC<OutlineEditProps> = ({
  projectOverview,
  techRequirements,
  outlineData,
  onOutlineGenerated,
}) => {
  const [generating, setGenerating] = useState(false);
  const [generatingContent, setGeneratingContent] = useState(false);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleGenerateOutline = async () => {
    if (!projectOverview || !techRequirements) {
      setMessage({ type: 'error', text: '请先完成文档分析' });
      return;
    }

    try {
      setGenerating(true);
      setMessage(null);

      const response = await outlineApi.generateOutlineStream({
        overview: projectOverview,
        requirements: techRequirements,
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
              }
            } catch (e) {
              // 忽略JSON解析错误
            }
          }
        }
      }

      // 解析最终结果
      try {
        const outlineJson = JSON.parse(result);
        onOutlineGenerated(outlineJson);
        setMessage({ type: 'success', text: '目录结构生成完成' });
        
        // 默认展开所有项目
        const allIds = new Set<string>();
        const collectIds = (items: OutlineItem[]) => {
          items.forEach(item => {
            allIds.add(item.id);
            if (item.children) {
              collectIds(item.children);
            }
          });
        };
        collectIds(outlineJson.outline);
        setExpandedItems(allIds);
        
      } catch (parseError) {
        throw new Error('解析目录结构失败');
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || '目录生成失败' });
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateContent = async () => {
    if (!outlineData) {
      setMessage({ type: 'error', text: '请先生成目录结构' });
      return;
    }

    try {
      setGeneratingContent(true);
      setMessage(null);

      const response = await outlineApi.generateContentStream({
        outline: outlineData,
        project_overview: projectOverview,
      });

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应流');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              break;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.status === 'completed' && parsed.result) {
                onOutlineGenerated(parsed.result);
                setMessage({ type: 'success', text: '内容生成完成' });
              } else if (parsed.status === 'error') {
                throw new Error(parsed.message);
              }
            } catch (e) {
              // 忽略JSON解析错误
            }
          }
        }
      }
    } catch (error: any) {
      setMessage({ type: 'error', text: error.message || '内容生成失败' });
    } finally {
      setGeneratingContent(false);
    }
  };

  const toggleExpanded = (itemId: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const renderOutlineItem = (item: OutlineItem, level: number = 0) => {
    const hasChildren = item.children && item.children.length > 0;
    const isExpanded = expandedItems.has(item.id);
    const isLeaf = !hasChildren;

    return (
      <div key={item.id} className={`${level > 0 ? 'ml-6' : ''}`}>
        <div className="flex items-start space-x-2 py-2 hover:bg-gray-50 rounded px-2">
          {hasChildren ? (
            <button
              onClick={() => toggleExpanded(item.id)}
              className="mt-1 p-0.5 rounded hover:bg-gray-200"
            >
              {isExpanded ? (
                <ChevronDownIcon className="h-4 w-4 text-gray-400" />
              ) : (
                <ChevronRightIcon className="h-4 w-4 text-gray-400" />
              )}
            </button>
          ) : (
            <DocumentTextIcon className="mt-1 h-4 w-4 text-gray-400" />
          )}
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <span className={`text-sm font-medium ${
                level === 0 ? 'text-blue-600' :
                level === 1 ? 'text-green-600' :
                'text-gray-700'
              }`}>
                {item.id} {item.title}
              </span>
              {item.content && (
                <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  已生成内容
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1">{item.description}</p>
            
            {/* 显示生成的内容（如果有） */}
            {item.content && isLeaf && (
              <div className="mt-2 p-3 bg-gray-50 rounded-md border-l-4 border-blue-200">
                <div className="text-xs text-gray-600 whitespace-pre-wrap">{item.content}</div>
              </div>
            )}
          </div>
        </div>
        
        {hasChildren && isExpanded && (
          <div>
            {item.children!.map(child => renderOutlineItem(child, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* 操作按钮 */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">📋 目录管理</h2>
        
        <div className="flex space-x-4">
          <button
            onClick={handleGenerateOutline}
            disabled={generating || !projectOverview || !techRequirements}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400"
          >
            {generating ? (
              <>
                <div className="animate-spin -ml-1 mr-3 h-4 w-4 text-white">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                正在生成目录...
              </>
            ) : (
              '生成目录结构'
            )}
          </button>

          {outlineData && (
            <button
              onClick={handleGenerateContent}
              disabled={generatingContent}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400"
            >
              {generatingContent ? (
                <>
                  <div className="animate-spin -ml-1 mr-3 h-4 w-4 text-white">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                  正在生成内容...
                </>
              ) : (
                '生成章节内容'
              )}
            </button>
          )}
        </div>

        {!projectOverview && !techRequirements && (
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-sm text-yellow-800">
              请先在"标书解析"步骤中完成文档分析，获取项目概述和技术评分要求。
            </p>
          </div>
        )}
      </div>

      {/* 目录结构显示 */}
      {outlineData && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">目录结构</h3>
          <div className="border rounded-lg p-4 max-h-96 overflow-y-auto">
            {outlineData.outline.map(item => renderOutlineItem(item))}
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

export default OutlineEdit;