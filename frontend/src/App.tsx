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
      // Create FormData to send the file
      const formData = new FormData();
      formData.append('file', file);

      // Send POST request to backend API
      const response = await fetch('http://localhost:8000/mindmap/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setMindmapData(data);
      setCurrentState('mindmap');
    } catch (error) {
      console.error('Error generating mindmap:', error);
      // In a real app, you'd show an error state here
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
