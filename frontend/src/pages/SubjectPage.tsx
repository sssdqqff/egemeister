import { Link, Navigate, useParams } from 'react-router'

const subjects = {
  informatics: {
    name: 'Информатика',
    description: 'Алгоритмы, прототипы и задачи ЕГЭ. Оттачивай навыки, разбирай сложные механики и поднимай свой тир.',
    image: '/diamond.png',
    accent: 'red',
  },
  mathematics: {
    name: 'Математика',
    description: 'Задачи профильного ЕГЭ, логика и нестандартные решения. Каждый новый уровень начинается с практики.',
    image: '/platinum.png',
    accent: 'gold',
  },
}

const modes = [
  {
    number: '01',
    label: 'ПО НОМЕРАМ ЕГЭ',
    title: 'Выбрать номер',
    description: 'Тренируй конкретный номер экзамена и отрабатывай темы, в которых хочется разобраться лучше.',
    path: 'topics',
  },
  {
    number: '02',
    label: 'ПО ТИПАМ ЗАДАЧ',
    title: 'Выбрать прототип',
    description: 'Сосредоточься на конкретном типе задачи и научись решать разные варианты одного прототипа.',
    path: 'prototypes',
  },
  {
    number: '03',
    label: 'БЕЗ ОГРАНИЧЕНИЙ',
    title: 'Смешанная тренировка',
    description: 'Практикуйся на разных задачах и проверяй, насколько уверенно ориентируешься в предмете.',
    path: 'mixed',
  },
]

export default function SubjectPage() {
  const { subjectSlug } = useParams()
  const subject = subjectSlug ? subjects[subjectSlug as keyof typeof subjects] : undefined

  if (!subject) return <Navigate to="/tasks" replace />

  return (
    <div className={`subject-page is-${subject.accent}`}>
      <Link to="/tasks" className="subject-back-link">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M19 12H5m0 0 6 6m-6-6 6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Все предметы
      </Link>

      <header className="subject-hero">
        <div className="subject-hero-content">
          <span className="subject-eyebrow">ТРЕНИРОВОЧНАЯ КОМНАТА</span>
          <h1>{subject.name}</h1>
          <p>{subject.description}</p>
        </div>
        <img className="subject-hero-emblem" src={subject.image} alt="" />
        <div className="subject-hero-glow" />
      </header>

      <section className="subject-modes-section">
        <div className="subject-section-heading">
          <div>
            <span className="subject-eyebrow">ВЫБЕРИ СВОЙ ПУТЬ</span>
            <h2>Режим тренировки</h2>
          </div>
          <p>Выбирай режим под свою цель</p>
        </div>

        <div className="subject-modes-grid">
          {modes.map((mode) => (
            <Link
              key={mode.path}
              to={`/tasks/${subjectSlug}/${mode.path}`}
              className="subject-mode-card"
            >
              <div className="subject-mode-top">
                <span className="subject-mode-number">{mode.number}</span>
                <span className="subject-mode-label">{mode.label}</span>
              </div>
              <div className="subject-mode-bottom">
                <div>
                  <h3>{mode.title}</h3>
                  <p>{mode.description}</p>
                </div>
                <span className="subject-mode-arrow" aria-hidden="true">↗</span>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
