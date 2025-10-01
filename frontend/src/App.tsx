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
      // Step 1: Preprocess the file (extract text)
      const formData = new FormData();
      formData.append('file', file);

      const preprocessResponse = await fetch('http://localhost:8000/preprocess/', {
        method: 'POST',
        body: formData,
      });

      if (!preprocessResponse.ok) {
        throw new Error(`Preprocess error! status: ${preprocessResponse.status}`);
      }

      const preprocessData = await preprocessResponse.json();
      const docText = preprocessData.processed_text;

      // Step 2: Generate mindmap from extracted text
      const mindmapResponse = await fetch('http://localhost:8000/generate-mindmap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document: docText, lang: 'en', max_depth: 3 }),
      });

      if (!mindmapResponse.ok) {
        throw new Error(`Mindmap error! status: ${mindmapResponse.status}`);
      }

      const mindmapData = await mindmapResponse.json();
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
