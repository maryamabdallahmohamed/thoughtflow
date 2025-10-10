import { useState } from 'react';
import { LandingScreen } from './components/LandingScreen';
import { ProcessingScreen } from './components/ProcessingScreen';
import { MindmapScreen } from './components/MindmapScreen';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';

type AppState = 'landing' | 'processing' | 'mindmap' | 'error';

// Transform backend format to frontend format
function transformMindmapData(node: any, level = 0): any {
  const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#06b6d4'];
  const color = colors[level % colors.length];

  const transformed: any = {
    id: Math.random().toString(36).substr(2, 9),
    title: node.label || 'Untitled',
    description: node.description || '',
    color: color,
    x: 0,
    y: 0,
    children: []
  };

  // Handle clusters (can be object or array)
  if (node.clusters) {
    const clusters = Array.isArray(node.clusters)
      ? node.clusters
      : Object.values(node.clusters);

    transformed.children = clusters.map((child: any) =>
      transformMindmapData(child, level + 1)
    );
  }

  return transformed;
}

// Calculate tree layout positions
function calculateTreeLayout(node: any, x = 100, y = 300, level = 0): any {
  const HORIZONTAL_SPACING = 250;
  const VERTICAL_SPACING = 100;

  // Set current node position
  node.x = x;
  node.y = y;

  if (node.children && node.children.length > 0) {
    // Calculate total height needed for all children
    const totalHeight = (node.children.length - 1) * VERTICAL_SPACING;
    const startY = y - totalHeight / 2;

    // Position each child
    node.children.forEach((child: any, index: number) => {
      const childY = startY + index * VERTICAL_SPACING;
      calculateTreeLayout(child, x + HORIZONTAL_SPACING, childY, level + 1);
    });
  }

  return node;
}

export default function App() {
  const [currentState, setCurrentState] = useState<AppState>('landing');
  const [mindmapData, setMindmapData] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    console.log('📤 Uploading file:', file.name);
    setCurrentState('processing');
    setErrorMessage(null);

    try {
      // --- Step 1: Upload & Preprocess File ---
      const formData = new FormData();
      formData.append('file', file);

      const preprocessResponse = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!preprocessResponse.ok) {
        throw new Error(`❌ Upload failed: ${preprocessResponse.status}`);
      }

      const uploadData = await preprocessResponse.json();
      const filePath = uploadData.file_path;
      console.log('✅ File uploaded:', filePath);

      // --- Step 2: Generate Mindmap ---
      const mindmapResponse = await fetch('http://localhost:8000/generate_mindmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          file_path: filePath,
        }),
      });

      if (!mindmapResponse.ok) {
        throw new Error(`❌ Mindmap generation failed: ${mindmapResponse.status}`);
      }

      const mindmapData = await mindmapResponse.json();
      console.log('✅ Mindmap generated successfully');
      console.log('📊 Raw mindmap data:', mindmapData);

      // --- Step 3: Transform backend data to frontend format ---
      const transformedData = transformMindmapData(mindmapData.mindmap || mindmapData);
      console.log('🔄 Transformed data:', transformedData);

      // --- Step 3.5: Calculate tree layout positions ---
      const layoutData = calculateTreeLayout(transformedData);
      console.log('📐 Layout calculated:', layoutData);

      // --- Step 4: Show Mindmap Renderer ---
      setMindmapData(layoutData);
      setCurrentState('mindmap');

    } catch (error: any) {
      console.error('💥 Error generating mindmap:', error);
      setErrorMessage(error.message || 'Unexpected error occurred.');
      setCurrentState('error');
    }
  };

  const handleBackToLanding = () => {
    setCurrentState('landing');
    setMindmapData(null);
    setErrorMessage(null);
  };

  return (
    <ThemeProvider>
      <LanguageProvider>
        <div className="w-full h-full">
          {currentState === 'landing' && (
            <LandingScreen onFileUpload={handleFileUpload} />
          )}

          {currentState === 'processing' && (
            <ProcessingScreen />
          )}

          {currentState === 'mindmap' && mindmapData && (
            <MindmapScreen
              mindmapData={mindmapData}
              onBack={handleBackToLanding}
            />
          )}

          {currentState === 'error' && (
            <div className="flex flex-col items-center justify-center h-screen text-center">
              <h2 className="text-2xl font-semibold text-red-500 mb-4">
                Something went wrong 😢
              </h2>
              <p className="text-gray-300 mb-6">{errorMessage}</p>
              <button
                onClick={handleBackToLanding}
                className="bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700 transition"
              >
                Back to Upload
              </button>
            </div>
          )}
        </div>
      </LanguageProvider>
    </ThemeProvider>
  );
}
