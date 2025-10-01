import { useState } from 'react';
import { LandingScreen } from './components/LandingScreen';
import { ProcessingScreen } from './components/ProcessingScreen';
import { MindmapScreen } from './components/MindmapScreen';
import { generateMindmapFromFile } from './utils/mockMindmapGenerator';
import { ThemeProvider } from './contexts/ThemeContext';
import { LanguageProvider } from './contexts/LanguageContext';

type AppState = 'landing' | 'processing' | 'mindmap';

export default function App() {
  const [currentState, setCurrentState] = useState<AppState>('landing');
  const [mindmapData, setMindmapData] = useState(null);

  const handleFileUpload = async (file: File) => {
    setCurrentState('processing');

    try {
      // Read the file as text (for .json or .txt files)
      const docText = await file.text();

      // Send POST request to backend API
      const response = await fetch('/generate-mindmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document: docText, lang: 'en', max_depth: 3 }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const mindmapData = await response.json();
      setMindmapData(mindmapData);
      setCurrentState('mindmap');
    } catch (error) {
      console.error('Error generating mindmap:', error);
      setCurrentState('landing');
    }
  };

  const handleBackToLanding = () => {
    setCurrentState('landing');
    setMindmapData(null);
  };

  return (
    <ThemeProvider>
      <LanguageProvider>
        <div className="size-full">
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
        </div>
      </LanguageProvider>
    </ThemeProvider>
  );
}
