import { genres, platforms, ageRatings, durationFilters } from '../data/games'
import { useLanguage } from '../contexts/LanguageContext'
import { getTranslatedGenre, getTranslatedPlatform, getTranslatedDurationFilter } from '../utils/gameTranslations'
import './Header.css'

function Header({ 
  searchQuery, 
  setSearchQuery, 
  selectedGenre, 
  setSelectedGenre,
  selectedPlatform,
  setSelectedPlatform,
  selectedAgeRating,
  setSelectedAgeRating,
  selectedDuration,
  setSelectedDuration,
  onBack,
  currentScreen,
  onAdminClick
}) {
  const { t, language, toggleLanguage } = useLanguage()
  
  return (
    <header className="header">
      <div className="header-background"></div>
      <div className="header-content">
        <div className="header-left">
          {onBack && (
            <button className="back-button" onClick={onBack}>
              <span className="back-icon">←</span>
              <span>{t('header.backToHome')}</span>
            </button>
          )}
          <div className="header-title-section">
            <h1 className="header-title">WARPOINT</h1>
            <p className="header-subtitle">{t('header.selectVRGames')}</p>
          </div>
        </div>
        
        {currentScreen === 'games' && (
          <div className="header-filters">
            <div className="header-language-toggle">
              <button 
                className="language-toggle-btn" 
                onClick={toggleLanguage}
                title={language === 'ru' ? 'Switch to English' : 'Переключить на русский'}
              >
                {language === 'ru' ? 'EN' : 'RU'}
              </button>
            </div>
            
            <div className="search-container">
              <div className="search-icon">🔍</div>
              <input
                type="text"
                className="search-input"
                placeholder={t('header.searchGames')}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <div className="filter-container">
              <div className="filter-wrapper">
                <label className="filter-label">{t('header.genre')}</label>
                <select
                  className="filter-select"
                  value={selectedGenre}
                  onChange={(e) => setSelectedGenre(e.target.value)}
                >
                  {genres.map(genre => (
                    <option key={genre} value={genre}>{getTranslatedGenre(genre, t)}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter-wrapper">
                <label className="filter-label">{t('header.platform')}</label>
                <select
                  className="filter-select"
                  value={selectedPlatform}
                  onChange={(e) => setSelectedPlatform(e.target.value)}
                >
                  {platforms.map(platform => (
                    <option key={platform} value={platform}>{getTranslatedPlatform(platform, t)}</option>
                  ))}
                </select>
              </div>

              <div className="filter-wrapper">
                <label className="filter-label">{t('header.age')}</label>
                <select
                  className="filter-select"
                  value={selectedAgeRating}
                  onChange={(e) => setSelectedAgeRating(e.target.value)}
                >
                  {ageRatings.map(rating => (
                    <option key={rating} value={rating}>{rating}</option>
                  ))}
                </select>
              </div>

              <div className="filter-wrapper">
                <label className="filter-label">{t('header.duration')}</label>
                <select
                  className="filter-select"
                  value={selectedDuration}
                  onChange={(e) => setSelectedDuration(e.target.value)}
                >
                  {durationFilters.map(duration => (
                    <option key={duration.value} value={duration.value}>{getTranslatedDurationFilter(duration, t)}</option>
                  ))}
                </select>
              </div>
            </div>
            
            {onAdminClick && (
              <button className="header-admin-button" onClick={onAdminClick} aria-label="Настройки">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 15a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>
                  <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/>
                </svg>
              </button>
            )}
          </div>
        )}
      </div>
    </header>
  )
}

export default Header
