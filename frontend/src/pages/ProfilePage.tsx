import { useState } from 'react'
import { Link } from 'react-router'
import {
  ArrowRight,
  ArrowUpRight,
  ChevronDown,
  CircleCheck,
  Compass,
  FileText,
  Flame,
  Target,
  TrendingDown,
  TrendingUp,
  UserRound,
} from 'lucide-react'
import { useAuth } from '../auth/authContext'

type SubjectKey = 'informatics' | 'mathematics'

type TaskStat = {
  number: number
  accuracy: number
}

type ExamAttempt = {
  id: number
  date: string
  score: number
  previousScore: number | null
  mistakes: number[]
}

const profile = {
  level: 12,
  totalXp: 4850,
  xpInLevel: 720,
  xpForNextLevel: 1000,
  streak: 7,
  solvedTasks: 1248,
  accuracy: 84,
  completedExams: 18,
  averageScore: 76,
}

const taskStats: Record<SubjectKey, TaskStat[]> = {
  informatics: [
    96, 71, 58, 94, 63, 48, 91, 66, 73, 54, 81, 69, 95, 44,
    62, 77, 39, 92, 86, 57, 33, 74, 41, 28, 36, 31, 22,
  ].map((accuracy, index) => ({ number: index + 1, accuracy })),
  mathematics: [
    92, 76, 68, 88, 57, 83, 71, 49, 64, 79, 53, 90, 43, 61,
    74, 38, 56, 32, 46,
  ].map((accuracy, index) => ({ number: index + 1, accuracy })),
}

const examHistory: Record<SubjectKey, ExamAttempt[]> = {
  informatics: [
    { id: 3, date: '12 октября 2026', score: 78, previousScore: 72, mistakes: [14, 21, 24, 27] },
    { id: 2, date: '5 октября 2026', score: 72, previousScore: 68, mistakes: [5, 14, 17, 25, 27] },
    { id: 1, date: '28 сентября 2026', score: 68, previousScore: null, mistakes: [3, 9, 17, 21, 24, 26] },
  ],
  mathematics: [
    { id: 3, date: '13 октября 2026', score: 64, previousScore: 59, mistakes: [5, 8, 13, 16] },
    { id: 2, date: '6 октября 2026', score: 59, previousScore: 55, mistakes: [8, 13, 16, 19] },
    { id: 1, date: '29 сентября 2026', score: 55, previousScore: null, mistakes: [5, 8, 12, 16, 19] },
  ],
}

const subjectNames: Record<SubjectKey, string> = {
  informatics: 'Информатика',
  mathematics: 'Математика',
}

function StatIcon({ type }: { type: 'tasks' | 'accuracy' | 'exams' | 'score' }) {
  const iconProps = { size: 20, strokeWidth: 1.7, 'aria-hidden': true as const }

  if (type === 'tasks') return <CircleCheck {...iconProps} />
  if (type === 'accuracy') return <Target {...iconProps} />
  if (type === 'exams') return <FileText {...iconProps} />
  return <TrendingUp {...iconProps} />
}

function formatNumber(value: number) {
  return value.toLocaleString('ru-RU')
}

