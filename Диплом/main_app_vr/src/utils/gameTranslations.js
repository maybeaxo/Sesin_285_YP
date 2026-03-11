// Утилита для получения переведенных данных игры

function isValidTranslation(translated, key) {
  // Проверяем, что перевод существует и не равен ключу (что означает, что перевод не найден)
  if (translated === null || translated === undefined) {
    return false
  }
  
  // Если это строка, проверяем, что она не равна ключу
  if (typeof translated === 'string') {
    return translated !== key
  }
  
  // Если это массив, считаем валидным
  if (Array.isArray(translated)) {
    return translated.length > 0
  }
  
  // Для других типов считаем валидным, если значение существует
  return true
}

export function getTranslatedGame(game, t, language) {
  if (!game) return game
  
  const gameId = String(game.id)
  
  // Получаем переводы для игры
  // Структура в games.en.json / games.ru.json:
  // {
  //   "games": {
  //     "1": { "title": "...", "description": "...", ... }
  //   }
  // }
  // Поэтому ключи вида games.<id>.field
  const titleKey = `games.${gameId}.title`
  const descKey = `games.${gameId}.description`
  const durationKey = `games.${gameId}.duration`
  const playersKey = `games.${gameId}.players`
  const featuresKey = `games.${gameId}.features`
  
  const gameTitle = t(titleKey)
  const gameDescription = t(descKey)
  const gameDuration = t(durationKey)
  const gamePlayers = t(playersKey)
  const gameFeatures = t(featuresKey)
  
  // Проверяем, что переводы действительно получены (не равны ключам)
  const hasTitle = gameTitle && typeof gameTitle === 'string' && gameTitle !== titleKey
  const hasDescription = gameDescription && typeof gameDescription === 'string' && gameDescription !== descKey
  const hasDuration = gameDuration && typeof gameDuration === 'string' && gameDuration !== durationKey
  const hasPlayers = gamePlayers && typeof gamePlayers === 'string' && gamePlayers !== playersKey
  const hasFeatures = Array.isArray(gameFeatures) && gameFeatures.length > 0
  
  // Обрабатываем features - может быть массивом или нужно переводить каждый элемент
  let translatedFeatures = game.features
  if (hasFeatures) {
    // Если в переводах есть готовый массив features
    translatedFeatures = gameFeatures
  } else {
    // Переводим каждый feature отдельно
    translatedFeatures = game.features.map(f => {
      const featureKey = `games.features.${f}`
      const translated = t(featureKey)
      return (translated && typeof translated === 'string' && translated !== featureKey) ? translated : f
    })
  }
  
  return {
    ...game,
    title: hasTitle ? gameTitle : game.title,
    description: hasDescription ? gameDescription : game.description,
    duration: hasDuration ? gameDuration : game.duration,
    players: hasPlayers ? gamePlayers : game.players,
    genre: game.genre.map(g => {
      const genreKey = `games.genres.${g}`
      const translated = t(genreKey)
      return (translated && typeof translated === 'string' && translated !== genreKey) ? translated : g
    }),
    platform: game.platform.map(p => {
      const platformKey = `games.platforms.${p}`
      const translated = t(platformKey)
      return (translated && typeof translated === 'string' && translated !== platformKey) ? translated : p
    }),
    features: translatedFeatures,
    languages: game.languages.map(l => {
      const langKey = `games.languages.${l}`
      const translated = t(langKey)
      return (translated && typeof translated === 'string' && translated !== langKey) ? translated : l
    })
  }
}

export function getTranslatedGenre(genre, t) {
  const key = `games.genres.${genre}`
  const translated = t(key)
  return isValidTranslation(translated, key) ? translated : genre
}

export function getTranslatedPlatform(platform, t) {
  const key = `games.platforms.${platform}`
  const translated = t(key)
  return isValidTranslation(translated, key) ? translated : platform
}

export function getTranslatedDurationFilter(filter, t) {
  const key = `games.durationFilters.${filter.label}`
  const translated = t(key)
  return isValidTranslation(translated, key) ? translated : filter.label
}

