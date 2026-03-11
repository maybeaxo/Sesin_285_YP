import { useState, useRef, useEffect } from 'react'
import './AdminLogin.css'

function AdminLogin({ onLogin, onClose }) {
  const [pin, setPin] = useState('')
  const [error, setError] = useState(false)
  const inputRef = useRef(null)

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (onLogin(pin)) {
      setPin('')
      setError(false)
    } else {
      setError(true)
      setPin('')
      setTimeout(() => setError(false), 2000)
    }
  }

  const handleChange = (e) => {
    const value = e.target.value.replace(/\D/g, '') // Только цифры
    if (value.length <= 4) {
      setPin(value)
      setError(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  return (
    <div className="admin-login-overlay" onClick={onClose}>
      <div className="admin-login-modal" onClick={(e) => e.stopPropagation()}>
        <button className="admin-login-close" onClick={onClose}>×</button>
        <h2>Вход в настройки</h2>
        <form onSubmit={handleSubmit}>
          <div className="admin-login-input-wrapper">
            <input
              ref={inputRef}
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              value={pin}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder="Введите PIN-код"
              className={`admin-login-input ${error ? 'error' : ''}`}
              maxLength={4}
            />
            <div className="admin-login-dots">
              {[0, 1, 2, 3].map((i) => (
                <span 
                  key={i} 
                  className={`admin-login-dot ${i < pin.length ? 'filled' : ''}`}
                />
              ))}
            </div>
          </div>
          {error && (
            <p className="admin-login-error">Неверный PIN-код</p>
          )}
          <button type="submit" className="admin-login-submit">Войти</button>
        </form>
      </div>
    </div>
  )
}

export default AdminLogin

