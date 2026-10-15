import type { Difficulty } from '../../types'
import { countChar, lcm, VOWELS, type PrototypeSpec, type Rng, type TopicSpec } from './shared'

const ones = (s: string) => countChar(s, '1')

/* ---------- Задание 5 ---------- */

function parityTwice(n: number): number {
  let s = n.toString(2)
  s += String(ones(s) % 2)
  s += String(ones(s) % 2)
  return parseInt(s, 2)
}

function wrapByParity(n: number): number {
  const s = n.toString(2)
  return parseInt(ones(s) % 2 === 0 ? `10${s}0` : `11${s}1`, 2)
}

const task5MinR: PrototypeSpec = {
  code: '5-parity',
  name: 'Дописывание битов чётности',
  description: 'К двоичной записи дважды дописывается остаток суммы цифр по модулю 2.',
  hint: 'Переберите N по возрастанию, для каждого постройте R и найдите первое значение, превышающее порог.',
  count: 6,
  make(rng) {
    const k = rng.int(60, 420)
    let best = Infinity
    let bestN = 0
    for (let n = 1; n < 2000; n += 1) {
      const r = parityTwice(n)
      if (r > k && r < best) {
        best = r
        bestN = n
      }
    }
    return {
      difficulty: 'easy',
      condition: `На вход алгоритма подаётся натуральное число N. Алгоритм строит по нему новое число R следующим образом.\n1. Строится двоичная запись числа N.\n2. К этой записи дописываются справа ещё два разряда по правилу:\n   а) складываются все цифры двоичной записи, остаток от деления суммы на 2 дописывается в конец числа (справа);\n   б) над этой записью производятся те же действия — справа дописывается остаток от деления суммы цифр на 2.\nПолученная таким образом запись является двоичной записью искомого числа R.\n\nУкажите минимальное число R, которое превышает ${k} и может являться результатом работы алгоритма. В ответе это число запишите в десятичной системе.`,
      answer: String(best),
      solution: `Перебираем N = 1, 2, 3, … и вычисляем R. Первое R > ${k} получается при N = ${bestN}: двоичная запись ${bestN.toString(2)} → ${best.toString(2)}, то есть R = ${best}.`,
    }
  },
}

const task5MinN: PrototypeSpec = {
  code: '5-wrap',
  name: 'Обрамление двоичной записи',
  description: 'Запись дополняется слева и справа в зависимости от чётности суммы цифр.',
  hint: 'Значение R растёт вместе с N не строго — проверяйте каждое N, а не только соседние с границей.',
  count: 6,
  make(rng) {
    const k = rng.int(150, 900)
    let n = 1
    while (wrapByParity(n) <= k) n += 1
    const r = wrapByParity(n)
    return {
      difficulty: 'medium',
      condition: `На вход алгоритма подаётся натуральное число N. Алгоритм строит по нему новое число R следующим образом.\n1. Строится двоичная запись числа N.\n2. Если сумма цифр двоичной записи чётная, то к этой записи справа дописывается 0, а слева — 10.\n3. Если сумма цифр нечётная, то справа дописывается 1, а слева — 11.\nПолученная запись является двоичной записью числа R.\n\nУкажите минимальное число N, после обработки которого получается число R, большее ${k}. В ответе это число запишите в десятичной системе.`,
      answer: String(n),
      solution: `Для N = ${n} двоичная запись ${n.toString(2)}, сумма цифр ${ones(n.toString(2))} — ${ones(n.toString(2)) % 2 === 0 ? 'чётная' : 'нечётная'}. Получаем ${r.toString(2)} = ${r} > ${k}, а для всех меньших N результат не превышает ${k}.`,
    }
  },
}

/* ---------- Задание 7 ---------- */

