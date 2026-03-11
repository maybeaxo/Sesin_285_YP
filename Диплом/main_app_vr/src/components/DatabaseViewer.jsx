import db from '../../db.json'
import './DatabaseViewer.css'

const TABLES = [
  {
    key: 'games',
    title: 'Games',
    subtitle: 'Основные атрибуты игр',
    columns: ['id', 'title', 'developer', 'rating', 'durationId', 'ageRatingId', 'availability']
  },
  {
    key: 'genres',
    title: 'Genres',
    subtitle: 'Жанры (справочник)',
    columns: ['id', 'name']
  },
  {
    key: 'platforms',
    title: 'Platforms',
    subtitle: 'Платформы (справочник)',
    columns: ['id', 'name']
  },
  {
    key: 'languages',
    title: 'Languages',
    subtitle: 'Языки (справочник)',
    columns: ['id', 'name']
  },
  {
    key: 'features',
    title: 'Features',
    subtitle: 'Особенности (справочник)',
    columns: ['id', 'name']
  },
  {
    key: 'ageRatings',
    title: 'Age Ratings',
    subtitle: 'Возрастные рейтинги',
    columns: ['id', 'label', 'numericValue']
  },
  {
    key: 'durations',
    title: 'Durations',
    subtitle: 'Категории длительности',
    columns: ['id', 'label', 'minutes']
  },
  {
    key: 'screenshots',
    title: 'Screenshots',
    subtitle: 'Скриншоты по играм',
    columns: ['id', 'gameId', 'order', 'url']
  },
  {
    key: 'promoBanners',
    title: 'Promo Banners',
    subtitle: 'Промо-баннеры',
    columns: ['id', 'title', 'gameId', 'link']
  },
  {
    key: 'gameGenres',
    title: 'Game ↔ Genre',
    subtitle: 'Связи многие-ко-многим',
    columns: ['gameId', 'genreId']
  },
  {
    key: 'gamePlatforms',
    title: 'Game ↔ Platform',
    subtitle: 'Связи многие-ко-многим',
    columns: ['gameId', 'platformId']
  },
  {
    key: 'gameLanguages',
    title: 'Game ↔ Language',
    subtitle: 'Связи многие-ко-многим',
    columns: ['gameId', 'languageId']
  },
  {
    key: 'gameFeatures',
    title: 'Game ↔ Feature',
    subtitle: 'Связи многие-ко-многим',
    columns: ['gameId', 'featureId']
  }
]

const formatValue = (value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (value === null || value === undefined) {
    return '—'
  }
  if (typeof value === 'boolean') {
    return value ? 'Да' : 'Нет'
  }
  return value
}

function DatabaseViewer({ onBack }) {
  return (
    <div className="db-viewer">
      <header className="db-viewer__header">
        <button className="db-viewer__back" onClick={onBack}>
          ← Назад
        </button>
        <div>
          <p className="db-viewer__eyebrow">Псевдо-БД</p>
          <h1>WARPOINT VR — Data Tables</h1>
          <p className="db-viewer__subtitle">
            Структура соответствует ER-диаграмме и файлу <code>db.json</code>
          </p>
        </div>
      </header>

      <div className="db-viewer__tables">
        {TABLES.map(({ key, title, subtitle, columns }) => {
          const rows = db[key] ?? []
          return (
            <section key={key} className="db-viewer__card">
              <div className="db-viewer__card-header">
                <div>
                  <h2>{title}</h2>
                  <p>{subtitle}</p>
                </div>
                <span className="db-viewer__badge">{rows.length}</span>
              </div>
              <div className="db-viewer__table-wrapper">
                <table>
                  <thead>
                    <tr>
                      {columns.map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={columns.map((column) => row[column]).join('-')}>
                        {columns.map((column) => (
                          <td key={column}>{formatValue(row[column])}</td>
                        ))}
                      </tr>
                    ))}
                    {rows.length === 0 && (
                      <tr>
                        <td colSpan={columns.length} className="db-viewer__empty">
                          Нет данных
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          )
        })}
      </div>
    </div>
  )
}

export default DatabaseViewer


