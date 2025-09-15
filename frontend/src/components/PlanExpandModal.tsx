import React, { useState } from 'react';
import { expandApi } from '../services/api';

interface PlanExpandModalProps {
  open: boolean;
  onClose: () => void;
  outlineData: any;
  onUploaded: (data: { aligned_outline?: any; docx_structure?: any; message?: string }) => void;
}

type Mode = 'gpu' | 'cpu' | 'none';

const PlanExpandModal: React.FC<PlanExpandModalProps> = ({ open, onClose, outlineData, onUploaded }) => {
  const [selectedMode] = useState<Mode>('none');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0] || null;
    setFile(f);
  };

  const handleUpload = async () => {
    if (!file) {
      setError('请先选择文件');
      return;
    }
    try {
      setUploading(true);
      setError(null);
      const res = await expandApi.uploadPlanFile(file, outlineData, selectedMode);
      if (res.data?.success) {
        onUploaded({
          aligned_outline: res.data.aligned_outline,
          docx_structure: res.data.docx_structure,
          message: res.data.message,
        });
        onClose();
      } else {
        setError(res.data?.message || '上传失败');
      }
    } catch (e: any) {
      setError(e?.response?.data?.detail || e?.message || '上传失败');
    } finally {
      setUploading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black bg-opacity-30" onClick={onClose} />
      <div className="relative bg-white w-full max-w-2xl rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">方案扩写</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <div className="space-y-4">
          

          <div>
            <h4 className="text-sm font-medium text-gray-800 mb-2">上传方案文档（PDF / Word）</h4>
            <input type="file" accept=".pdf,.docx,.doc" onChange={handleFileChange} />
          </div>

          {error && (
            <div className="text-sm text-red-600">{error}</div>
          )}

          <div className="flex justify-end space-x-3 pt-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm rounded border border-gray-300 text-gray-700 bg-white hover:bg-gray-50"
            >
              取消
            </button>
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="inline-flex items-center px-4 py-2 text-sm rounded text-white bg-green-600 hover:bg-green-700 disabled:bg-gray-400"
            >
              {uploading ? (
                <>
                  <div className="animate-spin -ml-1 mr-2 h-4 w-4 text-white">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  </div>
                  正在上传并解析...
                </>
              ) : (
                '开始扩写'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlanExpandModal;


