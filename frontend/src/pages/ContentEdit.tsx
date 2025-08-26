/**
 * 内容编辑页面
 */
import React, { useState, useEffect } from 'react';
import { OutlineData, OutlineItem } from '../types';
import { DocumentTextIcon, ChevronRightIcon } from '@heroicons/react/24/outline';

interface ContentEditProps {
  outlineData: OutlineData | null;
  selectedChapter: string;
  onChapterSelect: (chapterId: string) => void;
}

const ContentEdit: React.FC<ContentEditProps> = ({
  outlineData,
  selectedChapter,
  onChapterSelect,
}) => {
  const [leafItems, setLeafItems] = useState<OutlineItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<OutlineItem | null>(null);

  useEffect(() => {
    if (outlineData) {
      // 收集所有叶子节点（没有children的节点）
      const collectLeafItems = (items: OutlineItem[]): OutlineItem[] => {
        let leaves: OutlineItem[] = [];
        items.forEach(item => {
          if (!item.children || item.children.length === 0) {
            leaves.push(item);
          } else {
            leaves = leaves.concat(collectLeafItems(item.children));
          }
        });
        return leaves;
      };

      const leaves = collectLeafItems(outlineData.outline);
      setLeafItems(leaves);

      // 设置默认选中的章节
      if (selectedChapter) {
        const selected = leaves.find(item => item.id === selectedChapter);
        setSelectedItem(selected || null);
      } else if (leaves.length > 0) {
        setSelectedItem(leaves[0]);
        onChapterSelect(leaves[0].id);
      }
    }
  }, [outlineData, selectedChapter, onChapterSelect]);

  const handleChapterSelect = (item: OutlineItem) => {
    setSelectedItem(item);
    onChapterSelect(item.id);
  };

  if (!outlineData || leafItems.length === 0) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center py-12">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">暂无内容</h3>
            <p className="mt-1 text-sm text-gray-500">
              请先在"目录编辑"步骤中生成目录结构和章节内容
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="flex h-screen max-h-96">
          {/* 左侧章节列表 */}
          <div className="w-1/3 border-r border-gray-200 overflow-y-auto">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">📑 章节列表</h3>
            </div>
            
            <div className="p-2 space-y-1">
              {leafItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleChapterSelect(item)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedItem?.id === item.id
                      ? 'bg-blue-100 text-blue-900 border border-blue-200'
                      : 'hover:bg-gray-50 text-gray-700'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0 mt-1">
                      {item.content ? (
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      ) : (
                        <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-mono text-gray-500">{item.id}</span>
                        {item.content && (
                          <span className="inline-flex items-center px-1.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            已生成
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-medium truncate">{item.title}</p>
                      <p className="text-xs text-gray-500 mt-1 line-clamp-2">{item.description}</p>
                    </div>
                    
                    <ChevronRightIcon className="flex-shrink-0 h-4 w-4 text-gray-400" />
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* 右侧内容编辑区域 */}
          <div className="flex-1 flex flex-col">
            {selectedItem && (
              <>
                {/* 章节标题 */}
                <div className="p-4 border-b border-gray-200 bg-gray-50">
                  <div className="flex items-center space-x-3">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {selectedItem.id}
                    </span>
                    <h2 className="text-lg font-semibold text-gray-900">{selectedItem.title}</h2>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">{selectedItem.description}</p>
                </div>

                {/* 内容编辑区域 */}
                <div className="flex-1 p-4">
                  {selectedItem.content ? (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium text-gray-900">章节内容</h3>
                        <div className="flex items-center space-x-2">
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            内容已生成
                          </span>
                          <span className="text-xs text-gray-500">
                            {selectedItem.content.length} 字符
                          </span>
                        </div>
                      </div>
                      
                      <div className="border rounded-lg">
                        <textarea
                          value={selectedItem.content}
                          onChange={(e) => {
                            // 这里可以添加内容更新逻辑
                            const updatedItem = { ...selectedItem, content: e.target.value };
                            setSelectedItem(updatedItem);
                          }}
                          className="w-full h-80 p-4 border-0 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          placeholder="章节内容..."
                        />
                      </div>
                      
                      <div className="flex justify-end space-x-3">
                        <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                          重新生成
                        </button>
                        <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                          保存修改
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                      <DocumentTextIcon className="h-12 w-12 text-gray-400 mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">暂无内容</h3>
                      <p className="text-sm text-gray-500 mb-6 max-w-sm">
                        该章节还没有生成内容，请在"目录编辑"步骤中点击"生成章节内容"按钮。
                      </p>
                      <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                        生成内容
                      </button>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* 底部统计信息 */}
      <div className="mt-4 bg-white rounded-lg shadow p-4">
        <div className="flex justify-between items-center text-sm text-gray-600">
          <div className="flex space-x-6">
            <span>总章节: {leafItems.length}</span>
            <span>已生成: {leafItems.filter(item => item.content).length}</span>
            <span>待生成: {leafItems.filter(item => !item.content).length}</span>
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