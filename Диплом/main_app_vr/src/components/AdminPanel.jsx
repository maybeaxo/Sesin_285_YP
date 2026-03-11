import { useState, useEffect } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { promoBanners } from '../data/games'
import { getTranslatedGame } from '../utils/gameTranslations'
import AdminStats from './AdminStats'
import './AdminPanel.css'

function AdminPanel({ onBack, onShowDatabase, games: initialGames, banners: initialBanners, onGamesUpdate, onBannersUpdate }) {
  // Получаем и переводчик, и текущий язык (нужен для getTranslatedGame)
  const { t, language } = useLanguage()
  const [password, setPassword] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [games, setGames] = useState(initialGames)
  const [banners, setBanners] = useState(initialBanners)
  const [editingGame, setEditingGame] = useState(null)
  const [showAddForm, setShowAddForm] = useState(false)
  const [activeTab, setActiveTab] = useState('games') // 'games', 'banners', or 'stats'

  // Закрытие модального окна по Escape и блокировка скролла
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && (editingGame || showAddForm)) {
        setEditingGame(null)
        setShowAddForm(false)
      }
    }
    
    // Блокировка скролла при открытом модальном окне
    if (editingGame || showAddForm) {
      document.body.style.overflow = 'hidden'
      window.addEventListener('keydown', handleEscape)
    } else {
      document.body.style.overflow = ''
    }
    
    return () => {
      window.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = ''
    }
  }, [editingGame, showAddForm])

  const handleLogin = (e) => {
    e.preventDefault()
    if (password === '0309') {
      setIsAuthenticated(true)
      setPassword('')
    } else {
      alert('Неверный PIN-код')
    }
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setEditingGame(null)
    setShowAddForm(false)
  }

  const handleDelete = (id) => {
    if (confirm('Вы уверены, что хотите удалить эту игру?')) {
      const updated = games.filter(game => game.id !== id)
      setGames(updated)
      onGamesUpdate(updated)
    }
  }

  const handleEdit = (game) => {
    setEditingGame({ ...game })
    setShowAddForm(false)
  }

  const handleSave = () => {
    if (editingGame) {
      let updated
      if (editingGame.id) {
        updated = games.map(game => game.id === editingGame.id ? editingGame : game)
      } else {
        const newId = Math.max(...games.map(g => g.id), 0) + 1
        updated = [...games, { ...editingGame, id: newId }]
      }
      setGames(updated)
      onGamesUpdate(updated)
      setEditingGame(null)
      setShowAddForm(false)
    }
  }

  const handleAddNew = () => {
    setEditingGame({
      id: null,
      title: '',
      developer: '',
      genre: [],
      platform: [],
      rating: 0,
      releaseDate: new Date().toISOString().split('T')[0],
      description: '',
      image: '',
      screenshots: [],
      video: '',
      features: [],
      duration: '',
      durationMinutes: 0,
      ageRating: '6+',
      ageRatingNum: 6,
      players: '1 игрок',
      playersNum: 1,
      availability: true,
      languages: []
    })
    setShowAddForm(true)
  }

  const handleBannerDelete = (id) => {
    if (confirm('Вы уверены, что хотите удалить этот баннер?')) {
      const updated = banners.filter(banner => banner.id !== id)
      setBanners(updated)
      onBannersUpdate(updated)
    }
  }

  const handleBannerAdd = () => {
    const newId = Math.max(...banners.map(b => b.id), 0) + 1
    const newBanner = {
      id: newId,
      title: '',
      image: '',
      link: null
    }
    setBanners([...banners, newBanner])
  }

  if (!isAuthenticated) {
    return (
      <div className="admin-login">
        <div className="admin-login-container">
          <h2>Административная панель</h2>
          <form onSubmit={handleLogin}>
            <input
              type="password"
              placeholder="Введите пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="admin-password-input"
              autoFocus
            />
            <button type="submit" className="admin-login-button">Войти</button>
          </form>
          <button onClick={onBack} className="admin-back-button">Назад</button>
        </div>
      </div>
    )
  }

  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h1>{t('admin.panel')}</h1>
        <div className="admin-header-actions">
          <button onClick={onShowDatabase} className="admin-button">{t('admin.viewData')}</button>
          <button onClick={handleLogout} className="admin-button">{t('admin.logout')}</button>
          <button onClick={onBack} className="admin-button">{t('admin.back')}</button>
        </div>
      </div>

      <div className="admin-tabs">
        <button 
          className={`admin-tab ${activeTab === 'games' ? 'active' : ''}`}
          onClick={() => setActiveTab('games')}
        >
          {t('admin.games')}
        </button>
        <button 
          className={`admin-tab ${activeTab === 'banners' ? 'active' : ''}`}
          onClick={() => setActiveTab('banners')}
        >
          {t('admin.banners')}
        </button>
        <button 
          className={`admin-tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          {t('admin.stats')}
        </button>
      </div>

      {activeTab === 'games' && (
        <>
          {(editingGame || showAddForm) && (
            <div className="admin-modal-overlay" onClick={() => { setEditingGame(null); setShowAddForm(false) }}>
              <div className="admin-modal" onClick={(e) => e.stopPropagation()}>
                <div className="admin-modal-header">
                  <h2>{editingGame?.id ? t('admin.editGame') : t('admin.addGame')}</h2>
                  <button 
                    className="admin-modal-close"
                    onClick={() => { setEditingGame(null); setShowAddForm(false) }}
                    aria-label={t('admin.close')}
                  >
                    ×
                  </button>
                </div>
                <div className="admin-modal-content">
                  <div className="admin-form-grid">
                <div>
                  <label>{t('admin.title')} *</label>
                  <input
                    type="text"
                    value={editingGame?.title || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, title: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label>{t('admin.developer')} *</label>
                  <input
                    type="text"
                    value={editingGame?.developer || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, developer: e.target.value })}
                    required
                  />
                </div>
                <div className="full-width">
                  <label>{t('admin.description')} *</label>
                  <textarea
                    value={editingGame?.description || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, description: e.target.value })}
                    rows="3"
                    required
                  />
                </div>
                <div>
                  <label>{t('admin.image')} *</label>
                  <input
                    type="text"
                    value={editingGame?.image || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, image: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label>{t('admin.video')}</label>
                  <input
                    type="text"
                    value={editingGame?.video || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, video: e.target.value })}
                    placeholder="https://www.youtube.com/embed/..."
                  />
                </div>
                <div>
                  <label>{t('admin.rating')}</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="10"
                    value={editingGame?.rating || 0}
                    onChange={(e) => setEditingGame({ ...editingGame, rating: parseFloat(e.target.value) })}
                  />
                </div>
                <div>
                  <label>{t('admin.ageRating')}</label>
                  <select
                    value={editingGame?.ageRating || '6+'}
                    onChange={(e) => {
                      const rating = e.target.value
                      setEditingGame({ 
                        ...editingGame, 
                        ageRating: rating,
                        ageRatingNum: parseInt(rating.replace('+', ''))
                      })
                    }}
                  >
                    <option value="6+">6+</option>
                    <option value="12+">12+</option>
                    <option value="16+">16+</option>
                    <option value="18+">18+</option>
                  </select>
                </div>
                <div>
                  <label>{t('admin.players')}</label>
                  <input
                    type="text"
                    value={editingGame?.players || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, players: e.target.value })}
                    placeholder={t('admin.playersPlaceholder')}
                  />
                </div>
                <div>
                  <label>{t('admin.duration')}</label>
                  <input
                    type="text"
                    value={editingGame?.duration || ''}
                    onChange={(e) => setEditingGame({ ...editingGame, duration: e.target.value })}
                    placeholder={t('admin.durationPlaceholder')}
                  />
                </div>
                <div>
                  <label>{t('admin.availability')}</label>
                  <select
                    value={editingGame?.availability ? 'true' : 'false'}
                    onChange={(e) => setEditingGame({ ...editingGame, availability: e.target.value === 'true' })}
                  >
                    <option value="true">{t('admin.available')}</option>
                    <option value="false">{t('admin.unavailable')}</option>
                  </select>
                </div>
                  </div>
                  <div className="admin-form-actions">
                    <button onClick={handleSave} className="admin-button primary">{t('admin.save')}</button>
                    <button onClick={() => { setEditingGame(null); setShowAddForm(false) }} className="admin-button">{t('admin.cancel')}</button>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="admin-games-list">
            <div className="admin-section-header">
              <h2>{t('admin.gameList')} ({games.length})</h2>
              <button onClick={handleAddNew} className="admin-button primary">{t('admin.addGame')}</button>
            </div>
            <div className="admin-games-grid">
              {games.map(game => {
                const translatedGame = getTranslatedGame(game, t, language)
                return (
                  <div key={game.id} className="admin-game-card">
                    <img src={game.image} alt={translatedGame.title} />
                    <div className="admin-game-info">
                      <h3>{translatedGame.title}</h3>
                      <p>{game.developer}</p>
                      <div className="admin-game-status">
                        <span className={game.availability ? 'available' : 'unavailable'}>
                          {game.availability ? t('admin.available') : t('admin.unavailable')}
                        </span>
                      </div>
                      <div className="admin-game-actions">
                        <button onClick={() => handleEdit(game)} className="admin-button small">{t('admin.editGame')}</button>
                        <button onClick={() => handleDelete(game.id)} className="admin-button small danger">{t('admin.deleteGame')}</button>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </>
      )}

      {activeTab === 'banners' && (
        <div className="admin-banners-list">
          <div className="admin-section-header">
            <h2>{t('admin.bannerList')} ({banners.length})</h2>
            <button onClick={handleBannerAdd} className="admin-button primary">{t('admin.addBanner')}</button>
          </div>
          <div className="admin-banners-grid">
            {banners.map(banner => (
              <div key={banner.id} className="admin-banner-card">
                <img src={banner.image} alt={banner.title} />
                <div className="admin-banner-info">
                  <h3>{banner.title || 'Без названия'}</h3>
                  <button onClick={() => handleBannerDelete(banner.id)} className="admin-button small danger">{t('admin.deleteBanner')}</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'stats' && (
        <AdminStats games={games} />
      )}
    </div>
  )
}

export default AdminPanel
