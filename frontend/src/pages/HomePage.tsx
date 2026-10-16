
import { useMemo, useState } from 'react'
import { Link } from 'react-router'

type SubjectKey = 'informatics' | 'mathematics'

type ExamMarker = {
  date: string
  subject: SubjectKey
  title: string
}

type ActivityDay = {
  date: Date
  key: string
  solved: number
  xp: number
  level: number
  isToday: boolean
  isInSeason: boolean
  isFuture: boolean
  exam: ExamMarker | null
}

const activityColors = [
  '#252A28',
  '#542622',
  '#94372F',
  '#ED493F',
  '#F4C34F',
]

const examDates: ExamMarker[] = []

const challenges = {
  informatics: {
    subject: 'Информатика',
    topic: 'Системы счисления',
    description: 'Реши три задания и проверь, насколько уверенно работаешь с разными основаниями систем счисления.',
    tag: 'ТРЕНАЖЁР · ИНФОРМАТИКА',
  },
  mathematics: {
    subject: 'Математика',
    topic: 'Уравнения',
    description: 'Реши три задания на уравнения и закрепи навыки решения задач профильного ЕГЭ.',
    tag: 'ТРЕНАЖЁР · МАТЕМАТИКА',
  },
}

const goals = {
  informatics: { subject: 'Информатика', target: 100, lastScore: 76 },
  mathematics: { subject: 'Математика', target: 80, lastScore: 62 },
}

