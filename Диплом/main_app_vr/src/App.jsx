import { useState, useEffect } from 'react'
import GameList from './components/GameList'
import GameDetail from './components/GameDetail'
import Header from './components/Header'
import HomeScreen from './components/HomeScreen'
import DatabaseViewer from './components/DatabaseViewer'
import AdminPanel from './components/AdminPanel'
import AdminLogin from './components/AdminLogin'
import QuickSelect from './components/QuickSelect'
import { vrGames, promoBanners } from './data/games'
import { loadGames, saveGames, loadBanners, saveBanners } from './utils/storage'
import { trackGameView } from './utils/viewTracker'
import './App.css'

function App() {
  const [currentScreen, setCurrentScreen] = useState('home')
  const [selectedGame, setSelectedGame] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedGenre, setSelectedGenre] = useState('Все')
  const [selectedPlatform, setSelectedPlatform] = useState('Все')
  const [selectedAgeRating, setSelectedAgeRating] = useState('Все')
  const [selectedDuration, setSelectedDuration] = useState('all')
  const [games, setGames] = useState(() => loadGames(vrGames))
  const [banners, setBanners] = useState(() => loadBanners(promoBanners))
  const [showAdminLogin, setShowAdminLogin] = useState(false)
  const [isAdmin, setIsAdmin] = useState(false)
  const [showQuickSelect, setShowQuickSelect] = useState(false)

  // Сохранение при изменении игр
  useEffect(() => {
    saveGames(games)
  }, [games])

  useEffect(() => {
    saveBanners(banners)
  }, [banners])

  const handleGameSelect = (game) => {
    setSelectedGame(game)
    setCurrentScreen('detail')
    trackGameView(game.id)
  }

  const handleBack = () => {
    if (currentScreen === 'detail') {
      setSelectedGame(null)
      setCurrentScreen('games')
    } else if (currentScreen === 'games') {
      setCurrentScreen('home')
    } else if (currentScreen === 'admin') {
      setCurrentScreen('home')
      setIsAdmin(false)
    } else if (currentScreen === 'db') {
      setCurrentScreen('admin')
    }
  }

  const handleEnterCatalog = () => {
    setCurrentScreen('games')
  }

  const handleShowDatabase = () => {
    setCurrentScreen('db')
  }

  const handleGamesUpdate = (updatedGames) => {
    setGames(updatedGames)
  }

  const handleBannersUpdate = (updatedBanners) => {
    setBanners(updatedBanners)
  }

  const handleAdminLogin = (pin) => {
    if (pin === '0309') {
      setIsAdmin(true)
      setShowAdminLogin(false)
      setCurrentScreen('admin')
      return true
    }
    return false
  }

  const handleAdminButtonClick = () => {
    setShowAdminLogin(true)
  }

  const handleAdminLoginClose = () => {
    setShowAdminLogin(false)
  }

  return (
    <div className="app">

      {/* Модальное окно входа в админ-панель */}
      {showAdminLogin && (
        <AdminLogin 
          onLogin={handleAdminLogin}
          onClose={handleAdminLoginClose}
        />
      )}

      {/* Модальное окно быстрого выбора */}
      {showQuickSelect && (
        <QuickSelect
          games={games}
          onGameSelect={handleGameSelect}
          onClose={() => setShowQuickSelect(false)}
        />
      )}

      {currentScreen === 'home' ? (
        <HomeScreen 
          onEnter={handleEnterCatalog}
          onQuickSelect={() => setShowQuickSelect(true)}
        />
      ) : currentScreen === 'db' ? (
        <DatabaseViewer onBack={handleBack} />
      ) : currentScreen === 'admin' ? (
        <AdminPanel 
          onBack={handleBack}
          onShowDatabase={handleShowDatabase}
          games={games}
          banners={banners}
          onGamesUpdate={handleGamesUpdate}
          onBannersUpdate={handleBannersUpdate}
        />
      ) : (
        <>
          {currentScreen === 'games' && (
            <Header 
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              selectedGenre={selectedGenre}
              setSelectedGenre={setSelectedGenre}
              selectedPlatform={selectedPlatform}
              setSelectedPlatform={setSelectedPlatform}
              selectedAgeRating={selectedAgeRating}
              setSelectedAgeRating={setSelectedAgeRating}
              selectedDuration={selectedDuration}
              setSelectedDuration={setSelectedDuration}
              onBack={handleBack}
              currentScreen={currentScreen}
              onAdminClick={handleAdminButtonClick}
            />
          )}
          <main className="main-content">
            {currentScreen === 'detail' ? (
              <GameDetail game={selectedGame} onBack={handleBack} />
            ) : (
              <GameList 
                games={games}
                searchQuery={searchQuery}
                selectedGenre={selectedGenre}
                selectedPlatform={selectedPlatform}
                selectedAgeRating={selectedAgeRating}
                selectedDuration={selectedDuration}
                onGameSelect={handleGameSelect}
                onQuickSelect={() => setShowQuickSelect(true)}
              />
            )}
          </main>
        </>
      )}
    </div>
  )
}

export default App
