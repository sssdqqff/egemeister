import type { PrototypeSpec, TopicSpec } from './shared'

const SUBSCRIPT: Record<number, string> = { 2: '₂', 3: '₃', 5: '₅' }

const probabilityTickets: PrototypeSpec = {
  code: 'm4-classic',
  name: 'Классическое определение вероятности',
  description: 'Отношение числа благоприятных исходов к общему числу исходов.',
  hint: 'Вероятность = число благоприятных исходов / число всех исходов.',
  count: 7,
  make(rng) {
    const total = rng.pick([20, 25, 40, 50])
    const marked = rng.int(2, total - 2)
    const answer = (total - marked) / total
    return {
      difficulty: 'easy',
      condition: `В сборнике билетов по биологии всего ${total} билетов, в ${marked} из них встречается вопрос по ботанике. Найдите вероятность того, что в случайно выбранном на экзамене билете школьнику не достанется вопроса по ботанике.`,
      answer: String(answer),
      solution: `Благоприятных билетов ${total} − ${marked} = ${total - marked}. Вероятность: ${total - marked} / ${total} = ${answer}.`,
    }
  },
}

const exponential: PrototypeSpec = {
  code: 'm6-exp',
  name: 'Показательные уравнения',
  description: 'Уравнения вида aᶠ⁽ˣ⁾ = b, сводимые к равенству показателей.',
  hint: 'Представьте правую часть как степень того же основания и приравняйте показатели.',
  count: 6,
  make(rng) {
    const base = rng.pick([2, 3, 5])
    const power = rng.int(2, 4)
    const shift = rng.int(-9, 9)
    const sign = shift >= 0 ? '−' : '+'
    return {
      difficulty: 'easy',
      condition: `Найдите корень уравнения ${base}^(x ${sign} ${Math.abs(shift)}) = ${base ** power}.`,
      answer: String(shift + power),
      solution: `${base ** power} = ${base}^${power}, значит, x ${sign} ${Math.abs(shift)} = ${power}, x = ${shift + power}.`,
    }
  },
}

const logarithmic: PrototypeSpec = {
  code: 'm6-log',
  name: 'Логарифмические уравнения',
  description: 'Уравнения вида logₐ(x + b) = c.',
  hint: 'По определению логарифма аргумент равен основанию в степени значения логарифма.',
  count: 6,
  make(rng) {
    const base = rng.pick([2, 3])
    const value = rng.int(2, 5)
    const shift = rng.int(-9, 9)
    const sign = shift >= 0 ? '+' : '−'
    const answer = base ** value - shift
    return {
      difficulty: 'easy',
      condition: `Найдите корень уравнения log${SUBSCRIPT[base]}(x ${sign} ${Math.abs(shift)}) = ${value}.`,
      answer: String(answer),
      solution: `x ${sign} ${Math.abs(shift)} = ${base}^${value} = ${base ** value}, откуда x = ${answer}.`,
    }
  },
}

const irrational: PrototypeSpec = {
  code: 'm6-sqrt',
  name: 'Иррациональные уравнения',
  description: 'Уравнения с квадратным корнем от линейного выражения.',
  hint: 'Возведите обе части в квадрат — правая часть неотрицательна, поэтому посторонних корней не будет.',
  count: 6,
  make(rng) {
    const value = rng.int(2, 9)
    const c = rng.int(value * value - 20, value * value + 30)
    return {
      difficulty: 'easy',
      condition: `Найдите корень уравнения √(${c} − x) = ${value}.`,
      answer: String(c - value * value),
      solution: `${c} − x = ${value * value}, x = ${c - value * value}.`,
    }
  },
}

const empty = (number: number, name: string, slug: string, description: string): TopicSpec => ({
  number,
  name,
  slug,
  description,
  prototypes: [],
})

export const MATH_TOPICS: TopicSpec[] = [
  empty(1, 'Планиметрия', 'planimetry', 'Вычисление длин, углов и площадей плоских фигур.'),
  empty(2, 'Векторы', 'vectors', 'Координаты, длина и скалярное произведение векторов.'),
  empty(3, 'Стереометрия', 'stereometry', 'Объёмы и площади поверхностей многогранников и тел вращения.'),
  {
    number: 4,
    name: 'Теория вероятностей',
    slug: 'probability',
    description: 'Классическое определение вероятности.',
    prototypes: [probabilityTickets],
  },
  empty(5, 'Сложные события', 'probability-advanced', 'Независимые события, условная вероятность.'),
  {
    number: 6,
    name: 'Простейшие уравнения',
    slug: 'equations',
    description: 'Показательные, логарифмические и иррациональные уравнения.',
    prototypes: [exponential, logarithmic, irrational],
  },
  empty(7, 'Вычисления и преобразования', 'expressions', 'Преобразование числовых и буквенных выражений.'),
  empty(8, 'Производная и первообразная', 'derivative', 'Геометрический и физический смысл производной.'),
  empty(9, 'Прикладные задачи', 'applied', 'Задачи с физическим и экономическим содержанием.'),
  empty(10, 'Текстовые задачи', 'word-problems', 'Движение, работа, смеси и проценты.'),
  empty(11, 'Графики функций', 'graphs', 'Определение параметров функции по её графику.'),
  empty(12, 'Наибольшее и наименьшее значение', 'extremum', 'Исследование функции с помощью производной.'),
  empty(13, 'Уравнения', 'equations-advanced', 'Тригонометрические, показательные и логарифмические уравнения с отбором корней.'),
  empty(14, 'Стереометрическая задача', 'stereometry-proof', 'Доказательство и вычисление в пространстве.'),
  empty(15, 'Неравенства', 'inequalities', 'Показательные и логарифмические неравенства.'),
  empty(16, 'Финансовая математика', 'finance', 'Кредиты и вклады.'),
  empty(17, 'Планиметрическая задача', 'planimetry-proof', 'Доказательство и вычисление на плоскости.'),
  empty(18, 'Задача с параметром', 'parameters', 'Уравнения и системы с параметром.'),
  empty(19, 'Теория чисел', 'number-theory', 'Свойства целых чисел.'),
]
