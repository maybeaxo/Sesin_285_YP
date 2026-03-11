import { useState, useEffect } from 'react'
import { promoBanners } from '../data/games'
import './PromoBanner.css'

function PromoBanner({ banners = promoBanners }) {
  const [currentBanner, setCurrentBanner] = useState(0)

  useEffect(() => {
    if (banners.length <= 1) return

    const interval = setInterval(() => {
      setCurrentBanner((prev) => (prev + 1) % banners.length)
    }, 5000)

    return () => clearInterval(interval)
  }, [banners.length])

  if (banners.length === 0) return null

  return (
    <div className="promo-banner">
      <div className="promo-banner-container">
        {banners.map((banner, index) => (
          <div
            key={banner.id}
            className={`promo-banner-item ${index === currentBanner ? 'active' : ''}`}
            style={{ backgroundImage: `url(${banner.image})` }}
          >
            <div className="promo-banner-overlay" />
            <div className="promo-banner-content">
              <h3 className="promo-banner-title">{banner.title}</h3>
            </div>
          </div>
        ))}
      </div>
      
      {banners.length > 1 && (
        <div className="promo-banner-indicators">
          {banners.map((_, index) => (
            <button
              key={index}
              className={`promo-indicator ${index === currentBanner ? 'active' : ''}`}
              onClick={() => setCurrentBanner(index)}
              aria-label={`Баннер ${index + 1}`}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default PromoBanner