const task7Image: PrototypeSpec = {
  code: '7-raster',
  name: 'Растровые изображения',
  description: 'Глубина цвета и размер палитры по объёму файла.',
  hint: 'Найдите, сколько бит приходится на один пиксель: объём в битах делим на число пикселей и округляем вниз.',
  count: 6,
  make(rng) {
    const w = rng.pick([640, 800, 1024, 1280, 1600])
    const h = rng.pick([480, 600, 768, 1024])
    const targetBits = rng.int(2, 16)
    const minKb = Math.ceil((targetBits * w * h) / 8192)
    const v = minKb + rng.int(0, Math.floor(minKb * 0.08))
    const bits = Math.floor((v * 8192) / (w * h))
    const colors = 2 ** bits
    return {
      difficulty: bits > 10 ? 'medium' : 'easy',
      condition: `Автоматическая камера производит растровые изображения размером ${w}×${h} пикселей. Для кодирования цвета каждого пикселя используется одинаковое количество бит, коды пикселей записываются в файл один за другим без промежутков. Объём файла с изображением не может превышать ${v} Кбайт без учёта размера заголовка файла.\n\nКакое максимальное количество цветов можно использовать в палитре?`,
      answer: String(colors),
      solution: `Пикселей: ${w}·${h} = ${w * h}. Доступно ${v}·8192 = ${v * 8192} бит. На пиксель: ⌊${v * 8192} / ${w * h}⌋ = ${bits} бит. Цветов: 2^${bits} = ${colors}.`,
    }
  },
}

const task7Sound: PrototypeSpec = {
  code: '7-sound',
  name: 'Звукозапись',
  description: 'Объём звукового файла по частоте, разрешению и числу каналов.',
  hint: 'Объём = частота · разрешение · каналы · время. Не забудьте перевести минуты в секунды, а биты — в мегабайты.',
  count: 6,
  make(rng) {
    const channels = rng.pick([
      [1, 'одноканальная (моно)'],
      [2, 'двухканальная (стерео)'],
      [4, 'четырёхканальная (квадро)'],
    ] as const)
    const freq = rng.pick([16, 22, 32, 44, 48])
    const depth = rng.pick([16, 24, 32])
    const minutes = rng.int(1, 6)
    const bits = freq * 1000 * depth * channels[0] * minutes * 60
    const mb = Math.round(bits / 8 / 2 ** 20)
    return {
      difficulty: 'easy',
      condition: `Производится ${channels[1]} звукозапись с частотой дискретизации ${freq} кГц и ${depth}-битным разрешением. Запись длится ${minutes} мин, её результаты записываются в файл, сжатие данных не производится.\n\nОпределите размер полученного файла в Мбайтах. В ответе запишите ближайшее к размеру файла целое число.`,
      answer: String(mb),
      solution: `${freq}000 · ${depth} · ${channels[0]} · ${minutes * 60} = ${bits} бит = ${(bits / 8 / 2 ** 20).toFixed(2)} Мбайт ≈ ${mb}.`,
    }
  },
}

/* ---------- Задание 8 ---------- */

const task8Repeat: PrototypeSpec = {
  code: '8-repeat',
  name: 'Слова с повторениями',
  description: 'Подсчёт слов из заданного алфавита с ограничениями на позиции букв.',
  hint: 'Посчитайте все слова без ограничения на обязательную букву и вычтите те, где её нет совсем.',
  count: 6,
  make(rng) {
    const word = rng.pick(['КРОТ', 'ЛИСА', 'МЕТР', 'ВЕСНА', 'ПЛОВ', 'СУМКА'])
    const letters = [...new Set(word)]
    const length = rng.int(4, 5)
    const consonants = letters.filter((l) => !VOWELS.has(l))
    const required = rng.pick(consonants)
    let count = 0
    const total = letters.length ** length
    for (let code = 0; code < total; code += 1) {
      let c = code
      const chars: string[] = []
      for (let i = 0; i < length; i += 1) {
        chars.push(letters[c % letters.length])
        c = Math.floor(c / letters.length)
      }
      chars.reverse()
      if (VOWELS.has(chars[0])) continue
      if (!chars.includes(required)) continue
      count += 1
    }
    return {
      difficulty: 'medium',
      condition: `Петя составляет ${length}-буквенные слова из букв ${letters.join(', ')}. Каждая буква может входить в слово любое количество раз или не входить совсем. Слово не может начинаться с гласной буквы и должно содержать хотя бы одну букву ${required}.\n\nСколько различных слов может составить Петя?`,
      answer: String(count),
      solution: `Перебор всех ${total} слов длины ${length} над алфавитом из ${letters.length} букв. Подходят слова, у которых первая буква согласная и есть хотя бы одна «${required}». Таких слов ${count}.`,
    }
  },
}

