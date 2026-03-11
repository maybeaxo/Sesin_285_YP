import { useMemo } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import GameCard from './GameCard'
import './GameList.css'

function GameList({ games, searchQuery, selectedGenre, selectedPlatform, selectedAgeRating, selectedDuration, onGameSelect, onQuickSelect }) {
  const { t } = useLanguage()
  const filteredGames = useMemo(() => {
    return games.filter(game => {
      // Скрываем недоступные игры из списка
      if (!game.availability) return false
      
      const matchesSearch = game.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           game.developer.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           game.description.toLowerCase().includes(searchQuery.toLowerCase())
      
      const matchesGenre = selectedGenre === 'Все' || game.genre.includes(selectedGenre)
      
      const matchesPlatform = selectedPlatform === 'Все' || 
                             game.platform.some(p => p === selectedPlatform)
      
      const matchesAgeRating = selectedAgeRating === 'Все' || 
                              game.ageRating === selectedAgeRating
      
      const matchesDuration = (() => {
        if (selectedDuration === 'all') return true
        if (selectedDuration === 'infinite') return game.durationMinutes >= 9999
        if (selectedDuration === '0-60') return game.durationMinutes <= 60
        if (selectedDuration === '60-180') return game.durationMinutes > 60 && game.durationMinutes <= 180
        if (selectedDuration === '180-360') return game.durationMinutes > 180 && game.durationMinutes <= 360
        if (selectedDuration === '360-720') return game.durationMinutes > 360 && game.durationMinutes <= 720
        if (selectedDuration === '720+') return game.durationMinutes > 720 && game.durationMinutes < 9999
        return true
      })()
      
      return matchesSearch && matchesGenre && matchesPlatform && matchesAgeRating && matchesDuration
    })
  }, [games, searchQuery, selectedGenre, selectedPlatform, selectedAgeRating, selectedDuration])

  return (
    <div className="game-list">
      <div className="game-list-header">
        <h2>{t('header.selectVRGames')}</h2>
        <div className="game-list-header-actions">
          {onQuickSelect && (
            <button className="quick-select-btn-inline" onClick={onQuickSelect}>
              ✨ {t('home.quickSelect')}
            </button>
          )}
          <p className="games-count">{t('gameList.availableGames')}: {filteredGames.length}</p>
        </div>
      </div>
      
      {filteredGames.length === 0 ? (
        <div className="no-games">
          <p>{t('gameList.noGamesFound')}</p>
          <p className="no-games-hint">{t('gameList.tryOtherFilters')}</p>
        </div>
      ) : (
        <div className="games-grid">
          {filteredGames.map((game, index) => (
            <GameCard 
              key={game.id} 
              game={game} 
              onClick={() => onGameSelect(game)}
              index={index}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default GameList
