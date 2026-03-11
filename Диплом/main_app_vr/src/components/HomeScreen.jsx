import { useEffect, useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import './HomeScreen.css'

function HomeScreen({ onEnter, onQuickSelect }) {
  const { t } = useLanguage()
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth - 0.5) * 20,
        y: (e.clientY / window.innerHeight - 0.5) * 20
      })
    }

    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  return (
    <div className="home-screen">
      <div className="home-background">
        <div className="gradient-orb gradient-orb-1"></div>
        <div className="gradient-orb gradient-orb-2"></div>
        <div className="gradient-orb gradient-orb-3"></div>
        <div 
          className="parallax-layer"
          style={{
            transform: `translate(${mousePosition.x * 0.5}px, ${mousePosition.y * 0.5}px)`
          }}
        ></div>
        <div className="floating-particles">
          {Array.from({ length: 15 }, (_, i) => (
            <div key={i} className={`particle particle-${i + 1}`}></div>
          ))}
        </div>
        <div className="grid-overlay"></div>
      </div>

      <div className="home-content">
        <div className="home-title-wrapper">
          <h1 className="home-title">
            <span className="title-letter">W</span>
            <span className="title-letter">A</span>
            <span className="title-letter">R</span>
            <span className="title-letter">P</span>
            <span className="title-letter">O</span>
            <span className="title-letter">I</span>
            <span className="title-letter">N</span>
            <span className="title-letter">T</span>
          </h1>
          <div className="home-subtitle-line">
            <span className="subtitle-text">{t('home.subtitle')}</span>
            <div className="subtitle-dot"></div>
          </div>
        </div>

        <div className="home-buttons">
          <button className="enter-button" onClick={onEnter}>
            <span className="button-glow"></span>
            <span className="button-text">{t('home.selectGame')}</span>
            <div className="button-arrow">→</div>
          </button>
          
          {onQuickSelect && (
            <button className="quick-select-button" onClick={onQuickSelect}>
              <span className="button-glow"></span>
              <span className="button-text">{t('home.quickSelect')}</span>
              <div className="button-icon">✨</div>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default HomeScreen