function permutations<T>(items: T[]): T[][] {
  if (items.length <= 1) return [items]
  const result: T[][] = []
  items.forEach((item, i) => {
    const rest = [...items.slice(0, i), ...items.slice(i + 1)]
    for (const p of permutations(rest)) result.push([item, ...p])
  })
  return result
}

const task8Permute: PrototypeSpec = {
  code: '8-permute',
  name: 'Перестановки букв',
  description: 'Перестановки букв слова с запретом на соседство гласных.',
  hint: 'Расставьте сначала согласные, а гласные размещайте в промежутки между ними.',
  count: 6,
  make(rng) {
    const word = rng.pick(['ПОРТАЛ', 'СТЕПАН', 'КОМПАС', 'ГРУЗИН', 'ЛЕКТОР', 'ПЛАНЕТ'])
    const valid = permutations([...word]).filter((p) =>
      p.every((ch, i) => i === 0 || !(VOWELS.has(ch) && VOWELS.has(p[i - 1]))),
    )
    return {
      difficulty: 'medium',
      condition: `Сколько различных слов можно составить, переставляя буквы слова ${word}, если в слове не могут стоять рядом две гласные буквы? Каждая буква должна использоваться ровно один раз.`,
      answer: String(valid.length),
      solution: `Всего перестановок 6! = 720. Из них ровно ${valid.length} не содержат двух гласных подряд.`,
    }
  },
}

/* ---------- Задание 11 ---------- */

const task11Passwords: PrototypeSpec = {
  code: '11-passwords',
  name: 'Хранение паролей',
  description: 'Объём памяти для паролей и дополнительных сведений.',
  hint: 'Символ кодируется ⌈log₂N⌉ битами, а весь пароль округляется вверх до целого числа байт.',
  count: 7,
  make(rng) {
    const length = rng.int(8, 22)
    const alphabet = rng.pick([10, 12, 26, 33, 52, 62, 100])
    const extra = rng.int(6, 30)
    const users = rng.pick([20, 30, 40, 50, 100])
    const bitsPerChar = Math.ceil(Math.log2(alphabet))
    const bytesPerPassword = Math.ceil((length * bitsPerChar) / 8)
    const total = users * (bytesPerPassword + extra)
    return {
      difficulty: 'easy',
      condition: `При регистрации в компьютерной системе каждому пользователю выдаётся пароль, состоящий из ${length} символов и содержащий только символы из ${alphabet}-символьного набора. В базе данных для хранения сведений о каждом пользователе отведено одинаковое и минимально возможное целое число байт. При этом используют посимвольное кодирование паролей, все символы кодируют одинаковым и минимально возможным количеством бит. Кроме собственно пароля, для каждого пользователя в системе хранятся дополнительные сведения, для чего выделено ${extra} байт.\n\nОпределите объём памяти (в байтах), необходимый для хранения сведений о ${users} пользователях.`,
      answer: String(total),
      solution: `На символ: ⌈log₂${alphabet}⌉ = ${bitsPerChar} бит. Пароль: ⌈${length}·${bitsPerChar}/8⌉ = ${bytesPerPassword} байт. На пользователя: ${bytesPerPassword} + ${extra} = ${bytesPerPassword + extra}. Итого: ${users}·${bytesPerPassword + extra} = ${total}.`,
    }
  },
}

/* ---------- Задание 14 ---------- */

const task14Binary: PrototypeSpec = {
  code: '14-binary',
  name: 'Единицы в двоичной записи',
  description: 'Количество единиц в двоичной записи выражения со степенями двойки.',
  hint: 'Запишите 2ᵇ − c как 2ᵇ − 2ᵏ + (2ᵏ − c): разность степеней двойки даёт серию единиц.',
  count: 6,
  make(rng) {
    const a = rng.int(500, 2025)
    const b = rng.int(10, a)
    const c = rng.int(2, 200)
    const value = 4n ** BigInt(a) + 2n ** BigInt(b) - BigInt(c)
    const count = ones(value.toString(2))
    return {
      difficulty: 'medium',
      condition: `Значение арифметического выражения\n4^${a} + 2^${b} − ${c}\nзаписали в системе счисления с основанием 2. Сколько единиц содержится в этой записи?`,
      answer: String(count),
      solution: `4^${a} = 2^${2 * a} даёт одну единицу в старшем разряде. 2^${b} − ${c} раскладывается в серию единиц и хвост, определяемый числом ${c}. Подсчёт даёт ${count}.`,
    }
  },
}

