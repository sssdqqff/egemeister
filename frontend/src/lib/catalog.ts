import type { Catalog } from '../hooks/useData'
import type { Attempt, Prototype, Subject, Task, Topic } from '../types'

export function tasksOfSubject(catalog: Catalog, subjectId: number): Task[] {
  const topicIds = new Set(catalog.topics.filter((t) => t.subject_id === subjectId).map((t) => t.id))
  return catalog.tasks.filter((task) => topicIds.has(task.topic_id))
}

export function topicsOfSubject(catalog: Catalog, subjectId: number): Topic[] {
  return catalog.topics.filter((t) => t.subject_id === subjectId)
}

export function tasksOfTopic(catalog: Catalog, topicId: number): Task[] {
  return catalog.tasks.filter((task) => task.topic_id === topicId)
}

/** У прототипа в API нет topic_id — связь восстанавливается через задачи. */
export function prototypesOfTopic(catalog: Catalog, topicId: number): Prototype[] {
  const ids = new Set(tasksOfTopic(catalog, topicId).map((task) => task.prototype_id))
  return catalog.prototypes.filter((p) => ids.has(p.id))
}

export interface TaskLocation {
  task: Task
  topic: Topic
  subject: Subject
}

export function locateTask(catalog: Catalog, taskId: number): TaskLocation | null {
  const task = catalog.tasks.find((t) => t.id === taskId)
  if (!task) return null
  const topic = catalog.topics.find((t) => t.id === task.topic_id)
  if (!topic) return null
  const subject = catalog.subjects.find((s) => s.id === topic.subject_id)
  if (!subject) return null
  return { task, topic, subject }
}

export function lastPracticed(catalog: Catalog, attempts: Attempt[] | undefined): TaskLocation | null {
  if (!attempts?.length) return null
  const latest = attempts.reduce((a, b) => (b.id > a.id ? b : a))
  return locateTask(catalog, latest.task_id)
}

export function topicPath(subjectId: number, topicNumber: number): string {
  return `/subjects/${subjectId}/tasks/${topicNumber}`
}
