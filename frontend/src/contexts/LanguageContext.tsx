import { createContext, useContext, useState } from 'react';

type Language = 'en' | 'ar';

interface LanguageContextType {
  language: Language;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const translations = {
  en: {
    // Landing Screen
    appName: 'Thoughtify',
    tagline: 'Turn your knowledge into clarity.',
    dragDrop: 'Drop your file here or click to browse',
    uploadDescription: 'Upload JSON or PDF files to generate your mindmap',
    chooseFile: 'Choose File',
    
    // Processing Screen
    generating: 'Generating your mindmap...',
    analyzing: 'Analyzing content and creating connections',
    
    // Mindmap Screen
    back: 'Back',
    exportJSON: 'Export JSON',
    downloadImage: 'Download Image',
    generateAnother: 'Generate Another Mindmap',
    
    // File formats
    json: 'JSON',
    pdf: 'PDF'
  },
  ar: {
    // Landing Screen
    appName: 'ثوتفاي',
    tagline: 'حوّل معرفتك إلى وضوح.',
    dragDrop: 'اسحب ملفك هنا أو اضغط للتصفح',
    uploadDescription: 'ارفع ملفات JSON أو PDF لإنشاء خريطتك الذهنية',
    chooseFile: 'اختر ملف',
    
    // Processing Screen
    generating: 'جاري إنشاء خريطتك الذهنية...',
    analyzing: 'تحليل المحتوى وإنشاء الروابط',
    
    // Mindmap Screen
    back: 'رجوع',
    exportJSON: 'تصدير JSON',
    downloadImage: 'تحميل الصورة',
    generateAnother: 'إنشاء خريطة ذهنية أخرى',
    
    // File formats
    json: 'JSON',
    pdf: 'PDF'
  }
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<Language>('en');

  const toggleLanguage = () => {
    setLanguage(prevLang => prevLang === 'en' ? 'ar' : 'en');
  };

  const t = (key: string): string => {
    return translations[language][key as keyof typeof translations.en] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, toggleLanguage, t }}>
      <div dir={language === 'ar' ? 'rtl' : 'ltr'} className={language === 'ar' ? 'font-arabic' : ''}>
        {children}
      </div>
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}