const task14Ternary: PrototypeSpec = {
  code: '14-ternary',
  name: 'Цифры в троичной записи',
  description: 'Количество двоек в троичной записи выражения со степенями тройки.',
  hint: 'Вычитание небольшого числа из степени тройки порождает длинную серию двоек.',
  count: 6,
  make(rng) {
    const a = rng.int(20, 200)
    const b = rng.int(5, a - 1)
    const c = rng.int(2, 60)
    const value = 9n ** BigInt(a) + 3n ** BigInt(b) - BigInt(c)
    const count = countChar(value.toString(3), '2')
    return {
      difficulty: 'hard',
      condition: `Значение арифметического выражения\n9^${a} + 3^${b} − ${c}\nзаписали в системе счисления с основанием 3. Сколько цифр 2 содержится в этой записи?`,
      answer: String(count),
      solution: `9^${a} = 3^${2 * a}. Разность 3^${b} − ${c} в троичной записи даёт серию двоек и хвост от числа ${c}. Всего двоек: ${count}.`,
    }
  },
}

/* ---------- Задание 15 ---------- */

type Predicate = (x: number, y: number) => boolean

function minimalA(f: (x: number, y: number) => number, rest: Predicate): number {
  let max = -Infinity
  for (let x = 0; x <= 120; x += 1) {
    for (let y = 0; y <= 120; y += 1) if (!rest(x, y)) max = Math.max(max, f(x, y))
  }
  return max + 1
}

const task15Inequalities: PrototypeSpec = {
  code: '15-ineq',
  name: 'Неравенства',
  description: 'Подбор параметра A, при котором логическое выражение тождественно истинно.',
  hint: 'Выражение ложно только там, где ложны все остальные дизъюнкты. Найдите максимум выражения с A на этой области.',
  count: 7,
  make(rng) {
    const form = rng.int(0, 2)
    const b = rng.int(8, 30)
    const c = rng.int(2, 4)
    let text: string
    let answer: number
    if (form === 0) {
      answer = minimalA((x, y) => x + c * y, (x, y) => y > x || x > b)
      text = `(x + ${c}y < A) ∨ (y > x) ∨ (x > ${b})`
    } else if (form === 1) {
      answer = minimalA((x, y) => c * x + y, (x, y) => x > y || y > b)
      text = `(${c}x + y < A) ∨ (x > y) ∨ (y > ${b})`
    } else {
      const d = rng.int(5, 25)
      answer = minimalA((x, y) => x * y, (x, y) => x > b || y > d)
      text = `(x · y < A) ∨ (x > ${b}) ∨ (y > ${d})`
    }
    return {
      difficulty: form === 2 ? 'easy' : 'medium',
      condition: `Для какого наименьшего целого неотрицательного числа A выражение\n${text}\nтождественно истинно, то есть принимает значение 1 при любых целых неотрицательных x и y?`,
      answer: String(answer),
      solution: `Выражение может быть ложным, только когда ложны все дизъюнкты, кроме первого. На этой области максимум левой части неравенства равен ${answer - 1}, значит, A должно быть строго больше: A = ${answer}.`,
    }
  },
}