function dateKey(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function formatActivityDate(date: Date) {
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export default function HomePage() {
  const [challengeSubject, setChallengeSubject] = useState<SubjectKey>('informatics')
  const [goalSubject, setGoalSubject] = useState<SubjectKey>('informatics')
  const [selectedDayKey, setSelectedDayKey] = useState<string | null>(null)
  const [hoveredCell, setHoveredCell] = useState<{
    key: string
    x: number
    y: number
    below: boolean
  } | null>(null)

  const activityData = useMemo(() => {
    const now = new Date()
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12)
    const startYear = today.getMonth() >= 6 ? today.getFullYear() : today.getFullYear() - 1
    const seasonStart = new Date(startYear, 6, 1, 12)
    const seasonEnd = new Date(startYear + 1, 5, 30, 12)

    const gridStart = new Date(seasonStart)
    gridStart.setDate(gridStart.getDate() - gridStart.getDay())

    const gridEnd = new Date(seasonEnd)
    gridEnd.setDate(gridEnd.getDate() + (6 - gridEnd.getDay()))

    const days: ActivityDay[] = []

    // Пока история активности не подключена к API, все показатели равны нулю.
    for (
      const cursor = new Date(gridStart);
      cursor <= gridEnd;
      cursor.setDate(cursor.getDate() + 1)
    ) {
      const date = new Date(cursor)
      const key = dateKey(date)
      const isInSeason = date >= seasonStart && date <= seasonEnd
      const isToday = key === dateKey(today)
      const isFuture = date > today

      const xp = 0
      const solved = 0
      const level = 0
      const exam = isInSeason
        ? examDates.find((item) => item.date === key) ?? null
        : null

      days.push({
        date,
        key,
        solved,
        xp,
        level,
        isToday,
        isInSeason,
        isFuture,
        exam,
      })
    }

    const months = Array.from({ length: 12 }, (_, monthIndex) => {
      const date = new Date(startYear, 6 + monthIndex, 1, 12)
      const offsetDays = Math.round(
        (date.getTime() - gridStart.getTime()) / 86400000,
      )

      return {
        label: date.toLocaleDateString('ru-RU', { month: 'short' }).replace('.', ''),
        column: Math.floor(offsetDays / 7) + 1,
      }
    })

    return {
      days,
      months,
      seasonLabel: `${startYear}/${String(startYear + 1).slice(-2)}`,
    }
  }, [])

  const activityDays = activityData.days
  const today = activityDays.find((day) => day.isToday)!
  const activeDay =
    activityDays.find((day) => day.key === selectedDayKey) ?? today
  const hoveredDay = hoveredCell
    ? activityDays.find((day) => day.key === hoveredCell.key)
    : undefined

  const challenge = challenges[challengeSubject]
  const goal = goals[goalSubject]
  const goalProgress = Math.min(100, Math.round((goal.lastScore / goal.target) * 100))

  const showActivityTooltip = (day: ActivityDay, element: HTMLButtonElement) => {
    const rect = element.getBoundingClientRect()

    setHoveredCell({
      key: day.key,
      x: Math.max(130, Math.min(rect.left + rect.width / 2, window.innerWidth - 130)),
      y: rect.top,
      below: rect.top < 110,
    })
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-heading">
        <div className="home-accent-line" />
        <h1 className="home-title">Твой прогресс</h1>
        <p className="home-description">
          Каждое решённое задание приближает тебя к цели.
        </p>
      </div>

      <div className="dashboard-grid">
        <section className="dashboard-card challenge-card">
          <div className="dashboard-card-heading">
            <div className="dashboard-icon is-red">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m14 7 3-3 3 3-3 3M4 20l8-8M7 5l12 12M5 7l2-2 12 12-2 2Z" />
              </svg>
            </div>
            <div className="dashboard-card-title">
              <span className="dashboard-eyebrow">ЕЖЕДНЕВНОЕ ИСПЫТАНИЕ</span>
              <h2>Челлендж дня</h2>
            </div>
            <span className="dashboard-reward">+ XP</span>
          </div>

          <div className="dashboard-switch" aria-label="Предмет челленджа">
            <span
              className={`dashboard-switch-indicator ${challengeSubject === 'mathematics' ? 'is-right' : ''}`}
              aria-hidden="true"
            />
            <button
              type="button"
              className={challengeSubject === 'informatics' ? 'is-selected' : ''}
              onClick={() => setChallengeSubject('informatics')}
            >
              Информатика
            </button>
            <button
              type="button"
              className={challengeSubject === 'mathematics' ? 'is-selected' : ''}
              onClick={() => setChallengeSubject('mathematics')}
            >
              Математика
            </button>
          </div>

          <div className="challenge-content">
            <span className="challenge-tag">{challenge.tag}</span>
            <h3>{challenge.topic}</h3>
            <p>{challenge.description}</p>
          </div>

          <div className="challenge-footer">
            <span className="dashboard-meta">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01" />
              </svg>
              3 задания
            </span>
            <span className="dashboard-meta is-gold">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <path d="m13 2-3 8h7l-6 12 1-9H6l7-11Z" />
              </svg>
              Бонус XP
            </span>
          </div>

          <Link
            className="dashboard-primary-button"
            to={`/tasks?subject=${challengeSubject}&challenge=daily`}
          >
            Начать челлендж
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </Link>
        </section>

        <section className="dashboard-card goal-card">
          <div className="dashboard-card-heading">
            <div className="dashboard-icon is-gold">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <circle cx="12" cy="12" r="9" />
                <circle cx="12" cy="12" r="5" />
                <circle cx="12" cy="12" r="1" />
                <path d="m15 9 6-6" />
              </svg>
            </div>
            <div className="dashboard-card-title">
              <span className="dashboard-eyebrow">ТВОЯ ЦЕЛЬ</span>
              <h2>Результат ЕГЭ</h2>
            </div>
          </div>

          <div className="dashboard-switch" aria-label="Предмет целевого балла">
            <span
              className={`dashboard-switch-indicator ${goalSubject === 'mathematics' ? 'is-right' : ''}`}
              aria-hidden="true"
            />
            <button
              type="button"
              className={goalSubject === 'informatics' ? 'is-selected' : ''}
              onClick={() => setGoalSubject('informatics')}
            >
              Информатика
            </button>
            <button
              type="button"
              className={goalSubject === 'mathematics' ? 'is-selected' : ''}
              onClick={() => setGoalSubject('mathematics')}
            >
              Математика
            </button>
          </div>

          <div className="goal-score">
            <div>
              <span className="dashboard-eyebrow">Целевой балл</span>
              <div className="goal-target">
                {goal.target}<span> / 100</span>
              </div>
            </div>
            <div className="goal-last-score">
              <span className="dashboard-eyebrow">Последний пробник</span>
              <strong>{goal.lastScore}</strong>
            </div>
          </div>

          <div
            className="goal-progress-track"
            role="progressbar"
            aria-label={`Результат последнего пробника по предмету ${goal.subject}`}
            aria-valuemin={0}
            aria-valuemax={goal.target}
            aria-valuenow={goal.lastScore}
          >
            <div className="goal-progress-fill" style={{ width: `${goalProgress}%` }} />
          </div>

          <div className="goal-progress-caption">
            <span>Последний результат</span>
            <strong>До цели: {Math.max(0, goal.target - goal.lastScore)} баллов</strong>
          </div>

          <Link to="/profile" className="dashboard-text-link">
            Мой план подготовки
            <svg viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h14M13 6l6 6-6 6" />
            </svg>
          </Link>
        </section>

        <section className="dashboard-card activity-card">
          <div className="dashboard-card-heading activity-heading">
            <div className="dashboard-icon is-gold">
              <svg viewBox="0 0 24 24" aria-hidden="true">
                <rect x="3" y="4" width="18" height="17" rx="2" />
                <path d="M16 2v4M8 2v4M3 9h18" />
              </svg>
            </div>
            <div className="dashboard-card-title">
              <h2>Активность</h2>
              <p>Учебный сезон {activityData.seasonLabel} · июль — июнь</p>
            </div>
            <div className="activity-legend">
              <span>Меньше XP</span>
              {activityColors.map((color) => (
                <span
                  key={color}
                  className="activity-legend-cell"
                  style={{ backgroundColor: color }}
                />
              ))}
              <span>Больше</span>
            </div>
          </div>

          <div className="activity-content">
            <div className="activity-grid-wrap">
              <div className="activity-months" aria-hidden="true">
                {activityData.months.map((month, index) => (
                  <span
                    key={`${month.label}-${index}`}
                    style={{ gridColumn: month.column }}
                  >
                    {month.label}
                  </span>
                ))}
              </div>

              <div className="activity-grid" aria-label="Календарь активности за учебный сезон">
                {activityDays.map((day, index) => {
                  const examClass = day.exam
                    ? day.exam.subject === 'mathematics'
                      ? 'is-exam-math'
                      : 'is-exam-informatics'
                    : ''

                  const dayClass = [
                    'activity-cell',
                    day.isToday ? 'is-today' : '',
                    selectedDayKey === day.key ? 'is-selected' : '',
                    !day.isInSeason ? 'is-outside-season' : '',
                    day.isFuture && !day.exam ? 'is-future' : '',
                    examClass,
                  ].filter(Boolean).join(' ')

                  const title = day.exam
                    ? `${formatActivityDate(day.date)} · ${day.solved} заданий · ${day.xp} XP · ${day.exam.title}`
                    : `${formatActivityDate(day.date)} · ${day.solved} заданий · ${day.xp} XP`

                  return (
                    <button
                      key={day.key}
                      type="button"
                      className={dayClass}
                      style={{
                        gridColumn: Math.floor(index / 7) + 1,
                        gridRow: day.date.getDay() + 1,
                        backgroundColor: day.isInSeason
                          ? activityColors[day.level]
                          : 'transparent',
                      }}
                      aria-label={title}
                      disabled={!day.isInSeason || (day.isFuture && !day.exam)}
                      onMouseEnter={(event) => showActivityTooltip(day, event.currentTarget)}
                      onMouseLeave={() => setHoveredCell(null)}
                      onFocus={(event) => showActivityTooltip(day, event.currentTarget)}
                      onBlur={() => setHoveredCell(null)}
                      onClick={() => {
                        setSelectedDayKey(day.key)
                        setHoveredCell(null)
                      }}
                    />
                  )
                })}
              </div>
            </div>

            {hoveredDay && hoveredCell && (
              <div
                className={`activity-hover-tooltip${hoveredCell.below ? ' is-below' : ''}`}
                style={{
                  left: hoveredCell.x,
                  top: hoveredCell.y,
                }}
                role="tooltip"
              >
                <span className="dashboard-eyebrow">
                  {hoveredDay.exam
                    ? 'ДЕНЬ ЕГЭ'
                    : hoveredDay.isToday
                      ? 'СЕГОДНЯ'
                      : 'АКТИВНОСТЬ'}
                </span>

                <strong className="activity-tooltip-date">
                  {formatActivityDate(hoveredDay.date)}
                </strong>

                <div className="activity-tooltip-stat">
                  <span className="activity-tooltip-dot is-red" />
                  {hoveredDay.solved} заданий решено
                </div>

                <div className="activity-tooltip-stat">
                  <span className="activity-tooltip-dot is-gold" />
                  <strong>+{hoveredDay.xp} XP</strong>
                </div>

                {hoveredDay.xp === 0 && !hoveredDay.exam && (
                  <span className="activity-tooltip-empty">
                    Активности не было
                  </span>
                )}

                {hoveredDay.exam && (
                  <span
                    className={`activity-selected-exam ${hoveredDay.exam.subject === 'mathematics' ? 'is-math' : 'is-informatics'}`}
                  >
                    {hoveredDay.exam.title}
                  </span>
                )}
              </div>
            )}

            <div className="activity-exam-legend">
              <span>
                <i className="activity-exam-dot is-math" />
                ЕГЭ по математике
              </span>
              <span>
                <i className="activity-exam-dot is-informatics" />
                ЕГЭ по информатике
              </span>
            </div>

            <div className="activity-details">
              <div className="activity-detail-heading">
                <div>
                  <span className="dashboard-eyebrow">
                    {activeDay.isToday ? 'СЕГОДНЯ' : 'ВЫБРАННЫЙ ДЕНЬ'}
                  </span>
                  <strong className="activity-detail-date">
                    {formatActivityDate(activeDay.date)}
                  </strong>
                </div>

                {!activeDay.isToday && (
                  <button
                    type="button"
                    className="activity-reset-day"
                    onClick={() => setSelectedDayKey(null)}
                  >
                    Сегодня
                  </button>
                )}
              </div>

              <div className="activity-today-stats">
                <div className="activity-today-stat">
                  <span className="activity-stat-icon is-red">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="m5 12 4 4L19 6" />
                    </svg>
                  </span>
                  <div>
                    <strong>{activeDay.solved}</strong>
                    <span>Решено заданий</span>
                  </div>
                </div>

                <div className="activity-today-stat">
                  <span className="activity-stat-icon is-gold">
                    <svg viewBox="0 0 24 24" aria-hidden="true">
                      <path d="m13 2-3 8h7l-6 12 1-9H6l7-11Z" />
                    </svg>
                  </span>
                  <div>
                    <strong className="is-gold">+{activeDay.xp}</strong>
                    <span>Получено XP</span>
                  </div>
                </div>
              </div>

              {activeDay.exam && (
                <div
                  className={`activity-selected-exam ${activeDay.exam.subject === 'mathematics' ? 'is-math' : 'is-informatics'}`}
                >
                  {activeDay.exam.title}
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