export default function ProfilePage() {
  const { user } = useAuth()
  const [selectedSubject, setSelectedSubject] = useState<SubjectKey>('informatics')
  const [expandedExam, setExpandedExam] = useState<number | null>(null)

  const tasks = taskStats[selectedSubject]
  const strengths = [...tasks].sort((a, b) => b.accuracy - a.accuracy).slice(0, 5)
  const weaknesses = [...tasks].sort((a, b) => a.accuracy - b.accuracy).slice(0, 5)
  const attempts = examHistory[selectedSubject]
  const xpRemaining = Math.max(0, profile.xpForNextLevel - profile.xpInLevel)
  const xpPercent = Math.min(100, Math.round((profile.xpInLevel / profile.xpForNextLevel) * 100))
  const subjectSlug = selectedSubject

  const renderTaskList = (items: TaskStat[], type: 'strength' | 'weakness') => (
    <div className="profile-task-list">
      {items.map((task) => (
        <Link
          key={task.number}
          to={`/tasks/${subjectSlug}/topics?number=${task.number}`}
          className="profile-task-row"
        >
          <span className="profile-task-number">{task.number}</span>
          <span className="profile-task-info">
            <span className="profile-task-name">Задание №{task.number}</span>
            <span className="profile-mini-track">
              <span
                className={`profile-mini-fill ${type}`}
                style={{ width: `${task.accuracy}%` }}
              />
            </span>
          </span>
          <strong className={`profile-task-percent ${type}`}>{task.accuracy}%</strong>
        </Link>
      ))}
    </div>
  )

  return (
    <main className="profile-page">
      <section className="profile-hero">
        <div className="profile-user-row">
          <div className="profile-avatar">
            <UserRound size={27} strokeWidth={1.6} aria-hidden="true" />
          </div>
          <div className="profile-identity">
            <span className="profile-eyebrow">ПРОФИЛЬ УЧЕНИКА</span>
            <h1>{user?.first_name ?? 'Ученик'}</h1>
            <span className="profile-level">LVL <strong>{profile.level}</strong></span>
          </div>
          <div className="profile-streak">
            <div className="profile-streak-value">
              <Flame size={21} strokeWidth={1.8} aria-hidden="true" />
              <strong>{profile.streak}</strong>
            </div>
            <span>дней подряд</span>
          </div>
        </div>

        <div className="profile-xp-row">
          <div className="profile-total-xp">
            <span>Всего опыта</span>
            <strong>{formatNumber(profile.totalXp)} XP</strong>
          </div>
          <div className="profile-xp-progress">
            <div className="profile-xp-heading">
              <span>Прогресс до LVL {profile.level + 1}</span>
              <strong>{xpPercent}%</strong>
            </div>
            <div
              className="profile-xp-track"
              role="progressbar"
              aria-label="Опыт до следующего уровня"
              aria-valuemin={0}
              aria-valuemax={profile.xpForNextLevel}
              aria-valuenow={profile.xpInLevel}
            >
              <div className="profile-xp-fill" style={{ width: `${xpPercent}%` }} />
            </div>
            <div className="profile-xp-details">
              <span>{formatNumber(profile.xpInLevel)} / {formatNumber(profile.xpForNextLevel)} XP</span>
              <span>Ещё {formatNumber(xpRemaining)} XP</span>
            </div>
          </div>
        </div>

        <div className="profile-overview-stats">
          <article className="profile-overview-stat">
            <span className="profile-stat-icon is-gold"><StatIcon type="tasks" /></span>
            <strong>{formatNumber(profile.solvedTasks)}</strong>
            <span>Решено заданий</span>
          </article>
          <article className="profile-overview-stat">
            <span className="profile-stat-icon is-red"><StatIcon type="exams" /></span>
            <strong>{profile.completedExams}</strong>
            <span>Пробников пройдено</span>
          </article>
          <article className="profile-overview-stat">
            <span className="profile-stat-icon is-gold"><StatIcon type="score" /></span>
            <strong>{profile.averageScore}</strong>
            <span>Средний балл</span>
          </article>
          <article className="profile-overview-stat">
            <span className="profile-stat-icon is-red"><StatIcon type="accuracy" /></span>
            <strong>{profile.accuracy}%</strong>
            <span>Точность ответов</span>
          </article>
        </div>
      </section>

      <div className="profile-subject-switch-wrap">
        <div className="dashboard-switch dashboard-global-switch profile-subject-switch" aria-label="Выбор предмета">
          <span className={`dashboard-switch-indicator ${selectedSubject === 'mathematics' ? 'is-right' : ''}`} aria-hidden="true" />
          <button
            type="button"
            className={selectedSubject === 'informatics' ? 'is-selected' : ''}
            aria-pressed={selectedSubject === 'informatics'}
            onClick={() => {
              setSelectedSubject('informatics')
              setExpandedExam(null)
            }}
          >
            Информатика
          </button>
          <button
            type="button"
            className={selectedSubject === 'mathematics' ? 'is-selected' : ''}
            aria-pressed={selectedSubject === 'mathematics'}
            onClick={() => {
              setSelectedSubject('mathematics')
              setExpandedExam(null)
            }}
          >
            Математика
          </button>
        </div>
        <span className="profile-subject-caption">Аналитика: {subjectNames[selectedSubject].toLowerCase()}</span>
      </div>

      <section className="profile-section">
        <div className="profile-section-heading">
          <div>
            <span className="profile-eyebrow">АНАЛИЗ РЕЗУЛЬТАТОВ</span>
            <h2>Сильные и слабые стороны</h2>
          </div>
          <Link to={`/tasks/${subjectSlug}/topics`} className="profile-section-link">
            Все задания <ArrowUpRight size={15} strokeWidth={1.8} />
          </Link>
        </div>
        <div className="profile-strengths-grid">
          <article className="profile-analysis-card">
            <div className="profile-analysis-heading">
              <span className="profile-analysis-mark is-strong">
                <TrendingUp size={20} strokeWidth={1.8} aria-hidden="true" />
              </span>
              <div><h3>Сильные стороны</h3><p>Лучше всего получается</p></div>
            </div>
            {renderTaskList(strengths, 'strength')}
          </article>
          <article className="profile-analysis-card">
            <div className="profile-analysis-heading">
              <span className="profile-analysis-mark is-weak">
                <TrendingDown size={20} strokeWidth={1.8} aria-hidden="true" />
              </span>
              <div><h3>Зоны роста</h3><p>Темы, которым стоит уделить время</p></div>
            </div>
            {renderTaskList(weaknesses, 'weakness')}
          </article>
        </div>
      </section>

      <section className="profile-section">
        <div className="profile-section-heading">
          <div>
            <span className="profile-eyebrow">ТВОЙ ПРОГРЕСС</span>
            <h2>Карта освоения</h2>
          </div>
          <span className="profile-map-count">{tasks.length} заданий</span>
        </div>
        <div className="profile-mastery-card">
          <div className="profile-mastery-legend">
            <span><i className="is-low" /> Нужно подтянуть</span>
            <span><i className="is-medium" /> В процессе</span>
            <span><i className="is-high" /> Освоено</span>
          </div>
          <div className="profile-mastery-grid">
            {tasks.map((task) => {
              const masteryClass = task.accuracy >= 80 ? 'is-high' : task.accuracy >= 55 ? 'is-medium' : 'is-low'
              return (
                <Link
                  key={task.number}
                  to={`/tasks/${subjectSlug}/topics?number=${task.number}`}
                  className={`profile-mastery-cell ${masteryClass}`}
                  title={`Задание №${task.number}: ${task.accuracy}% правильных ответов`}
                >
                  <strong>{task.number}</strong>
                  <span>{task.accuracy}%</span>
                </Link>
              )
            })}
          </div>
          <p className="profile-mastery-note">Нажми на номер, чтобы перейти к практике по этому заданию.</p>
        </div>
      </section>

      <section className="profile-section">
        <div className="profile-section-heading">
          <div>
            <span className="profile-eyebrow">ИСТОРИЯ РЕЗУЛЬТАТОВ</span>
            <h2>Последние пробники</h2>
          </div>
          <span className="profile-map-count">{attempts.length} последних</span>
        </div>
        <div className="profile-exam-history">
          {attempts.map((attempt) => {
            const difference = attempt.previousScore === null ? null : attempt.score - attempt.previousScore
            const isExpanded = expandedExam === attempt.id
            return (
              <article className={`profile-exam-item ${isExpanded ? 'is-expanded' : ''}`} key={`${selectedSubject}-${attempt.id}`}>
                <button
                  type="button"
                  className="profile-exam-summary"
                  onClick={() => setExpandedExam(isExpanded ? null : attempt.id)}
                  aria-expanded={isExpanded}
                >
                  <span className="profile-exam-icon"><StatIcon type="exams" /></span>
                  <span className="profile-exam-main">
                    <strong>Пробник по {subjectNames[selectedSubject].toLowerCase()}</strong>
                    <span>{attempt.date}</span>
                  </span>
                  <span className="profile-exam-score">
                    <strong>{attempt.score}</strong>
                    <span>из 100</span>
                  </span>
                  <span className={`profile-exam-change ${difference === null ? 'is-neutral' : difference >= 0 ? 'is-positive' : 'is-negative'}`}>
                    {difference === null ? 'Первый' : `${difference > 0 ? '+' : ''}${difference}`}
                  </span>
                  <span className="profile-exam-chevron">
                    <ChevronDown
                      size={18}
                      strokeWidth={1.8}
                      aria-hidden="true"
                      style={{ transform: isExpanded ? 'rotate(180deg)' : undefined }}
                    />
                  </span>
                </button>
                {isExpanded && (
                  <div className="profile-exam-details">
                    <div className="profile-exam-detail-stats">
                      <span>Ошибок по номерам</span>
                      <strong>{attempt.mistakes.length}</strong>
                    </div>
                    <div className="profile-mistake-tags">
                      {attempt.mistakes.map((number) => (
                        <Link key={number} to={`/tasks/${subjectSlug}/topics?number=${number}`} className="profile-mistake-tag">
                          №{number}
                        </Link>
                      ))}
                    </div>
                    <Link to={`/tasks/${subjectSlug}/topics`} className="profile-practice-mistakes">
                      Потренировать ошибки <ArrowRight size={15} strokeWidth={1.8} />
                    </Link>
                  </div>
                )}
              </article>
            )
          })}
        </div>
      </section>
    </main>
  )
}
