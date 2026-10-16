import { Link } from 'react-router'
import { Code2, Calculator } from 'lucide-react'
import { getRankForLevel, subjects } from '../data/subjects'

const subjectDescriptions = {
  informatics:
    'Алгоритмы, прототипы и сложные задачи. Оттачивай навыки и зарабатывай XP за каждое решение.',
  mathematics:
    'Профильный ЕГЭ, математические задачи и испытания, которые прокачивают твою логику.',
}

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
        {Object.values(subjects).map((subject) => {
          const rank = getRankForLevel(subject.level)
          const SubjectIcon =
            subject.slug === 'informatics' ? Code2 : Calculator

          return (
            <Link
              key={subject.slug}
              to={`/tasks/${subject.slug}`}
              className={`practice-subject-card is-${subject.accent}`}
            >
              <span className="practice-subject-label">
                ПОДГОТОВКА К ЕГЭ
              </span>

              <div className="practice-tier-badge">
                <img
                  className="practice-tier-image"
                  src={rank.image}
                  alt={`${rank.name} tier`}
                />
                <span className="practice-tier-level">
                  {subject.level}
                </span>
              </div>

              <div className="practice-subject-title-row">
                <span className="practice-subject-icon">
                  <SubjectIcon size={23} strokeWidth={1.8} aria-hidden="true" />
                </span>
                <h2>{subject.name}</h2>
              </div>

              <p className="practice-subject-description">
                {subjectDescriptions[subject.slug]}
              </p>
            </Link>
          )
        })}
      </div>
    </div>
  )
}
