import { useState, useRef } from 'react';
import { motion } from 'motion/react';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';
import { Button } from './ui/button';
import { MindmapNode } from './MindmapNode';
import { useLanguage } from '../contexts/LanguageContext';
import { ThemeLanguageToggle } from './ThemeLanguageToggle';

interface MindmapData {
  id: string;
  title: string;
  description?: string;
  children?: MindmapData[];
  color: string;
  x: number;
  y: number;
}

interface MindmapScreenProps {
  mindmapData: MindmapData;
  onBack: () => void;
}

export function MindmapScreen({ mindmapData, onBack }: MindmapScreenProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set([mindmapData.id]));
  const containerRef = useRef<HTMLDivElement>(null);
  const { t } = useLanguage();

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));
  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const toggleNode = (nodeId: string) => {
    setExpandedNodes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(nodeId)) {
        newSet.delete(nodeId);
      } else {
        newSet.add(nodeId);
      }
      return newSet;
    });
  };

  const handleExportJSON = () => {
    const dataStr = JSON.stringify(mindmapData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'mindmap.json';
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleExportImage = () => {
    // Mock image export - in a real app, you'd capture the canvas/SVG
    alert('Image export functionality would be implemented here');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-900 dark:to-blue-900 flex flex-col">
      {/* Header */}
      <div className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm border-b border-slate-200 dark:border-slate-700 p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            <Button 
              variant="outline" 
              onClick={onBack}
              className="rounded-xl"
            >
              {t('back')}
            </Button>
            <h1 className="text-xl text-slate-800 dark:text-slate-100">{t('appName')}</h1>
          </div>

          {/* Controls */}
          <div className="flex items-center space-x-4">
            {/* Zoom Controls */}
            <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              className="rounded-lg"
            >
              <ZoomOut className="w-4 h-4" />
            </Button>
              <span className="text-sm text-slate-600 dark:text-slate-400 min-w-12 text-center">
                {Math.round(zoom * 100)}%
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleZoomIn}
                className="rounded-lg"
              >
                <ZoomIn className="w-4 h-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleReset}
                className="rounded-lg"
              >
                <RotateCcw className="w-4 h-4" />
              </Button>
            </div>
            
            {/* Theme and Language Toggle */}
            <ThemeLanguageToggle />
          </div>
        </div>
      </div>

      {/* Mindmap Area */}
      <div className="flex-1 relative overflow-hidden">
        <motion.div
          ref={containerRef}
          className="w-full h-full relative"
          style={{
            transform: `scale(${zoom}) translate(${pan.x}px, ${pan.y}px)`,
          }}
          transition={{ type: "tween", duration: 0.2 }}
        >
          {/* Grid background */}
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `
                radial-gradient(circle, #e2e8f0 1px, transparent 1px)
              `,
              backgroundSize: '40px 40px'
            }}
          />
          
          {/* Mindmap nodes */}
          <MindmapNode
            node={mindmapData}
            onToggle={toggleNode}
            isExpanded={expandedNodes.has(mindmapData.id)}
            level={0}
          />
        </motion.div>
      </div>

      {/* Action Bar */}
      <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-sm border-t border-slate-200 dark:border-slate-700 p-6">
        <div className="flex items-center justify-center space-x-4">
          <Button
            onClick={handleExportJSON}
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
          >
            {t('exportJSON')}
          </Button>
          <Button
            onClick={handleExportImage}
            className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white px-6 py-2 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105"
          >
            {t('downloadImage')}
          </Button>
          <Button
            onClick={onBack}
            variant="outline"
            className="px-6 py-2 rounded-xl border-2 hover:bg-slate-50 dark:hover:bg-slate-800 transition-all duration-300"
          >
            {t('generateAnother')}
          </Button>
        </div>
      </div>
    </div>
  );
}