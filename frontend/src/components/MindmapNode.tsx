import { useState } from 'react';
import { motion } from 'motion/react';
import { ChevronDown, ChevronRight } from 'lucide-react';

interface MindmapNodeProps {
  node: {
    id: string;
    title: string;
    description?: string;
    children?: MindmapNodeProps['node'][];
    color: string;
    x: number;
    y: number;
  };
  onToggle: (nodeId: string) => void;
  isExpanded: boolean;
  level: number;
}

export function MindmapNode({ node, onToggle, isExpanded, level }: MindmapNodeProps) {
  const [isHovered, setIsHovered] = useState(false);

  const nodeSize = level === 0 ? 'large' : level === 1 ? 'medium' : 'small';
  const sizeClasses = {
    large: 'px-8 py-4 text-lg',
    medium: 'px-6 py-3 text-base',
    small: 'px-4 py-2 text-sm'
  };

  return (
    <motion.div
      className="absolute"
      style={{ left: node.x, top: node.y }}
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.5, delay: level * 0.1 }}
    >
      <motion.div
        className={`
          relative rounded-2xl shadow-lg cursor-pointer transition-all duration-300
          ${sizeClasses[nodeSize]}
          border-2 hover:shadow-xl
        `}
        style={{
          backgroundColor: node.color,
          borderColor: isHovered ? '#6366f1' : 'transparent'
        }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        onClick={() => node.children && onToggle(node.id)}
      >
        <div className="flex items-center space-x-2">
          {node.children && node.children.length > 0 && (
            <motion.div
              animate={{ rotate: isExpanded ? 90 : 0 }}
              transition={{ duration: 0.2 }}
            >
              <ChevronRight className="w-4 h-4 text-slate-600" />
            </motion.div>
          )}
          <span className="text-slate-800 whitespace-nowrap">{node.title}</span>
        </div>

        {/* Tooltip */}
        {isHovered && node.description && (
          <motion.div
            className="absolute z-50 bg-slate-800 dark:bg-slate-700 text-white px-3 py-2 rounded-lg text-sm whitespace-nowrap"
            style={{ top: '100%', left: '50%', transform: 'translateX(-50%)' }}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 10 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {node.description}
            <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-slate-800 dark:bg-slate-700 rotate-45"></div>
          </motion.div>
        )}
      </motion.div>
    </motion.div>
  );
}
