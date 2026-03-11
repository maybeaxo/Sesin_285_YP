import { useState } from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { getTranslatedGame } from '../utils/gameTranslations'
import './QuickSelect.css'

function QuickSelect({ games, onGameSelect, onClose }) {
  const { t, language } = useLanguage()
  const [step, setStep] = useState(1)
  const [answers, setAnswers] = useState({
    players: null,
    genre: null,
    difficulty: null,
    duration: null
  })

  const questions = [
    {
      id: 'players',
      question: t('quickSelect.question1'),
      answers: [
        { value: '1', label: t('quickSelect.answer1_1') },
        { value: '2-4', label: t('quickSelect.answer1_2') },
        { value: '5+', label: t('quickSelect.answer1_3') }
      ]
    },
    {
      id: 'genre',
      question: t('quickSelect.question2'),
      answers: [
        { value: 'Экшен', label: t('quickSelect.answer2_1') },
        { value: 'Приключения', label: t('quickSelect.answer2_2') },
        { value: 'Хоррор', label: t('quickSelect.answer2_3') },
        { value: 'Головоломка', label: t('quickSelect.answer2_4') },
        { value: 'Ритм', label: t('quickSelect.answer2_5') }
      ]
    },
    {
      id: 'difficulty',
      question: t('quickSelect.question3'),
      answers: [
        { value: 'easy', label: t('quickSelect.answer3_1') },
        { value: 'medium', label: t('quickSelect.answer3_2') },
        { value: 'hard', label: t('quickSelect.answer3_3') }
      ]
    },
    {
      id: 'duration',
      question: t('quickSelect.question4'),
      answers: [
        { value: '0-60', label: t('quickSelect.answer4_1') },
        { value: '60-180', label: t('quickSelect.answer4_2') },
        { value: '180+', label: t('quickSelect.answer4_3') }
      ]
    }
  ]

  const handleAnswer = (questionId, value) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
  }

  const handleNext = () => {
    if (step < questions.length) {
      setStep(step + 1)
    } else {
      findGames()
    }
  }

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1)
    }
  }

  const findGames = () => {
    const filtered = games.filter(game => {
      // Фильтр по игрокам
      if (answers.players === '1' && game.playersNum > 1) return false
      if (answers.players === '2-4' && (game.playersNum < 2 || game.playersNum > 4)) return false
      if (answers.players === '5+' && game.playersNum < 5) return false

      // Фильтр по жанру
      if (answers.genre && !game.genre.includes(answers.genre)) return false

      // Фильтр по сложности (на основе рейтинга)
      if (answers.difficulty === 'easy' && game.rating < 7) return false
      if (answers.difficulty === 'hard' && game.rating < 8.5) return false

      // Фильтр по длительности
      if (answers.duration === '0-60' && game.durationMinutes > 60) return false
      if (answers.duration === '60-180' && (game.durationMinutes < 60 || game.durationMinutes > 180)) return false
      if (answers.duration === '180+' && game.durationMinutes < 180) return false

      return game.availability
    })

    // Сортируем по рейтингу
    filtered.sort((a, b) => b.rating - a.rating)

    setStep(5) // Переход к результатам
    setAnswers(prev => ({ ...prev, results: filtered.slice(0, 5) }))
  }

  const currentQuestion = questions[step - 1]

  if (step === 5) {
    const results = answers.results || []
    
    return (
      <div className="quick-select-overlay" onClick={onClose}>
        <div className="quick-select-modal" onClick={(e) => e.stopPropagation()}>
          <div className="quick-select-header">
            <h2>{t('quickSelect.results')}</h2>
            <button className="quick-select-close" onClick={onClose}>×</button>
          </div>
          
          <div className="quick-select-results">
            {results.length > 0 ? (
              results.map(game => {
                const translatedGame = getTranslatedGame(game, t, language)
                return (
                  <div 
                    key={game.id} 
                    className="quick-select-result-card"
                    onClick={() => {
                      onGameSelect(game)
                      onClose()
                    }}
                  >
                    <img src={game.image} alt={translatedGame.title} />
                    <div className="quick-select-result-info">
                      <h3>{translatedGame.title}</h3>
                      <p>{game.developer}</p>
                      <div className="quick-select-result-rating">
                        ⭐ {game.rating}
                      </div>
                    </div>
                  </div>
                )
              })
            ) : (
              <div className="quick-select-no-results">
                <p>{t('quickSelect.noResults')}</p>
                <button onClick={() => setStep(1)} className="quick-select-retry">
                  {t('quickSelect.back')}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="quick-select-overlay" onClick={onClose}>
      <div className="quick-select-modal" onClick={(e) => e.stopPropagation()}>
        <div className="quick-select-header">
          <h2>{t('quickSelect.title')}</h2>
          <button className="quick-select-close" onClick={onClose}>×</button>
        </div>
        
        <div className="quick-select-progress">
          <div className="quick-select-progress-bar" style={{ width: `${(step / questions.length) * 100}%` }}></div>
          <span>{step} / {questions.length}</span>
        </div>

        <div className="quick-select-content">
          <h3>{currentQuestion.question}</h3>
          
          <div className="quick-select-answers">
            {currentQuestion.answers.map((answer, idx) => (
              <button
                key={idx}
                className={`quick-select-answer ${answers[currentQuestion.id] === answer.value ? 'selected' : ''}`}
                onClick={() => handleAnswer(currentQuestion.id, answer.value)}
              >
                {answer.label}
              </button>
            ))}
          </div>

          <div className="quick-select-actions">
            {step > 1 && (
              <button className="quick-select-btn secondary" onClick={handleBack}>
                {t('quickSelect.back')}
              </button>
            )}
            <button 
              className="quick-select-btn primary" 
              onClick={handleNext}
              disabled={!answers[currentQuestion.id]}
            >
              {step === questions.length ? t('quickSelect.findGames') : t('quickSelect.next')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default QuickSelect