const task15Segments: PrototypeSpec = {
  code: '15-segments',
  name: 'Отрезки на числовой прямой',
  description: 'Минимальная длина отрезка A для истинности формулы с импликацией.',
  hint: 'Импликация (x ∈ P) → (x ∈ Q) ложна на P \\ Q — именно эту часть должен покрыть отрезок A.',
  count: 6,
  make(rng) {
    const a = rng.int(10, 40)
    let p: [number, number]
    let q: [number, number]
    let length: number
    if (rng.chance(0.5)) {
      const d = a + rng.int(5, 20)
      const b = d + rng.int(5, 30)
      p = [a, b]
      q = [a - rng.int(3, 15), d]
      length = b - d
    } else {
      const c = a + rng.int(5, 30)
      const b = c + rng.int(5, 20)
      p = [a, b]
      q = [c, b + rng.int(3, 15)]
      length = c - a
    }
    const formula = rng.chance(0.5)
      ? '((x ∈ P) → (x ∈ Q)) ∨ (x ∈ A)'
      : '¬(x ∈ A) → ((x ∈ P) → (x ∈ Q))'
    return {
      difficulty: 'medium',
      condition: `На числовой прямой даны два отрезка: P = [${p[0]}, ${p[1]}] и Q = [${q[0]}, ${q[1]}]. Укажите наименьшую возможную длину такого отрезка A, что формула\n${formula}\nтождественно истинна, то есть принимает значение 1 при любом значении переменной x.`,
      answer: String(length),
      solution: `Формула ложна только для x ∈ P, x ∉ Q и x ∉ A. Значит, A должен покрывать P \\ Q — это промежуток длины ${length}.`,
    }
  },
}

const task15Divisibility: PrototypeSpec = {
  code: '15-div',
  name: 'Делимость',
  description: 'Наибольшее A для тождественно истинной формулы с предикатом ДЕЛ.',
  hint: 'Формула ложна лишь при x, кратных обоим числам. Значит, A должно делить их НОК.',
  count: 6,
  make(rng) {
    let p = 0
    let q = 0
    do {
      p = rng.int(4, 40)
      q = rng.int(4, 40)
    } while (p === q || p % q === 0 || q % p === 0 || lcm(p, q) > 600)
    const answer = lcm(p, q)
    return {
      difficulty: 'hard',
      condition: `Обозначим через ДЕЛ(n, m) утверждение «натуральное число n делится без остатка на натуральное число m».\n\nДля какого наибольшего натурального числа A формула\n¬ДЕЛ(x, A) → (ДЕЛ(x, ${p}) → ¬ДЕЛ(x, ${q}))\nтождественно истинна, то есть принимает значение 1 при любом натуральном значении переменной x?`,
      answer: String(answer),
      solution: `Формула ложна, если x делится на ${p} и на ${q}, но не делится на A. Чтобы этого не случалось, A должно делить НОК(${p}, ${q}) = ${answer}. Наибольшее такое A = ${answer}.`,
    }
  },
}

/* ---------- Задание 16 ---------- */

const task16Value: PrototypeSpec = {
  code: '16-value',
  name: 'Значение рекурсивной функции',
  description: 'Вычисление значения функции, заданной рекуррентными соотношениями.',
  hint: 'Вычисляйте значения снизу вверх и записывайте их в таблицу — так проще не запутаться в ветвях.',
  count: 6,
  make(rng) {
    const k = rng.int(2, 3)
    const n = rng.int(12, 24)
    const memo = new Map<number, bigint>()
    const f = (m: number): bigint => {
      if (m === 1) return 1n
      const cached = memo.get(m)
      if (cached !== undefined) return cached
      const value = m % 2 === 0 ? BigInt(m) + f(m - 1) : BigInt(k) * f(m - 2)
      memo.set(m, value)
      return value
    }
    const answer = f(n)
    return {
      difficulty: 'easy',
      condition: `Алгоритм вычисления значения функции F(n), где n — натуральное число, задан следующими соотношениями:\nF(n) = 1 при n = 1;\nF(n) = n + F(n − 1), если n чётно;\nF(n) = ${k} × F(n − 2), если n > 1 и при этом n нечётно.\n\nЧему равно значение функции F(${n})?`,
      answer: answer.toString(),
      solution: `Последовательно вычисляем F(1), F(2), …, F(${n}) по соотношениям. Получаем F(${n}) = ${answer}.`,
    }
  },
}

