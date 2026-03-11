// Утилита для работы с localStorage
export const saveGames = (games) => {
  try {
    localStorage.setItem('warpoint_games', JSON.stringify(games))
  } catch (error) {
    console.error('Ошибка сохранения игр:', error)
  }
}

export const loadGames = (defaultGames) => {
  try {
    const saved = localStorage.getItem('warpoint_games')
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (error) {
    console.error('Ошибка загрузки игр:', error)
  }
  return defaultGames
}

export const saveBanners = (banners) => {
  try {
    localStorage.setItem('warpoint_banners', JSON.stringify(banners))
  } catch (error) {
    console.error('Ошибка сохранения баннеров:', error)
  }
}

export const loadBanners = (defaultBanners) => {
  try {
    const saved = localStorage.getItem('warpoint_banners')
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (error) {
    console.error('Ошибка загрузки баннеров:', error)
  }
  return defaultBanners
}

