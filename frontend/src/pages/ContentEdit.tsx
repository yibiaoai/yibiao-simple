/**
 * 内容编辑页面 - 完整标书预览和生成
 */
import React, { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { OutlineData, OutlineItem } from '../types';
import { DocumentTextIcon, PlayIcon, DocumentArrowDownIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline';
import { contentApi, ChapterContentRequest } from '../services/api';
import { saveAs } from 'file-saver';
import { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } from 'docx';

interface ContentEditProps {
  outlineData: OutlineData | null;
  selectedChapter: string;
  onChapterSelect: (chapterId: string) => void;
}

interface GenerationProgress {
  total: number;
  completed: number;
  current: string;
  failed: string[];
  generating: Set<string>; // 正在生成的项目ID集合
}

const ContentEdit: React.FC<ContentEditProps> = ({
  outlineData,
  selectedChapter,
  onChapterSelect,
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<GenerationProgress>({
    total: 0,
    completed: 0,
    current: '',
    failed: [],
    generating: new Set<string>()
  });
  const [leafItems, setLeafItems] = useState<OutlineItem[]>([]);

  // 收集所有叶子节点
  const collectLeafItems = useCallback((items: OutlineItem[]): OutlineItem[] => {
    let leaves: OutlineItem[] = [];
    items.forEach(item => {
      if (!item.children || item.children.length === 0) {
        leaves.push(item);
      } else {
        leaves = leaves.concat(collectLeafItems(item.children));
      }
    });
    return leaves;
  }, []);

  // 获取章节的上级章节信息
  const getParentChapters = useCallback((targetId: string, items: OutlineItem[], parents: OutlineItem[] = []): OutlineItem[] => {
    for (const item of items) {
      if (item.id === targetId) {
        return parents;
      }
      if (item.children && item.children.length > 0) {
        const found = getParentChapters(targetId, item.children, [...parents, item]);
        if (found.length > 0 || item.children.some(child => child.id === targetId)) {
          return found.length > 0 ? found : [...parents, item];
        }
      }
    }
    return [];
  }, []);

  // 获取章节的同级章节信息
  const getSiblingChapters = useCallback((targetId: string, items: OutlineItem[]): OutlineItem[] => {
    // 直接在当前级别查找
    if (items.some(item => item.id === targetId)) {
      return items;
    }
    
    // 递归在子级别查找
    for (const item of items) {
      if (item.children && item.children.length > 0) {
        const siblings = getSiblingChapters(targetId, item.children);
        if (siblings.length > 0) {
          return siblings;
        }
      }
    }
    
    return [];
  }, []);

  useEffect(() => {
    if (outlineData) {
      const leaves = collectLeafItems(outlineData.outline);
      setLeafItems(leaves);
      setProgress(prev => ({ ...prev, total: leaves.length }));
    }
  }, [outlineData, collectLeafItems]);

  // 获取叶子节点的实时内容
  const getLeafItemContent = (itemId: string): string | undefined => {
    const leafItem = leafItems.find(leaf => leaf.id === itemId);
    return leafItem?.content;
  };

  // 检查是否为叶子节点
  const isLeafNode = (item: OutlineItem): boolean => {
    return !item.children || item.children.length === 0;
  };

  // 渲染目录结构
  const renderOutline = (items: OutlineItem[], level: number = 1): React.ReactElement[] => {
    return items.map((item) => {
      const isLeaf = isLeafNode(item);
      const currentContent = isLeaf ? getLeafItemContent(item.id) : item.content;
      
      return (
        <div key={item.id} className={`mb-${level === 1 ? '8' : '4'}`}>
          {/* 标题 */}
          <div className={`text-${level === 1 ? 'xl' : level === 2 ? 'lg' : 'base'} font-${level === 1 ? 'bold' : 'semibold'} text-gray-900 mb-2`}>
            {item.id} {item.title}
          </div>
          
          {/* 描述 */}
          <div className="text-sm text-gray-600 mb-4">
            {item.description}
          </div>

          {/* 内容（仅叶子节点） */}
          {isLeaf && (
            <div className="border-l-4 border-blue-200 pl-4 mb-6">
              {currentContent ? (
                <div className="prose max-w-none">
                  <ReactMarkdown>{currentContent}</ReactMarkdown>
                </div>
              ) : (
                <div className="text-gray-400 italic py-4">
                  <DocumentTextIcon className="inline w-4 h-4 mr-2" />
                  {progress.generating.has(item.id) ? (
                    <span className="text-blue-600">正在生成内容...</span>
                  ) : (
                    '内容待生成...'
                  )}
                </div>
              )}
            </div>
          )}

          {/* 子章节 */}
          {item.children && item.children.length > 0 && (
            <div className={`ml-${level * 4} mt-4`}>
              {renderOutline(item.children, level + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  // 生成单个章节内容
  const generateItemContent = async (item: OutlineItem, projectOverview: string): Promise<OutlineItem> => {
    if (!outlineData) throw new Error('缺少目录数据');
    
    // 将当前项目添加到正在生成的集合中
    setProgress(prev => ({ 
      ...prev, 
      current: item.title,
      generating: new Set([...Array.from(prev.generating), item.id])
    }));
    
    try {
      // 获取上级章节和同级章节信息
      const parentChapters = getParentChapters(item.id, outlineData.outline);
      const siblingChapters = getSiblingChapters(item.id, outlineData.outline);

      const request: ChapterContentRequest = {
        chapter: item,
        parent_chapters: parentChapters,
        sibling_chapters: siblingChapters,
        project_overview: projectOverview
      };

      const response = await contentApi.generateChapterContentStream(request);

      if (!response.ok) throw new Error('生成失败');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('无法读取响应');

      let content = '';
      const updatedItem = { ...item };
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') continue;
            
            try {
              const parsed = JSON.parse(data);
              
              if (parsed.status === 'streaming' && parsed.full_content) {
                // 实时更新内容
                content = parsed.full_content;
                updatedItem.content = content;
                
                // 实时更新叶子节点数据以触发重新渲染
                setLeafItems(prevItems => {
                  const newItems = [...prevItems];
                  const index = newItems.findIndex(i => i.id === item.id);
                  if (index !== -1) {
                    newItems[index] = { ...updatedItem };
                  }
                  return newItems;
                });
              } else if (parsed.status === 'completed' && parsed.content) {
                content = parsed.content;
                updatedItem.content = content;
              } else if (parsed.status === 'error') {
                throw new Error(parsed.message);
              }
            } catch (e) {
              // 忽略JSON解析错误
            }
          }
        }
      }

      return updatedItem;
    } catch (error) {
      setProgress(prev => ({
        ...prev,
        failed: [...prev.failed, item.title]
      }));
      throw error;
    } finally {
      // 从正在生成的集合中移除当前项目
      setProgress(prev => {
        const newGenerating = new Set(Array.from(prev.generating));
        newGenerating.delete(item.id);
        return {
          ...prev,
          generating: newGenerating
        };
      });
    }
  };

  // 开始生成所有内容
  const handleGenerateContent = async () => {
    if (!outlineData || leafItems.length === 0) return;

    setIsGenerating(true);
    setProgress({
      total: leafItems.length,
      completed: 0,
      current: '',
      failed: [],
      generating: new Set<string>()
    });

    try {
      // 使用5个并发线程生成内容
      const concurrency = 5;
      const updatedItems = [...leafItems];
      
      for (let i = 0; i < leafItems.length; i += concurrency) {
        const batch = leafItems.slice(i, i + concurrency);
        const promises = batch.map(item => 
          generateItemContent(item, outlineData.project_overview || '')
            .then(updatedItem => {
              const index = updatedItems.findIndex(ui => ui.id === updatedItem.id);
              if (index !== -1) {
                updatedItems[index] = updatedItem;
              }
              setProgress(prev => ({ ...prev, completed: prev.completed + 1 }));
              return updatedItem;
            })
            .catch(error => {
              console.error(`生成内容失败 ${item.title}:`, error);
              setProgress(prev => ({ ...prev, completed: prev.completed + 1 }));
              return item; // 返回原始项目
            })
        );

        await Promise.all(promises);
      }

      // 更新状态
      setLeafItems(updatedItems);
      
      // 这里需要更新整个outlineData，但由于我们只有props，需要通过回调通知父组件
      // 暂时只更新本地状态
      
    } catch (error) {
      console.error('生成内容时出错:', error);
    } finally {
      setIsGenerating(false);
      setProgress(prev => ({ ...prev, current: '', generating: new Set<string>() }));
    }
  };

  // 获取叶子节点的最新内容（包括生成的内容）
  const getLatestContent = (item: OutlineItem): string => {
    if (!item.children || item.children.length === 0) {
      // 叶子节点，从 leafItems 获取最新内容
      const leafItem = leafItems.find(leaf => leaf.id === item.id);
      return leafItem?.content || item.content || '';
    }
    return item.content || '';
  };

  // 解析Markdown内容为Word段落
  const parseMarkdownToWord = (content: string) => {
    const paragraphs = [];
    const lines = content.split('\n');
    let i = 0;
    
    while (i < lines.length) {
      const line = lines[i].trim();
      
      if (!line) {
        i++;
        continue;
      }
      
      // 处理列表项
      if (line.startsWith('- ') || line.startsWith('* ') || /^\d+\.\s/.test(line)) {
        const listItems = [];
        while (i < lines.length && (lines[i].trim().startsWith('- ') || lines[i].trim().startsWith('* ') || /^\s*\d+\.\s/.test(lines[i]))) {
          const listItem = lines[i].trim().replace(/^[-*]\s|^\d+\.\s/, '');
          if (listItem) {
            listItems.push(listItem);
          }
          i++;
        }
        
        // 为每个列表项创建段落
        listItems.forEach(item => {
          paragraphs.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `• ${item}`,
                  size: 20,
                }),
              ],
              spacing: { after: 100 },
              indent: { left: 360 }, // 缩进
            })
          );
        });
        continue;
      }
      
      // 处理表格（简化处理）
      if (line.includes('|')) {
        const tableRows = [];
        while (i < lines.length && lines[i].trim().includes('|')) {
          const row = lines[i].trim();
          if (row && !row.match(/^\|?[-\s\|]+\|?$/)) { // 跳过分隔行
            const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
            if (cells.length > 0) {
              tableRows.push(cells.join(' | '));
            }
          }
          i++;
        }
        
        // 将表格转换为段落形式
        tableRows.forEach(row => {
          paragraphs.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: row,
                  size: 20,
                }),
              ],
              spacing: { after: 100 },
              indent: { left: 180 },
            })
          );
        });
        continue;
      }
      
      // 处理标题
      if (line.startsWith('#')) {
        const match = line.match(/^#+/);
        const level = match ? match[0].length : 1;
        const text = line.replace(/^#+\s*/, '');
        paragraphs.push(
          new Paragraph({
            children: [
              new TextRun({
                text: text,
                bold: true,
                size: level === 1 ? 24 : level === 2 ? 22 : 20,
              }),
            ],
            spacing: { before: 200, after: 100 },
          })
        );
        i++;
        continue;
      }
      
      // 处理普通段落
      const paragraph = [];
      while (i < lines.length && lines[i].trim() && 
             !lines[i].trim().startsWith('-') && 
             !lines[i].trim().startsWith('*') && 
             !lines[i].trim().includes('|') && 
             !lines[i].trim().startsWith('#')) {
        paragraph.push(lines[i].trim());
        i++;
      }
      
      if (paragraph.length > 0) {
        const text = paragraph.join(' ').replace(/\*\*(.*?)\*\*/g, '$1').replace(/\*(.*?)\*/g, '$1').replace(/`(.*?)`/g, '$1');
        paragraphs.push(
          new Paragraph({
            children: [
              new TextRun({
                text: text,
                size: 20,
              }),
            ],
            spacing: { after: 200 },
          })
        );
      }
    }
    
    return paragraphs;
  };

  // 导出Word文档
  const handleExportWord = async () => {
    if (!outlineData) return;

    try {
      const children = [];
      
      // AI生成声明
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: '内容由AI生成',
              italics: true,
              size: 18,
              color: '666666',
            }),
          ],
          alignment: AlignmentType.CENTER,
          spacing: { after: 600 },
        })
      );
      
      // 文档标题
      children.push(
        new Paragraph({
          children: [
            new TextRun({
              text: outlineData.project_name || '投标技术文件',
              bold: true,
              size: 32,
            }),
          ],
          heading: HeadingLevel.TITLE,
          spacing: { after: 400 },
        })
      );

      // 项目概述
      if (outlineData.project_overview) {
        children.push(
          new Paragraph({
            children: [
              new TextRun({
                text: '项目概述',
                bold: true,
                size: 24,
              }),
            ],
            heading: HeadingLevel.HEADING_1,
            spacing: { before: 200, after: 200 },
          }),
          new Paragraph({
            children: [
              new TextRun({
                text: outlineData.project_overview,
                size: 20,
              }),
            ],
            spacing: { after: 400 },
          })
        );
      }
      
      // 构建文档内容
      const buildWordContent = (items: OutlineItem[], level: number = 1) => {
        items.forEach(item => {
          // 章节标题
          const headingLevel = level === 1 ? HeadingLevel.HEADING_1 : 
                              level === 2 ? HeadingLevel.HEADING_2 : HeadingLevel.HEADING_3;
          
          children.push(
            new Paragraph({
              children: [
                new TextRun({
                  text: `${item.id} ${item.title}`,
                  bold: true,
                  size: level === 1 ? 24 : level === 2 ? 22 : 20,
                }),
              ],
              heading: headingLevel,
              spacing: { before: 300, after: 100 },
            })
          );

          // 移除章节描述（description是给AI的提示，不应出现在最终文档中）

          // 叶子节点内容
          if (!item.children || item.children.length === 0) {
            const content = getLatestContent(item);
            if (content) {
              // 使用改进的Markdown解析器
              const parsedParagraphs = parseMarkdownToWord(content);
              children.push(...parsedParagraphs);
            }
          } else {
            // 递归处理子章节
            buildWordContent(item.children, level + 1);
          }
        });
      };

      buildWordContent(outlineData.outline);

      // 创建 Word 文档
      const doc = new Document({
        sections: [{
          properties: {},
          children: children,
        }],
      });

      // 生成并下载文件
      const buffer = await Packer.toBlob(doc);
      saveAs(buffer, `${outlineData.project_name || '标书文档'}.docx`);
      
    } catch (error) {
      console.error('导出失败:', error);
      alert('导出失败，请重试');
    }
  };

  if (!outlineData) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无内容</h3>
            <p className="mt-1 text-sm text-gray-500">
              请先在"目录编辑"步骤中生成目录结构
            </p>
          </div>
        </div>
      </div>
    );
  }

  const completedItems = leafItems.filter(item => item.content).length;

  return (
    <div className="max-w-6xl mx-auto">
      {/* 顶部工具栏 */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">标书内容</h2>
              <p className="text-sm text-gray-500 mt-1">
                共 {leafItems.length} 个章节，已生成 {completedItems} 个
                {progress.failed.length > 0 && (
                  <span className="text-red-500 ml-2">失败 {progress.failed.length} 个</span>
                )}
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handleGenerateContent}
                disabled={isGenerating}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PlayIcon className="w-4 h-4 mr-2" />
                {isGenerating ? '生成中...' : '生成标书'}
              </button>
              
              <button
                onClick={handleExportWord}
                disabled={isGenerating}
                className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <DocumentArrowDownIcon className="w-4 h-4 mr-2" />
                导出Word
              </button>
            </div>
          </div>
          
          {/* 进度条 */}
          {isGenerating && (
            <div className="mt-4">
              <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
                <span>正在生成: {progress.current}</span>
                <span>{progress.completed} / {progress.total}</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(progress.completed / progress.total) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 文档内容 */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-8">
          <div className="prose max-w-none">
            {/* 文档标题 */}
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
              {outlineData.project_name || '投标技术文件'}
            </h1>
            
            {/* 项目概述 */}
            {outlineData.project_overview && (
              <div className="bg-blue-50 border-l-4 border-blue-400 p-6 mb-8">
                <h2 className="text-lg font-semibold text-blue-900 mb-2">项目概述</h2>
                <p className="text-blue-800">{outlineData.project_overview}</p>
              </div>
            )}

            {/* 目录结构和内容 */}
            <div className="space-y-8">
              {renderOutline(outlineData.outline)}
            </div>
          </div>
        </div>
      </div>

      {/* 底部统计 */}
      <div className="mt-6 bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <CheckCircleIcon className="w-4 h-4 text-green-500 mr-1" />
              <span>已完成: {completedItems}</span>
            </div>
            <div className="flex items-center">
              <DocumentTextIcon className="w-4 h-4 text-gray-400 mr-1" />
              <span>待生成: {leafItems.length - completedItems}</span>
            </div>
            {progress.failed.length > 0 && (
              <div className="flex items-center">
                <ExclamationCircleIcon className="w-4 h-4 text-red-500 mr-1" />
                <span className="text-red-600">失败: {progress.failed.length}</span>
              </div>
            )}
          </div>
          <div>
            <span>总字数: {leafItems.reduce((sum, item) => sum + (item.content?.length || 0), 0)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContentEdit;