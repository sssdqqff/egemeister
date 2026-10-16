import { useState, type FormEvent } from 'react'
import { Link, Navigate, useParams } from 'react-router'
import {
  ArrowLeft,
  ArrowRight,
  Check,
  ChevronRight,
  Info,
  Minus,
  Plus,
  ScrollText,
  Sparkles,
} from 'lucide-react'
import { getRankForLevel, subjects, type SubjectSlug } from '../data/subjects'

type Panel = 'generated' | 'official' | null
type Difficulty = 'easy' | 'medium' | 'hard'

const difficulties: { value: Difficulty; label: string; description: string }[] = [
  { value: 'easy', label: 'Лёгкий', description: 'Закрепление основ' },
  { value: 'medium', label: 'Средний', description: 'Обычный уровень' },
  { value: 'hard', label: 'Сложный', description: 'Повышенная сложность' },
]

const difficultyHints: Record<Difficulty, string> = {
  easy: 'Изи-вариант — самые лёгкие задания каждого номера. Отлично, чтобы набить руку.',
  medium: 'Нормальный уровень — задания каждого номера без крайностей. Уже нужно разобраться в условии и подобрать решение.',
  hard: 'На подумать — сложные задания каждого номера. Придётся искать идею решения и хорошенько поработать головой.',
}

const examWaves = [
  { value: 'early', label: 'Досрочная волна' },
  { value: 'main', label: 'Основная волна' },
  { value: 'additional', label: 'Дополнительный период' },
  { value: 'resit', label: 'Пересдача' },
]

const years = [2026, 2025, 2024, 2023, 2022]

