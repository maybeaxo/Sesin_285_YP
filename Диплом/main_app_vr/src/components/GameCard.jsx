import { useLanguage } from '../contexts/LanguageContext'
import { getTranslatedGame } from '../utils/gameTranslations'
import './GameCard.css'

function GameCard({ game, onClick, index = 0 }) {
  const { t, language } = useLanguage()
  const translatedGame = getTranslatedGame(game, t, language)
  const getRatingColor = (rating) => {
    if (rating >= 9) return '#4caf50'
    if (rating >= 8) return '#8bc34a'
    if (rating >= 7) return '#ffc107'
    return '#ff9800'
  }

  return (
    <div 
      className="game-card" 
      onClick={onClick}
      style={{ animationDelay: `${index * 0.05}s` }}
    >
      <div className="game-card-image-container">
        <img 
          src={game.screenshots[0]} 
          alt={translatedGame.title}
          className="game-card-image"
        />
        <div className="game-card-rating" style={{ backgroundColor: getRatingColor(game.rating) }}>
          {game.rating}
        </div>
      </div>
      
      <div className="game-card-content">
        <h3 className="game-card-title">{translatedGame.title}</h3>
        <p className="game-card-developer">{game.developer}</p>
        
        <div className="game-card-info-row">
          <span className="game-card-players">{translatedGame.players}</span>
          <span className="game-card-duration">{translatedGame.duration}</span>
        </div>
        
        <div className="game-card-genres">
          {translatedGame.genre.slice(0, 3).map((g, idx) => (
            <span key={idx} className="genre-tag">{g}</span>
          ))}
        </div>
        
        <div className="game-card-platforms">
          {translatedGame.platform.map((p, idx) => (
            <span key={idx} className="platform-tag">{p}</span>
          ))}
        </div>
        
        <div className="game-card-footer">
          <button className="game-card-button">
            {t('home.selectGame')} →
          </button>
        </div>
      </div>
    </div>
  )
}

export default GameCard
