import { createContext, useContext, useState, useEffect } from 'react'
import ruTranslations from '../i18n/ru.json'
import enTranslations from '../i18n/en.json'
import ruGamesTranslations from '../i18n/games.ru.json'
import enGamesTranslations from '../i18n/games.en.json'

const LanguageContext = createContext()

const translations = {
  ru: { ...ruTranslations, ...ruGamesTranslations },
  en: { ...enTranslations, ...enGamesTranslations }
}

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState(() => {
    const saved = localStorage.getItem('app_language')
    return saved || 'ru'
  })

  useEffect(() => {
    localStorage.setItem('app_language', language)
  }, [language])

  const t = (key) => {
    try {
      const keys = key.split('.')
      let value = translations[language]
      
      if (!value) {
        return key
      }
      
      for (const k of keys) {
        if (value === null || value === undefined) {
          return key
        }
        value = value[k]
      }
      
      // Если значение не найдено, возвращаем ключ
      if (value === undefined || value === null) {
        return key
      }
      
      return value
    } catch (error) {
      return key
    }
  }

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'ru' ? 'en' : 'ru')
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage() {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within LanguageProvider')
  }
  return context
}