export default function SubjectPage() {
  const { subjectSlug } = useParams()
  const [activePanel, setActivePanel] = useState<Panel>(null)
  const [difficulty, setDifficulty] = useState<Difficulty>('medium')
  const [wave, setWave] = useState('main')
  const [year, setYear] = useState(2026)
  const [notice, setNotice] = useState('')

  const subject =
    subjectSlug && Object.prototype.hasOwnProperty.call(subjects, subjectSlug)
      ? subjects[subjectSlug as SubjectSlug]
      : undefined

  if (!subject) return <Navigate to="/tasks" replace />

  const rank = getRankForLevel(subject.level)
  const currentXp = subject.xp.current
  const requiredXp = subject.xp.required
  const xpPercent = Math.min(100, Math.round((currentXp / requiredXp) * 100))
  const remainingXp = Math.max(0, requiredXp - currentXp)
  const taskCount = subject.slug === 'informatics' ? 27 : 19
  const taskNumbers = Array.from({ length: taskCount }, (_, index) => index + 1)

  const stats = [
    {
      label: 'Заданий решено',
      value: subject.stats.solvedTasks?.toLocaleString('ru-RU') ?? '—',
    },
    {
      label: 'Тем изучено',
      value: subject.stats.topicsCompleted?.toLocaleString('ru-RU') ?? '—',
    },
  ]

  function togglePanel(panel: Exclude<Panel, null>) {
    setActivePanel((current) => current === panel ? null : panel)
    setNotice('')
  }

  function handleGenerate(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const selected = difficulties.find((item) => item.value === difficulty)
    setNotice(
      `Выбрана сложность «${selected?.label}». Для генерации варианта необходимо подключить backend.`,
    )
  }

  function handleOfficial(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const selectedWave = examWaves.find((item) => item.value === wave)
    setNotice(
      `Выбраны параметры: ${year} год, ${selectedWave?.label.toLowerCase()}. Каталог официальных вариантов ещё не подключён.`,
    )
  }

  return (
    <div className={`subject-page is-${subject.accent}`}>
      <Link to="/tasks" className="subject-back-link">
        <ArrowLeft size={17} strokeWidth={1.8} aria-hidden="true" />
        Все предметы
      </Link>

      <section className="subject-summary-card">
        <div className="subject-summary-top">
          <div className="subject-summary-title">
            <span className="subject-summary-kicker">GRANDMASTER / PRACTICE</span>
            <h1>{subject.name}</h1>
            <span className="subject-summary-rank">{rank.name.toUpperCase()}</span>
          </div>

          <div className="subject-summary-emblem" title={`${rank.name} · Level ${subject.level}`}>
            <img src={rank.image} alt={rank.name} />
            <span>{subject.level}</span>
          </div>
        </div>

        <div className="subject-summary-progress">
          <div className="subject-summary-progress-heading">
            <div>
              <span className="subject-summary-progress-label">
                XP ДО LEVEL {subject.level + 1}
              </span>
              <strong>{currentXp} / {requiredXp} XP</strong>
            </div>
            <span className="subject-summary-percent">{xpPercent}%</span>
          </div>

          <div
            className="subject-summary-track"
            role="progressbar"
            aria-label={`Прогресс XP до уровня ${subject.level + 1}`}
            aria-valuemin={0}
            aria-valuemax={requiredXp}
            aria-valuenow={currentXp}
          >
            <div
              className="subject-summary-fill"
              style={{ width: `${xpPercent}%` }}
            />
          </div>

          <span className="subject-summary-hint">
            {remainingXp > 0
              ? `Ещё ${remainingXp} XP до следующего уровня`
              : 'Достаточно XP для следующего уровня'}
          </span>
        </div>

        <div className="subject-summary-stats">
          {stats.map((stat) => (
            <div className="subject-summary-stat" key={stat.label}>
              <span>{stat.label}</span>
              <strong>{stat.value}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="subject-practice-section">
        <div className="subject-section-heading">
          <div>
            <span className="subject-eyebrow">ТРЕНИРОВКА</span>
            <h2>Выбери формат</h2>
          </div>
        </div>

        <div className="subject-action-grid">
          <button
            type="button"
            className={`subject-action-card is-generator ${activePanel === 'generated' ? 'is-active' : ''}`}
            aria-expanded={activePanel === 'generated'}
            onClick={() => togglePanel('generated')}
          >
            <span className="subject-action-icon" aria-hidden="true">
              <Sparkles size={22} strokeWidth={1.7} />
            </span>
            <span className="subject-action-copy">
              <strong>Сгенерировать вариант</strong>
              <span>Собери случайный вариант по сложности</span>
            </span>
            <span className="subject-action-arrow" aria-hidden="true">
              {activePanel === 'generated' ? (
                <Minus size={18} strokeWidth={1.8} />
              ) : (
                <Plus size={18} strokeWidth={1.8} />
              )}
            </span>
          </button>

          <button
            type="button"
            className={`subject-action-card is-official ${activePanel === 'official' ? 'is-active' : ''}`}
            aria-expanded={activePanel === 'official'}
            onClick={() => togglePanel('official')}
          >
            <span className="subject-action-icon" aria-hidden="true">
              <ScrollText size={22} strokeWidth={1.7} />
            </span>
            <span className="subject-action-copy">
              <strong>Официальные варианты</strong>
              <span>Экзаменационные работы по годам и волнам</span>
            </span>
            <span className="subject-action-arrow" aria-hidden="true">
              {activePanel === 'official' ? (
                <Minus size={18} strokeWidth={1.8} />
              ) : (
                <Plus size={18} strokeWidth={1.8} />
              )}
            </span>
          </button>
        </div>

        {activePanel === 'generated' && (
          <form className="subject-action-panel" onSubmit={handleGenerate}>
            <div className="subject-panel-heading">
              <div>
                <span className="subject-eyebrow">СЛУЧАЙНЫЙ ВАРИАНТ</span>
                <h3>Выбери сложность</h3>
              </div>
            </div>

            <div className="subject-difficulty-grid">
              {difficulties.map((item) => (
                <button
                  type="button"
                  key={item.value}
                  className={`subject-difficulty-option ${difficulty === item.value ? 'is-selected' : ''}`}
                  aria-pressed={difficulty === item.value}
                  onClick={() => {
                    setDifficulty(item.value)
                    setNotice('')
                  }}
                >
                  <span className="subject-difficulty-radio">
                    {difficulty === item.value && (
                      <Check size={12} strokeWidth={2.5} />
                    )}
                  </span>
                  <strong>{item.label}</strong>
                  <span>{item.description}</span>
                </button>
              ))}
            </div>

            <div className="subject-panel-footer">
              <p>{difficultyHints[difficulty]}</p>
              <button type="submit" className="subject-primary-button">
                <Sparkles size={16} strokeWidth={1.8} />
                Подготовить вариант
              </button>
            </div>
          </form>
        )}

        {activePanel === 'official' && (
          <form className="subject-action-panel" onSubmit={handleOfficial}>
            <div className="subject-panel-heading">
              <div>
                <span className="subject-eyebrow">АРХИВ ЕГЭ</span>
                <h3>Найти официальный вариант</h3>
              </div>
            </div>

            <div className="subject-official-fields">
              <label className="subject-field">
                <span>Год проведения</span>
                <select
                  value={year}
                  onChange={(event) => {
                    setYear(Number(event.target.value))
                    setNotice('')
                  }}
                >
                  {years.map((item) => (
                    <option key={item} value={item}>{item} год</option>
                  ))}
                </select>
              </label>

              <label className="subject-field">
                <span>Период экзамена</span>
                <select
                  value={wave}
                  onChange={(event) => {
                    setWave(event.target.value)
                    setNotice('')
                  }}
                >
                  {examWaves.map((item) => (
                    <option key={item.value} value={item.value}>{item.label}</option>
                  ))}
                </select>
              </label>
            </div>

            <div className="subject-panel-footer">
              <p>Выбери год и период экзамена.</p>
              <button type="submit" className="subject-primary-button is-gold">
                <ArrowRight size={16} strokeWidth={1.8} />
                Найти варианты
              </button>
            </div>
          </form>
        )}

        {notice && (
          <div className="subject-action-notice" role="status">
            <Info size={18} strokeWidth={1.8} aria-hidden="true" />
            <p>{notice}</p>
          </div>
        )}
      </section>

      <section className="subject-task-list-section">
        <div className="subject-section-heading">
          <div>
            <span className="subject-eyebrow">ПРАКТИКА ПО ТЕМАМ</span>
            <h2>Задания</h2>
          </div>
          <span className="subject-task-count">{taskCount} номеров</span>
        </div>

        <div className="subject-task-list">
          {taskNumbers.map((number) => (
            <Link
              key={number}
              to={`/tasks/${subject.slug}/topics?number=${number}`}
              className="subject-task-row"
            >
              <span className="subject-task-number">
                {String(number).padStart(2, '0')}
              </span>

              <span className="subject-task-info">
                <strong>Задание № {number}</strong>
                <span>Задачи и прототипы</span>
              </span>

              <span className="subject-task-progress">
                <span className="subject-task-progress-track">
                  <span />
                </span>
                <span className="subject-task-progress-label">Нет данных</span>
              </span>

              <span className="subject-task-arrow" aria-hidden="true">
                <ChevronRight size={19} strokeWidth={1.8} />
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  )
}
