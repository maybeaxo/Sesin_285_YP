// Утилита для отслеживания просмотров игр

const STORAGE_KEY = 'game_views_stats'

export function trackGameView(gameId) {
  const stats = getViewStats()
  
  if (!stats[gameId]) {
    stats[gameId] = {
      views: 0,
      lastViewed: null
    }
  }
  
  stats[gameId].views += 1
  stats[gameId].lastViewed = new Date().toISOString()
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stats))
}

export function getViewStats() {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored ? JSON.parse(stored) : {}
}

export function getGameViews(gameId) {
  const stats = getViewStats()
  return stats[gameId]?.views || 0
}

export function getTotalViews() {
  const stats = getViewStats()
  return Object.values(stats).reduce((sum, stat) => sum + stat.views, 0)
}

export function getMostViewedGames(games, limit = 10) {
  const stats = getViewStats()
  
  return games
    .map(game => ({
      ...game,
      views: stats[game.id]?.views || 0,
      lastViewed: stats[game.id]?.lastViewed || null
    }))
    .sort((a, b) => b.views - a.views)
    .slice(0, limit)
}

export function clearViewStats() {
  localStorage.removeItem(STORAGE_KEY)
}



