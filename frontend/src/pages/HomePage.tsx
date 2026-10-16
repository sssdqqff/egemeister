import { useAuth } from '../auth/authContext'
import { useMemo, useState } from 'react'
import { Link } from 'react-router'
import {
  Swords,
  ListChecks,
  Zap,
  ArrowRight,
  Target,
  CalendarDays,
  Flame,
  Trophy,
  Check,
} from 'lucide-react'

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

const examDates: ExamMarker[] = [
  { date: '2027-05-27', subject: 'informatics', title: 'ЕГЭ по информатике' },
  { date: '2027-06-01', subject: 'mathematics', title: 'ЕГЭ по математике' },
]

const challenges = {
  informatics: {
    subject: 'Информатика',
    topic: 'Системы счисления',
    description:
      'Реши три задания и проверь, насколько уверенно работаешь с разными основаниями систем счисления.',
    tag: 'ТРЕНАЖЁР · ИНФОРМАТИКА',
  },
  mathematics: {
    subject: 'Математика',
    topic: 'Уравнения',
    description:
      'Реши три задания на уравнения и закрепи навыки решения задач профильного ЕГЭ.',
    tag: 'ТРЕНАЖЁР · МАТЕМАТИКА',
  },
}

const goals = {
  informatics: {
    subject: 'Информатика',
    target: 100,
    scores: [62, 68, 71, 76],
  },
  mathematics: {
    subject: 'Математика',
    target: 80,
    scores: [48, 54, 58, 62],
  },
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
  const { user } = useAuth()
  const [selectedSubject, setSelectedSubject] =
    useState<SubjectKey>('informatics')
  const [selectedDayKey, setSelectedDayKey] = useState<string | null>(null)
  const [hoveredCell, setHoveredCell] = useState<{
    key: string
    x: number
    y: number
    below: boolean
  } | null>(null)

  const activityData = useMemo(() => {
    const now = new Date()
    const today = new Date(
      now.getFullYear(),
      now.getMonth(),
      now.getDate(),
      12,
    )
    const startYear =
      today.getMonth() >= 6
        ? today.getFullYear()
        : today.getFullYear() - 1

    const seasonStart = new Date(startYear, 6, 1, 12)
    const seasonEnd = new Date(startYear + 1, 5, 30, 12)

    const gridStart = new Date(seasonStart)
    gridStart.setDate(gridStart.getDate() - gridStart.getDay())

    const gridEnd = new Date(seasonEnd)
    gridEnd.setDate(gridEnd.getDate() + (6 - gridEnd.getDay()))

    const days: ActivityDay[] = []

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
        label: date
          .toLocaleDateString('ru-RU', { month: 'short' })
          .replace('.', ''),
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

  const challenge = challenges[selectedSubject]
  const goal = goals[selectedSubject]
  const lastScore = goal.scores[goal.scores.length - 1] ?? 0
  const minScore = Math.min(...goal.scores)
  const maxScore = Math.max(...goal.scores)
  const scoreRange = maxScore - minScore || 1

  const chartPoints = goal.scores.map((score, index) => ({
    x: 20 + index * 92,
    y: 82 - ((score - minScore) / scoreRange) * 48,
    score,
    index,
  }))

  const chartPath = chartPoints
    .map((point, index) =>
      `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`,
    )
    .join(' ')

  const showActivityTooltip = (
    day: ActivityDay,
    element: HTMLButtonElement,
  ) => {
    const rect = element.getBoundingClientRect()

    setHoveredCell({
      key: day.key,
      x: Math.max(
        130,
        Math.min(rect.left + rect.width / 2, window.innerWidth - 130),
      ),
      y: rect.top,
      below: rect.top < 110,
    })
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-topline">
        <div className="dashboard-heading">
          <h1 className="home-title">Привет, {user?.first_name ?? 'ученик'}!</h1>
          <p className="home-description">
            Реши одно задание сегодня, чтобы не потерять серию.
          </p>
        </div>

        <div
          className="dashboard-switch dashboard-global-switch"
          aria-label="Выбор предмета"
        >
          <span
            className={`dashboard-switch-indicator ${
              selectedSubject === 'mathematics' ? 'is-right' : ''
            }`}
            aria-hidden="true"
          />
          <button
            type="button"
            className={selectedSubject === 'informatics' ? 'is-selected' : ''}
            aria-pressed={selectedSubject === 'informatics'}
            onClick={() => setSelectedSubject('informatics')}
          >
            Информатика
          </button>
          <button
            type="button"
            className={selectedSubject === 'mathematics' ? 'is-selected' : ''}
            aria-pressed={selectedSubject === 'mathematics'}
            onClick={() => setSelectedSubject('mathematics')}
          >
            Математика
          </button>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="dashboard-card challenge-card">
          <div className="dashboard-card-heading">
            <div className="dashboard-icon is-red">
              <Swords size={22} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <div className="dashboard-card-title">
              <span className="dashboard-eyebrow">ЕЖЕДНЕВНОЕ ИСПЫТАНИЕ</span>
              <h2>Челлендж дня</h2>
            </div>
            <span className="dashboard-reward">+ XP</span>
          </div>

          <div className="challenge-content">
            <span className="challenge-tag">{challenge.tag}</span>
            <h3>{challenge.topic}</h3>
            <p>{challenge.description}</p>
          </div>

          <div className="challenge-footer">
            <span className="dashboard-meta">
              <ListChecks size={16} strokeWidth={1.8} aria-hidden="true" />
              3 задания
            </span>
            <span className="dashboard-meta is-gold">
              <Zap size={16} strokeWidth={1.8} aria-hidden="true" />
              Бонус XP
            </span>
          </div>

          <Link
            className="dashboard-primary-button"
            to={`/tasks?subject=${selectedSubject}&challenge=daily`}
          >
            Начать челлендж
            <ArrowRight size={16} strokeWidth={1.8} aria-hidden="true" />
          </Link>
        </section>

        <section
          className={`dashboard-card goal-card ${
            selectedSubject === 'mathematics' ? 'is-mathematics' : ''
          }`}
        >
          <div className="dashboard-card-heading">
            <div className="dashboard-icon is-gold">
              <Target size={22} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <div className="dashboard-card-title">
              <span className="dashboard-eyebrow">ТВОЯ ЦЕЛЬ</span>
              <h2>ЕГЭ по {goal.subject.toLowerCase()}</h2>
            </div>
          </div>

          <div className="goal-score">
            <div>
              <span className="dashboard-eyebrow">ЦЕЛЕВОЙ БАЛЛ</span>
              <div className="goal-target">
                {goal.target}
                <span> / 100</span>
              </div>
            </div>
            <div className="goal-last-score">
              <span className="dashboard-eyebrow">ПОСЛЕДНИЙ ПРОБНИК</span>
              <strong>{lastScore}</strong>
            </div>
          </div>

          <div className="goal-chart">
            <div className="goal-chart-heading">
              <span className="dashboard-eyebrow">ДИНАМИКА ПРОБНИКОВ</span>
              <span className="goal-chart-subject">{goal.subject}</span>
            </div>

            <svg
              className="goal-chart-svg"
              viewBox="0 0 320 120"
              role="img"
              aria-label={`Последние результаты по предмету ${goal.subject}: ${goal.scores.join(', ')} баллов`}
            >
              <line
                x1="12"
                y1="96"
                x2="308"
                y2="96"
                className="goal-chart-axis"
              />
              <path d={chartPath} className="goal-chart-line" />

              {chartPoints.map((point) => (
                <g key={`${selectedSubject}-${point.index}`}>
                  <circle
                    cx={point.x}
                    cy={point.y}
                    r="4"
                    className="goal-chart-point"
                  />
                  <text
                    x={point.x}
                    y={point.y - 11}
                    className={`goal-chart-score ${
                      point.index === chartPoints.length - 1 ? 'is-latest' : ''
                    }`}
                    textAnchor="middle"
                  >
                    {point.score}
                  </text>
                  <text
                    x={point.x}
                    y="113"
                    className="goal-chart-index"
                    textAnchor="middle"
                  >
                    {point.index + 1}
                  </text>
                </g>
              ))}
            </svg>
          </div>

          <div className="goal-progress-caption">
            <span>Последний результат</span>
            <strong>
              {lastScore >= goal.target
                ? 'Цель достигнута'
                : `До цели: ${goal.target - lastScore} баллов`}
            </strong>
          </div>

          <Link to="/profile" className="dashboard-text-link">
            Мой план подготовки
            <ArrowRight size={16} strokeWidth={1.8} aria-hidden="true" />
          </Link>
        </section>

        <section className="dashboard-card activity-card">
          <div className="dashboard-card-heading activity-heading">
            <div className="dashboard-icon is-gold">
              <CalendarDays size={22} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <div className="dashboard-card-title">
              <h2>Активность</h2>
              <p>Учебный сезон {activityData.seasonLabel} · июль — июнь</p>
            </div>
          </div>

          <div className="activity-content">
            <div className="activity-streaks">
              <div className="activity-streak activity-streak-current">
                <span className="activity-streak-icon is-current">
                  <Flame size={20} strokeWidth={1.8} aria-hidden="true" />
                </span>
                <div className="activity-streak-info">
                  <span className="activity-streak-label">Текущая серия</span>
                  <strong>5 <span>дней</span></strong>
                </div>
              </div>

              <div className="activity-streak activity-streak-record">
                <span className="activity-streak-icon is-record">
                  <Trophy size={20} strokeWidth={1.8} aria-hidden="true" />
                </span>
                <div className="activity-streak-info">
                  <span className="activity-streak-label">Личный рекорд</span>
                  <strong>12 <span>дней</span></strong>
                </div>
              </div>
            </div>

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

              <div
                className="activity-grid"
                aria-label="Календарь активности за учебный сезон"
              >
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
                  ]
                    .filter(Boolean)
                    .join(' ')

                  const title = day.exam
                    ? `${formatActivityDate(day.date)} · ${day.exam.title} · ${day.solved} заданий · ${day.xp} XP`
                    : `${formatActivityDate(day.date)} · ${day.solved} заданий · ${day.xp} XP`

                  return (
                    <button
                      key={day.key}
                      type="button"
                      className={dayClass}
                      style={{
                        gridColumn: Math.floor(index / 7) + 1,
                        gridRow: day.date.getDay() + 1,
                        backgroundColor: day.exam
                          ? day.exam.subject === 'informatics'
                            ? '#2868A5'
                            : '#A3D977'
                          : day.isInSeason
                            ? activityColors[day.level]
                            : 'transparent',
                      }}
                      aria-label={title}
                      disabled={!day.isInSeason || (day.isFuture && !day.exam)}
                      onMouseEnter={(event) =>
                        showActivityTooltip(day, event.currentTarget)
                      }
                      onMouseLeave={() => setHoveredCell(null)}
                      onFocus={(event) =>
                        showActivityTooltip(day, event.currentTarget)
                      }
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
                className={`activity-hover-tooltip${
                  hoveredCell.below ? ' is-below' : ''
                }`}
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

                {hoveredDay.exam && (
                  <span
                    className={`activity-selected-exam ${
                      hoveredDay.exam.subject === 'mathematics'
                        ? 'is-math'
                        : 'is-informatics'
                    }`}
                  >
                    {hoveredDay.exam.title}
                  </span>
                )}

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
              </div>
            )}

            <div className="activity-bottom-legend">
              <div className="activity-exam-legend">
                <span>
                  <i className="activity-exam-dot is-informatics" />
                  ЕГЭ по информатике
                </span>
                <span>
                  <i className="activity-exam-dot is-math" />
                  ЕГЭ по математике
                </span>
              </div>

              <div className="activity-legend">
                <span>Меньше</span>
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
                    <Check size={18} strokeWidth={2} aria-hidden="true" />
                  </span>
                  <div>
                    <strong>{activeDay.solved}</strong>
                    <span>Решено заданий</span>
                  </div>
                </div>

                <div className="activity-today-stat">
                  <span className="activity-stat-icon is-gold">
                    <Zap size={18} strokeWidth={1.8} aria-hidden="true" />
                  </span>
                  <div>
                    <strong className="is-gold">+{activeDay.xp}</strong>
                    <span>Получено XP</span>
                  </div>
                </div>
              </div>

              {activeDay.exam && (
                <div
                  className={`activity-selected-exam ${
                    activeDay.exam.subject === 'mathematics'
                      ? 'is-math'
                      : 'is-informatics'
                  }`}
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
