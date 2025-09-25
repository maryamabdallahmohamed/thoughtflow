import { Moon, Sun, Globe } from 'lucide-react';
import { Button } from './ui/button';
import { useTheme } from '../contexts/ThemeContext';
import { useLanguage } from '../contexts/LanguageContext';

export function ThemeLanguageToggle() {
  const { theme, toggleTheme } = useTheme();
  const { language, toggleLanguage } = useLanguage();

  return (
    <div className="flex items-center space-x-2">
      {/* Language Toggle */}
      <Button
        variant="outline"
        size="sm"
        onClick={toggleLanguage}
        className="rounded-lg hover:bg-accent"
      >
        <Globe className="w-4 h-4 mr-1" />
        <span className="text-sm">{language === 'en' ? 'العربية' : 'English'}</span>
      </Button>

      {/* Theme Toggle */}
      <Button
        variant="outline"
        size="sm"
        onClick={toggleTheme}
        className="rounded-lg hover:bg-accent"
      >
        {theme === 'light' ? (
          <Moon className="w-4 h-4" />
        ) : (
          <Sun className="w-4 h-4" />
        )}
      </Button>
    </div>
  );
}