const task16Ratio: PrototypeSpec = {
  code: '16-ratio',
  name: 'Выражения с большими аргументами',
  description: 'Упрощение выражений из значений факториалоподобной функции.',
  hint: 'Не вычисляйте F(n) напрямую — выразите F(n) через F(n − 1) и сократите.',
  count: 6,
  make(rng) {
    const n = rng.int(2000, 2030)
    const variant = rng.int(0, 1)
    const expression = variant === 0 ? `F(${n}) / F(${n - 2})` : `(F(${n}) − F(${n - 1})) / F(${n - 2})`
    const answer = variant === 0 ? BigInt(n) * BigInt(n - 1) : BigInt(n - 1) * BigInt(n - 1)
    return {
      difficulty: 'medium' as Difficulty,
      condition: `Алгоритм вычисления значения функции F(n), где n — натуральное число, задан следующими соотношениями:\nF(n) = 1 при n = 1;\nF(n) = n × F(n − 1), если n > 1.\n\nЧему равно значение выражения ${expression}?`,
      answer: answer.toString(),
      solution:
        variant === 0
          ? `F(n) = n!, поэтому F(${n}) / F(${n - 2}) = ${n} · ${n - 1} = ${answer}.`
          : `F(${n}) − F(${n - 1}) = (${n} − 1) · F(${n - 1}) = ${n - 1} · ${n - 1} · F(${n - 2}). Делим на F(${n - 2}): ${answer}.`,
    }
  },
}

/* ---------- Задание 23 ---------- */

function countPrograms(from: number, to: number, avoid?: number): number {
  if (to < from) return 0
  const ways = new Array<number>(to + 1).fill(0)
  ways[from] = 1
  for (let n = from + 1; n <= to; n += 1) {
    if (n === avoid) continue
    ways[n] = (n - 1 >= from ? ways[n - 1] : 0) + (n % 2 === 0 && n / 2 >= from ? ways[n / 2] : 0)
  }
  return ways[to]
}

const commands23 = 'У исполнителя есть две команды, которым присвоены номера:\n1. Прибавить 1\n2. Умножить на 2\nПервая команда увеличивает число на экране на 1, вторая умножает его на 2. Программа для исполнителя — это последовательность команд.'

const task23Through: PrototypeSpec = {
  code: '23-through',
  name: 'Обязательное число в траектории',
  description: 'Количество программ, траектория которых проходит через заданное число.',
  hint: 'Если траектория обязана пройти через c, ответ равен произведению числа путей a → c и c → b.',
  count: 6,
  make(rng) {
    const a = rng.int(1, 4)
    const c = rng.int(a + 4, 12)
    const b = rng.int(c + 8, 34)
    const left = countPrograms(a, c)
    const right = countPrograms(c, b)
    return {
      difficulty: 'medium',
      condition: `Исполнитель преобразует число на экране.\n${commands23}\n\nСколько существует программ, для которых при исходном числе ${a} результатом является число ${b}, и при этом траектория вычислений содержит число ${c}?`,
      answer: String(left * right),
      solution: `Число программ ${a} → ${c}: ${left}. Число программ ${c} → ${b}: ${right}. Ответ: ${left} · ${right} = ${left * right}.`,
    }
  },
}

const task23Avoid: PrototypeSpec = {
  code: '23-avoid',
  name: 'Запрещённое число в траектории',
  description: 'Количество программ, траектория которых не содержит заданное число.',
  hint: 'Заполняйте таблицу числа путей для каждого числа, а для запрещённого ставьте 0.',
  count: 6,
  make(rng) {
    const a = rng.int(1, 4)
    const d = rng.int(a + 3, 14)
    const b = rng.int(d + 8, 32)
    const answer = countPrograms(a, b, d)
    return {
      difficulty: 'medium',
      condition: `Исполнитель преобразует число на экране.\n${commands23}\n\nСколько существует программ, для которых при исходном числе ${a} результатом является число ${b}, и при этом траектория вычислений не содержит число ${d}?`,
      answer: String(answer),
      solution: `Строим таблицу K(n) — число путей из ${a} в n: K(n) = K(n − 1) + K(n / 2) для чётных n, при этом K(${d}) = 0. Получаем K(${b}) = ${answer}.`,
    }
  },
}

/* ---------- Каталог ---------- */

const empty = (number: number, name: string, slug: string, description: string): TopicSpec => ({
  number,
  name,
  slug,
  description,
  prototypes: [],
})

