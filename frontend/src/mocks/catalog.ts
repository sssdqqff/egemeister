import type { Prototype, Subject, Task, Topic } from '../types'
import { INFORMATICS_TOPICS } from './generators/informatics'
import { MATH_TOPICS } from './generators/math'
import { createRng, type SubjectSpec } from './generators/shared'

const SUBJECT_SPECS: SubjectSpec[] = [
  {
    id: 1,
    name: 'Информатика',
    slug: 'informatics',
    description: 'ЕГЭ по информатике и ИКТ: 27 заданий, компьютерная форма экзамена.',
    topics: INFORMATICS_TOPICS,
  },
  {
    id: 2,
    name: 'Профильная математика',
    slug: 'math',
    description: 'ЕГЭ по математике профильного уровня: 19 заданий с кратким и развёрнутым ответом.',
    topics: MATH_TOPICS,
  },
]

export interface DemoCatalog {
  subjects: Subject[]
  topics: Topic[]
  prototypes: Prototype[]
  tasks: Task[]
  /** Ответы хранятся отдельно и никогда не отдаются UI — как и в настоящем API. */
  answers: Map<number, string>
}

function buildCatalog(): DemoCatalog {
  const subjects: Subject[] = []
  const topics: Topic[] = []
  const prototypes: Prototype[] = []
  const tasks: Task[] = []
  const answers = new Map<number, string>()
  let prototypeId = 1
  let taskId = 1001

  for (const subject of SUBJECT_SPECS) {
    subjects.push({
      id: subject.id,
      name: subject.name,
      slug: subject.slug,
      description: subject.description,
      is_active: true,
    })

    for (const topic of subject.topics) {
      const topicId = subject.id * 100 + topic.number
      topics.push({
        id: topicId,
        number: topic.number,
        name: topic.name,
        slug: topic.slug,
        description: topic.description,
        is_active: true,
        subject_id: subject.id,
      })

      for (const spec of topic.prototypes) {
        const id = prototypeId++
        prototypes.push({
          id,
          name: spec.name,
          code: spec.code,
          description: spec.description,
          exam_number: topic.number,
          is_active: true,
        })
        const rng = createRng(id * 7919)
        const seen = new Set<string>()
        let guard = 0
        while (seen.size < spec.count && guard < spec.count * 20) {
          guard += 1
          const generated = spec.make(rng)
          if (seen.has(generated.condition)) continue
          seen.add(generated.condition)
          const tid = taskId++
          tasks.push({
            id: tid,
            condition: generated.condition,
            difficulty: generated.difficulty,
            is_active: true,
            topic_id: topicId,
            prototype_id: id,
            hint: spec.hint,
            solution: generated.solution,
          })
          answers.set(tid, generated.answer)
        }
      }
    }
  }

  return { subjects, topics, prototypes, tasks, answers }
}

export const demoCatalog = buildCatalog()
