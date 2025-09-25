import { motion } from 'motion/react';
import { useLanguage } from '../contexts/LanguageContext';

export function ProcessingScreen() {
  const { t } = useLanguage();
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-50 dark:from-slate-900 dark:via-blue-900 dark:to-purple-900 flex flex-col items-center justify-center p-8">
      <div className="text-center space-y-8">
        {/* Animated Loader */}
        <div className="relative">
          <motion.div
            className="w-20 h-20 border-4 border-blue-200 rounded-full"
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          >
            <motion.div
              className="absolute inset-0 border-4 border-transparent border-t-blue-600 rounded-full"
              animate={{ rotate: 360 }}
              transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
            />
          </motion.div>
          
          {/* Pulsing center */}
          <motion.div
            className="absolute inset-0 flex items-center justify-center"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <div className="w-3 h-3 bg-purple-600 rounded-full"></div>
          </motion.div>
        </div>

        {/* Processing Text */}
        <motion.div
          className="space-y-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <h2 className="text-2xl text-slate-800 dark:text-slate-100">{t('generating')}</h2>
          <p className="text-slate-600 dark:text-slate-300">
            {t('analyzing')}
          </p>
        </motion.div>

        {/* Floating particles */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-2 h-2 bg-blue-400/30 rounded-full"
              style={{
                left: `${20 + i * 10}%`,
                top: `${30 + i * 8}%`,
              }}
              animate={{
                y: [-10, -30, -10],
                opacity: [0.3, 0.8, 0.3],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: i * 0.5,
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}