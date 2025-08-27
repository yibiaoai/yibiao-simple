/**
 * 配置面板组件
 */
import React, { useState, useEffect } from 'react';
import { ConfigData } from '../types';
import { configApi } from '../services/api';

interface ConfigPanelProps {
  config: ConfigData;
  onConfigChange: (config: ConfigData) => void;
}

const ConfigPanel: React.FC<ConfigPanelProps> = ({ config, onConfigChange }) => {
  const [localConfig, setLocalConfig] = useState<ConfigData>(config);
  const [models, setModels] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await configApi.loadConfig();
      if (response.data) {
        setLocalConfig(response.data);
        onConfigChange(response.data);
      }
    } catch (error) {
      console.error('加载配置失败:', error);
    }
  };

  const handleSave = async () => {
    try {
      setLoading(true);
      const response = await configApi.saveConfig(localConfig);
      
      if (response.data.success) {
        onConfigChange(localConfig);
        setMessage({ type: 'success', text: '配置保存成功！' });
        setTimeout(() => setMessage(null), 3000);
      } else {
        setMessage({ type: 'error', text: response.data.message || '配置保存失败' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '配置保存失败' });
    } finally {
      setLoading(false);
    }
  };

  const handleGetModels = async () => {
    if (!localConfig.api_key) {
      setMessage({ type: 'error', text: '请先输入API Key' });
      return;
    }

    try {
      setLoading(true);
      const response = await configApi.getModels(localConfig);
      
      if (response.data.success) {
        setModels(response.data.models);
        setMessage({ type: 'success', text: `获取到 ${response.data.models.length} 个模型` });
        setTimeout(() => setMessage(null), 3000);
      } else {
        setMessage({ type: 'error', text: response.data.message });
      }
    } catch (error) {
      setMessage({ type: 'error', text: '获取模型列表失败' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white shadow-sm border-r border-gray-200 w-80 p-6 overflow-y-auto">
      <div className="space-y-6">
        {/* 标题 */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI写标书助手</h1>
          <hr className="mt-4 border-gray-200" />
        </div>

        {/* 基本配置 */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">⚙️ 基本配置</h2>
          
          <div className="space-y-4">
            <div>
              <label htmlFor="api_key" className="block text-sm font-medium text-gray-700">
                OpenAI API Key
              </label>
              <input
                type="password"
                id="api_key"
                value={localConfig.api_key}
                onChange={(e) => setLocalConfig({ ...localConfig, api_key: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="输入你的OpenAI API密钥"
              />
            </div>

            <div>
              <label htmlFor="base_url" className="block text-sm font-medium text-gray-700">
                Base URL (可选)
              </label>
              <input
                type="text"
                id="base_url"
                value={localConfig.base_url || ''}
                onChange={(e) => setLocalConfig({ ...localConfig, base_url: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="如果使用代理或其他服务，请输入base URL"
              />
            </div>
          </div>
        </div>

        {/* 模型配置 */}
        <div>
          <h3 className="text-base font-medium text-gray-900 mb-3">🤖 模型配置</h3>
          
          <button
            onClick={handleGetModels}
            disabled={loading}
            className="w-full mb-3 inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:bg-gray-400"
          >
            {loading ? '获取中...' : '🔄 获取可用模型'}
          </button>

          <div>
            <label htmlFor="model_name" className="block text-sm font-medium text-gray-700">
              模型名称
            </label>
            {models.length > 0 ? (
              <select
                id="model_name"
                value={localConfig.model_name}
                onChange={(e) => setLocalConfig({ ...localConfig, model_name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
              >
                {models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            ) : (
              <input
                type="text"
                id="model_name"
                value={localConfig.model_name}
                onChange={(e) => setLocalConfig({ ...localConfig, model_name: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                placeholder="输入要使用的模型名称"
              />
            )}
          </div>
        </div>

        {/* 保存按钮 */}
        <button
          onClick={handleSave}
          disabled={loading}
          className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:bg-gray-400"
        >
          {loading ? '保存中...' : '💾 保存配置'}
        </button>

        {/* 消息提示 */}
        {message && (
          <div className={`p-3 rounded-md text-sm ${
            message.type === 'success' 
              ? 'bg-green-100 text-green-700 border border-green-200' 
              : 'bg-red-100 text-red-700 border border-red-200'
          }`}>
            {message.text}
          </div>
        )}

        {/* 使用说明 */}
        <div className="border-t border-gray-200 pt-4">
          <h3 className="text-sm font-medium text-gray-900 mb-2">📋 使用说明</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <p>1. 配置API密钥和Base URL</p>
            <p>2. 选择或输入模型名称</p>
            <p>3. 按步骤完成标书编写流程</p>
          </div>
        </div>

        {/* 底部图标链接 */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex items-center justify-center space-x-4">
            {/* GitHub图标 */}
            <a
              href="https://github.com/yibiaoai/yibiao-simple"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-gray-700 transition-colors"
              title="GitHub"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.30.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
            </a>
            
            {/* 易标图标 */}
            <a
              href="https://yibiao.pro"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:opacity-75 transition-opacity"
              title="易标官网"
            >
              <img 
                src="/yibiao.png" 
                alt="易标" 
                className="w-6 h-6" 
                onError={(e) => {
                  console.log('易标logo加载失败');
                  e.currentTarget.style.display = 'none';
                }}
              />
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConfigPanel;