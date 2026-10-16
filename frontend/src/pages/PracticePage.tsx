
import { Link } from 'react-router'

const subjects = [
  {
    slug: 'informatics',
    name: 'Информатика',
    description: 'Алгоритмы, прототипы и сложные задачи. Оттачивай навыки и зарабатывай XP за каждое решение.',
    tierImage: '/diamond.png',
    accent: 'red',
  },
  {
    slug: 'mathematics',
    name: 'Математика',
    description: 'Профильный ЕГЭ, математические задачи и испытания, которые прокачивают твою логику.',
    tierImage: '/platinum.png',
    accent: 'gold',
  },
]

export default function PracticePage() {
  return (
    <div className="practice-page">
      <header className="practice-heading">
        <div className="home-accent-line" />
        <h1 className="home-title">Практика</h1>
        <p className="home-description">
          Выбирай предмет, оттачивай навыки и повышай свой тир.
        </p>
      </header>

      <div className="practice-subject-grid">
        {subjects.map((subject) => (
          <Link
            key={subject.slug}
            to={`/tasks/${subject.slug}`}
            className={`practice-subject-card is-${subject.accent}`}
          >
            <span className="practice-subject-label">
              ПОДГОТОВКА К ЕГЭ
            </span>

            <img
              className="practice-tier-image"
              src={subject.tierImage}
              alt="Эмблема текущего тира"
            />

            <div className="practice-subject-title-row">
              <h2>{subject.name}</h2>
            </div>

            <p className="practice-subject-description">
              {subject.description}
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}
