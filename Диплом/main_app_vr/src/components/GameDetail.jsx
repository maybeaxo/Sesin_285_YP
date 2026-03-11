import { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { trackGameView } from '../utils/viewTracker'
import { getTranslatedGame } from '../utils/gameTranslations'
import './GameDetail.css'

function GameDetail({ game, onBack }) {
  const { t, language } = useLanguage()
  const translatedGame = getTranslatedGame(game, t, language)
  
  useEffect(() => {
    if (game?.id) {
      trackGameView(game.id)
    }
  }, [game?.id])
  const [currentScreenshotIndex, setCurrentScreenshotIndex] = useState(0)
  const [isAutoPlay, setIsAutoPlay] = useState(true)
  const [showVideo, setShowVideo] = useState(false)

  const screenshots = game.screenshots || []

  useEffect(() => {
    if (!isAutoPlay || screenshots.length <= 1) return

    const interval = setInterval(() => {
      setCurrentScreenshotIndex((prev) => (prev + 1) % screenshots.length)
    }, 4000)

    return () => clearInterval(interval)
  }, [isAutoPlay, screenshots.length])

  const handleScreenshotClick = (index) => {
    setCurrentScreenshotIndex(index)
    setIsAutoPlay(false)
    setTimeout(() => setIsAutoPlay(true), 10000)
  }

  const goToNext = () => {
    setCurrentScreenshotIndex((prev) => (prev + 1) % screenshots.length)
    setIsAutoPlay(false)
    setTimeout(() => setIsAutoPlay(true), 10000)
  }

  const goToPrev = () => {
    setCurrentScreenshotIndex((prev) => (prev - 1 + screenshots.length) % screenshots.length)
    setIsAutoPlay(false)
    setTimeout(() => setIsAutoPlay(true), 10000)
  }

  return (
    <div className="game-detail">
      <div className="game-detail-container">
        <div className="game-detail-layout">
          {/* Левая часть - Скриншоты/Видео */}
          <div className="game-detail-screenshots-section">
            <button className="detail-back-button" onClick={onBack}>
              ← {t('gameDetail.back')}
            </button>

            <div className="screenshot-viewer">
              <div className="screenshot-main">
                {showVideo && game.video ? (
                  <div className="video-container">
                    <iframe
                      src={game.video}
                      title={translatedGame.title}
                      frameBorder="0"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      className="game-video"
                    />
                    <button 
                      className="video-close-button"
                      onClick={() => setShowVideo(false)}
                    >
                      ×
                    </button>
                  </div>
                ) : (
                  <>
                    <img 
                      src={screenshots[currentScreenshotIndex]} 
                      alt={`${translatedGame.title} - ${t('gameDetail.screenshots')} ${currentScreenshotIndex + 1}`}
                      className="screenshot-main-image"
                    />
                    
                    {game.video && (
                      <button 
                        className="video-play-button"
                        onClick={() => setShowVideo(true)}
                        aria-label="Воспроизвести видео"
                      >
                        ▶
                      </button>
                    )}
                  </>
                )}
                
                {/* Навигация поверх изображения */}
                {!showVideo && (
                  <>
                    <div className="screenshot-navigation">
                      <button 
                        className="screenshot-nav-button prev"
                        onClick={goToPrev}
                        aria-label="Предыдущий скриншот"
                      >
                        ←
                      </button>
                      <button 
                        className="screenshot-nav-button next"
                        onClick={goToNext}
                        aria-label="Следующий скриншот"
                      >
                        →
                      </button>
                    </div>

                    {/* Индикаторы скриншотов */}
                    <div className="screenshot-indicators">
                      {screenshots.map((_, index) => (
                        <button
                          key={index}
                          className={`screenshot-indicator ${index === currentScreenshotIndex ? 'active' : ''}`}
                          onClick={() => handleScreenshotClick(index)}
                          aria-label={`Скриншот ${index + 1}`}
                        />
                      ))}
                    </div>

                    {/* Счетчик скриншотов */}
                    <div className="screenshot-counter">
                      {currentScreenshotIndex + 1} / {screenshots.length}
                    </div>
                  </>
                )}

                {/* Рейтинг */}
                <div className="game-detail-rating">
                  <span className="rating-value">{game.rating}</span>
                  <span className="rating-label">{t('gameDetail.rating')}</span>
                </div>

                {/* Наличие на арене */}
                <div className={`game-availability ${game.availability ? 'available' : 'unavailable'}`}>
                  {game.availability ? `✓ ${t('gameDetail.available')}` : `✗ ${t('gameDetail.unavailable')}`}
                </div>
              </div>

              {/* Миниатюры скриншотов */}
              {!showVideo && (
                <div className="screenshot-thumbnails">
                  {screenshots.map((screenshot, index) => (
                    <div
                      key={index}
                      className={`screenshot-thumbnail ${index === currentScreenshotIndex ? 'active' : ''}`}
                      onClick={() => handleScreenshotClick(index)}
                    >
                      <img 
                        src={screenshot} 
                        alt={`Миниатюра ${index + 1}`}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Правая часть - Описание */}
          <div className="game-detail-info-section">
            <div className="game-detail-header">
              <h1 className="game-detail-title">{translatedGame.title}</h1>
              <p className="game-detail-developer">{game.developer}</p>
            </div>

            <div className="game-detail-description">
              <h2>{t('gameDetail.description')}</h2>
              <p>{translatedGame.description}</p>
            </div>

            <div className="game-detail-info-grid">
              <div className="info-item">
                <h3>{t('gameDetail.players')}</h3>
                <p className="players-info">{translatedGame.players}</p>
              </div>

              <div className="info-item">
                <h3>{t('gameDetail.genres')}</h3>
                <div className="info-tags">
                  {translatedGame.genre.map((g, idx) => (
                    <span key={idx} className="info-tag genre">{g}</span>
                  ))}
                </div>
              </div>
              
              <div className="info-item">
                <h3>{t('gameDetail.platforms')}</h3>
                <div className="info-tags">
                  {translatedGame.platform.map((p, idx) => (
                    <span key={idx} className="info-tag platform">{p}</span>
                  ))}
                </div>
              </div>
              
              <div className="info-item">
                <h3>{t('gameDetail.releaseDate')}</h3>
                <p>{new Date(game.releaseDate).toLocaleDateString(language === 'ru' ? 'ru-RU' : 'en-US')}</p>
              </div>
              
              <div className="info-item">
                <h3>{t('gameDetail.duration')}</h3>
                <p>{translatedGame.duration}</p>
              </div>
              
              <div className="info-item">
                <h3>{t('gameDetail.ageRating')}</h3>
                <p className="age-rating">{game.ageRating}</p>
              </div>
              
              <div className="info-item">
                <h3>{t('gameDetail.languages')}</h3>
                <p>{translatedGame.languages.join(', ')}</p>
              </div>

              <div className="info-item">
                <h3>{t('gameDetail.availability')}</h3>
                <p className={`availability-status ${game.availability ? 'available' : 'unavailable'}`}>
                  {game.availability ? `✓ ${t('gameDetail.available')}` : `✗ ${t('gameDetail.unavailable')}`}
                </p>
              </div>
            </div>

            <div className="game-detail-features">
              <h2>{t('gameDetail.features')}</h2>
              <ul>
                {translatedGame.features.map((feature, idx) => (
                  <li key={idx}>{feature}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default GameDetail