export const INFORMATICS_TOPICS: TopicSpec[] = [
  empty(1, 'Анализ информационных моделей', 'information-models', 'Сопоставление графа и таблицы расстояний.'),
  empty(2, 'Таблицы истинности', 'truth-tables', 'Восстановление логической функции по фрагменту таблицы.'),
  empty(3, 'Базы данных', 'databases', 'Запросы к реляционной базе данных в электронной таблице.'),
  empty(4, 'Кодирование и декодирование', 'encoding', 'Условие Фано и неравномерные двоичные коды.'),
  {
    number: 5,
    name: 'Анализ алгоритмов',
    slug: 'algorithms',
    description: 'Работа алгоритмов, преобразующих двоичную запись числа.',
    prototypes: [task5MinR, task5MinN],
  },
  empty(6, 'Исполнитель Черепаха', 'turtle', 'Подсчёт точек внутри фигуры, нарисованной Черепахой.'),
  {
    number: 7,
    name: 'Кодирование изображений и звука',
    slug: 'media-encoding',
    description: 'Объём растровых изображений и звуковых файлов.',
    prototypes: [task7Image, task7Sound],
  },
  {
    number: 8,
    name: 'Комбинаторика',
    slug: 'combinatorics',
    description: 'Подсчёт слов и перестановок с ограничениями.',
    prototypes: [task8Repeat, task8Permute],
  },
  empty(9, 'Работа с электронными таблицами', 'spreadsheets', 'Обработка числовых данных в электронной таблице.'),
  empty(10, 'Поиск в текстовом документе', 'text-search', 'Поиск слов в текстовом редакторе.'),
  {
    number: 11,
    name: 'Информационный объём',
    slug: 'information-volume',
    description: 'Объём памяти для хранения паролей и идентификаторов.',
    prototypes: [task11Passwords],
  },
  empty(12, 'Исполнитель Редактор', 'editor', 'Работа исполнителя, заменяющего подстроки.'),
  empty(13, 'IP-адреса и маски', 'networks', 'Адресация в сетях TCP/IP.'),
  {
    number: 14,
    name: 'Системы счисления',
    slug: 'number-systems',
    description: 'Запись больших выражений в позиционных системах счисления.',
    prototypes: [task14Binary, task14Ternary],
  },
  {
    number: 15,
    name: 'Логические выражения',
    slug: 'logic',
    description: 'Тождественно истинные выражения с параметром.',
    prototypes: [task15Inequalities, task15Segments, task15Divisibility],
  },
  {
    number: 16,
    name: 'Рекурсивные функции',
    slug: 'recursion',
    description: 'Вычисление значений рекурсивно заданных функций.',
    prototypes: [task16Value, task16Ratio],
  },
  empty(17, 'Обработка последовательностей', 'sequences', 'Перебор пар элементов числовой последовательности.'),
  empty(18, 'Динамика в таблицах', 'table-dp', 'Робот на клетчатом поле: максимальная и минимальная сумма.'),
  empty(19, 'Теория игр: первый ход', 'games-19', 'Выигрышная стратегия за один ход.'),
  empty(20, 'Теория игр: выигрыш Пети', 'games-20', 'Выигрыш первого игрока вторым ходом.'),
  empty(21, 'Теория игр: выигрыш Вани', 'games-21', 'Выигрыш второго игрока первым или вторым ходом.'),
  empty(22, 'Параллельные процессы', 'processes', 'Минимальное время выполнения взаимозависимых процессов.'),
  {
    number: 23,
    name: 'Исполнитель: число программ',
    slug: 'programs-count',
    description: 'Количество программ исполнителя с ограничениями на траекторию.',
    prototypes: [task23Through, task23Avoid],
  },
  empty(24, 'Обработка символьных строк', 'strings', 'Поиск подстрок с заданными свойствами в файле.'),
  empty(25, 'Обработка целых чисел', 'integers', 'Маски чисел и поиск делителей.'),
  empty(26, 'Сортировка и жадные алгоритмы', 'sorting', 'Обработка набора данных с сортировкой.'),
  empty(27, 'Анализ данных', 'clustering', 'Кластеризация точек и поиск центров.'),
]

export type { Rng }
