import { useState } from 'react';
import { Button } from './ui/button';
import { Upload, FileText, FileJson } from 'lucide-react';
import { useLanguage } from '../contexts/LanguageContext';
import { ThemeLanguageToggle } from './ThemeLanguageToggle';

interface LandingScreenProps {
  onFileUpload: (file: File) => void;
}

export function LandingScreen({ onFileUpload }: LandingScreenProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const { t } = useLanguage();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    const validFile = files.find(file => 
      file.type === 'application/pdf' || 
      file.type === 'application/json' ||
      file.name.endsWith('.json')
    );
    if (validFile) {
      onFileUpload(validFile);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900 flex flex-col">
      {/* Header with Controls */}
      <div className="flex justify-end p-6">
        <ThemeLanguageToggle />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="max-w-2xl w-full space-y-12">
          {/* Header */}
          <div className="text-center space-y-4">
            <h1 className="text-4xl text-slate-800 dark:text-slate-100 tracking-tight">{t('appName')}</h1>
            <p className="text-xl text-slate-600 dark:text-slate-300">{t('tagline')}</p>
          </div>

          {/* Upload Area */}
          <div
            className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 cursor-pointer ${
              isDragOver
                ? 'border-blue-400 bg-blue-50/50 dark:bg-blue-900/20 scale-105'
                : 'border-slate-300 dark:border-slate-600 bg-white/60 dark:bg-slate-800/60 hover:border-blue-300 dark:hover:border-blue-400 hover:bg-white/80 dark:hover:bg-slate-800/80'
            } backdrop-blur-sm shadow-lg`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <Upload className="w-12 h-12 text-slate-400 dark:text-slate-500 mx-auto mb-4" />
            <h3 className="text-lg text-slate-700 dark:text-slate-200 mb-2">
              {t('dragDrop')}
            </h3>
            <p className="text-slate-500 dark:text-slate-400 mb-6">
              {t('uploadDescription')}
            </p>
            
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              {t('chooseFile')}
            </Button>
            
            <input
              id="file-input"
              type="file"
              accept=".json,.pdf,application/json,application/pdf"
              onChange={handleFileSelect}
              className="hidden"
            />
          </div>

          {/* Supported Formats */}
          <div className="flex justify-center space-x-8">
            <div className="flex items-center space-x-2 text-slate-600 dark:text-slate-400">
              <FileJson className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <span className="text-sm">{t('json')}</span>
            </div>
            <div className="flex items-center space-x-2 text-slate-600 dark:text-slate-400">
              <FileText className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              <span className="text-sm">{t('pdf')}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}