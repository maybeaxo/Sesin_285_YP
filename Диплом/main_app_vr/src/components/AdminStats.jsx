import { useMemo } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { getViewStats, getTotalViews, getMostViewedGames } from '../utils/viewTracker'
import { getTranslatedGame } from '../utils/gameTranslations'
import './AdminStats.css'

function AdminStats({ games }) {
  const { t, language } = useLanguage()
  const stats = getViewStats()
  const totalViews = getTotalViews()
  const mostViewed = useMemo(() => getMostViewedGames(games, 10), [games])
  const averageRating = useMemo(() => {
    if (games.length === 0) return 0
    const sum = games.reduce((acc, game) => acc + game.rating, 0)
    return (sum / games.length).toFixed(1)
  }, [games])

  return (
    <div className="admin-stats">
      <div className="admin-stats-header">
        <h2>{t('admin.stats')}</h2>
      </div>

      <div className="admin-stats-overview">
        <div className="stat-card">
          <div className="stat-value">{totalViews}</div>
          <div className="stat-label">{t('admin.totalViews')}</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{games.length}</div>
          <div className="stat-label">{t('admin.gameList')}</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{averageRating}</div>
          <div className="stat-label">{t('admin.averageRating')}</div>
        </div>
      </div>

      <div className="admin-stats-section">
        <h3>{t('admin.mostViewed')}</h3>
        <div className="stats-games-list">
          {mostViewed.length > 0 ? (
            mostViewed.map((game, index) => {
              const views = stats[game.id]?.views || 0
              const translatedGame = getTranslatedGame(game, t, language)
              return (
                <div key={game.id} className="stats-game-item">
                  <div className="stats-game-rank">#{index + 1}</div>
                  <img src={game.image} alt={translatedGame.title} className="stats-game-image" />
                  <div className="stats-game-info">
                    <div className="stats-game-title">{translatedGame.title}</div>
                    <div className="stats-game-meta">
                      <span className="stats-game-rating">⭐ {game.rating}</span>
                      <span className="stats-game-views">
                        👁️ {views} {t('admin.views')}
                      </span>
                    </div>
                  </div>
                </div>
              )
            })
          ) : (
            <div className="stats-empty">
              <p>{t('admin.noStats')}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminStats

