import { useEffect, useMemo, useState, useRef } from 'react';
import { motion } from 'motion/react';
import { ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

// Fixed MindmapScreen.tsx
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

// Simple button component
const Button = ({ onClick, children, variant = 'default', size = 'default', className = '' }: any) => {
  const baseClasses = 'px-4 py-2 rounded-lg font-medium transition-all duration-200';
  const variantClasses = variant === 'outline' 
    ? 'border-2 border-slate-300 hover:bg-slate-100 text-slate-700'
    : 'bg-blue-600 hover:bg-blue-700 text-white';
  const sizeClasses = size === 'sm' ? 'px-3 py-1.5 text-sm' : '';
  
  return (
    <button 
      onClick={onClick}
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${className}`}
    >
      {children}
    </button>
  );
};

// MindmapNode component
const MindmapNode = ({ node, level }: { node: MindmapData; level: number }) => {
  const [isHovered, setIsHovered] = useState(false);

  const nodeSize = level === 0 ? 'large' : level === 1 ? 'medium' : 'small';
  const sizeClasses = {
    large: 'px-8 py-4 text-lg min-w-[200px]',
    medium: 'px-6 py-3 text-base min-w-[160px]',
    small: 'px-4 py-2 text-sm min-w-[120px]'
  };

  return (
    <>
      <motion.div
        className="absolute"
        style={{ 
          left: node.x, 
          top: node.y,
        }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, delay: level * 0.1 }}
      >
        <motion.div
          className={`relative rounded-2xl shadow-lg cursor-pointer transition-all duration-300 ${sizeClasses[nodeSize]} border-2`}
          style={{
            backgroundColor: node.color,
            borderColor: isHovered ? '#6366f1' : 'rgba(255,255,255,0.5)'
          }}
          whileHover={{ scale: 1.05 }}
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div className="flex items-center justify-center">
            <span className="text-slate-800 font-semibold text-center">{node.title}</span>
          </div>

          {isHovered && node.description && (
            <motion.div
              className="absolute z-50 bg-slate-800 text-white px-3 py-2 rounded-lg text-sm shadow-xl pointer-events-none"
              style={{ 
                top: '100%', 
                left: '50%', 
                transform: 'translateX(-50%)',
                marginTop: '8px',
                minWidth: '200px',
                maxWidth: '300px',
                whiteSpace: 'normal'
              }}
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {node.description}
              <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-slate-800 rotate-45"></div>
            </motion.div>
          )}
        </motion.div>
      </motion.div>

      {node.children?.map((child) => (
        <MindmapNode key={child.id} node={child} level={level + 1} />
      ))}
    </>
  );
};

export function MindmapScreen({ mindmapData, onBack }: MindmapScreenProps) {
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.2, 3));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.2, 0.5));

  // Calculate layout with proper positioning
  const layoutData = useMemo(() => {
    const nodeWidth = { 0: 200, 1: 160, 2: 120 };
    const nodeHeight = 60;
    const horizontalSpacing = 280;
    const verticalSpacing = 120;

    type NodeWithPosition = MindmapData & { level: number };
    const positioned: NodeWithPosition[] = [];
    const edges: Array<{ from: NodeWithPosition; to: NodeWithPosition }> = [];

    const calculatePositions = (node: MindmapData, level: number, x: number, y: number, parentNode?: NodeWithPosition) => {
      const positionedNode: NodeWithPosition = { ...node, x, y, level };
      positioned.push(positionedNode);

      if (parentNode) {
        edges.push({ from: parentNode, to: positionedNode });
      }

      if (node.children && node.children.length > 0) {
        const childCount = node.children.length;
        const totalHeight = (childCount - 1) * verticalSpacing;
        let currentY = y - totalHeight / 2;

        node.children.forEach((child, index) => {
          calculatePositions(
            child,
            level + 1,
            x + horizontalSpacing,
            currentY,
            positionedNode
          );
          currentY += verticalSpacing;
        });
      }
    };

    calculatePositions(mindmapData, 0, 100, 300);
    
    return { nodes: positioned, edges };
  }, [mindmapData]);

  const fitToView = () => {
    const el = containerRef.current;
    if (!el || layoutData.nodes.length === 0) return;
    
    const rect = el.getBoundingClientRect();
    const padding = 100;

    const xs = layoutData.nodes.map(n => n.x);
    const ys = layoutData.nodes.map(n => n.y);
    const minX = Math.min(...xs) - 100;
    const maxX = Math.max(...xs) + 300;
    const minY = Math.min(...ys) - 50;
    const maxY = Math.max(...ys) + 100;

    const width = maxX - minX;
    const height = maxY - minY;

    const scaleX = (rect.width - padding * 2) / width;
    const scaleY = (rect.height - padding * 2) / height;
    const newZoom = Math.min(scaleX, scaleY, 1.5);

    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;
    
    setPan({
      x: rect.width / 2 - centerX * newZoom,
      y: rect.height / 2 - centerY * newZoom
    });
    setZoom(newZoom);
  };

  useEffect(() => {
    setTimeout(fitToView, 100);
  }, [layoutData]);

  useEffect(() => {
    window.addEventListener('resize', fitToView);
    return () => window.removeEventListener('resize', fitToView);
  }, [layoutData]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex flex-col">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-slate-200 p-4">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            <Button variant="outline" onClick={onBack}>← Back</Button>
            <h1 className="text-xl font-bold text-slate-800">Mind Map</h1>
          </div>

          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={handleZoomOut}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <span className="text-sm text-slate-600 min-w-[60px] text-center">
              {Math.round(zoom * 100)}%
            </span>
            <Button variant="outline" size="sm" onClick={handleZoomIn}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={fitToView}>
              <RotateCcw className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Mindmap Canvas */}
      <div className="flex-1 overflow-hidden relative" ref={containerRef}>
        <div
          className="w-full h-full"
          style={{
            transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
            transformOrigin: '0 0',
            transition: 'transform 0.2s ease-out'
          }}
        >
          {/* Background grid */}
          <div 
            className="absolute inset-0 opacity-10"
            style={{
              backgroundImage: 'radial-gradient(circle, #64748b 1px, transparent 1px)',
              backgroundSize: '40px 40px',
              width: '4000px',
              height: '4000px',
              left: '-2000px',
              top: '-2000px'
            }}
          />

          {/* SVG for edges */}
          <svg className="absolute inset-0 pointer-events-none" style={{ width: '4000px', height: '4000px' }}>
            {layoutData.edges.map((edge, i) => {
              const fromWidth = edge.from.level === 0 ? 200 : edge.from.level === 1 ? 160 : 120;
              const toWidth = edge.to.level === 0 ? 200 : edge.to.level === 1 ? 160 : 120;
              
              const x1 = edge.from.x + fromWidth;
              const y1 = edge.from.y + 30;
              const x2 = edge.to.x;
              const y2 = edge.to.y + 30;
              
              const midX = (x1 + x2) / 2;
              
              return (
                <path
                  key={i}
                  d={`M ${x1} ${y1} C ${midX} ${y1}, ${midX} ${y2}, ${x2} ${y2}`}
                  stroke="#94a3b8"
                  strokeWidth={2}
                  fill="none"
                  opacity={0.4}
                />
              );
            })}
          </svg>

          {/* Render nodes */}
          {layoutData.nodes.map(node => (
            <MindmapNode key={node.id} node={node} level={node.level} />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="bg-white/90 backdrop-blur-sm border-t border-slate-200 p-4">
        <div className="flex justify-center space-x-4">
          <Button onClick={() => {
            const json = JSON.stringify(mindmapData, null, 2);
            const blob = new Blob([json], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'mindmap.json';
            a.click();
            URL.revokeObjectURL(url);
          }}>
            Export JSON
          </Button>
          <Button variant="outline" onClick={onBack}>
            Generate Another
          </Button>
        </div>
      </div>
    </div>
  );
}