# Field Ordering / Порядок полів

## English

To keep JSON data deterministic and easy to review, fields are emitted in a fixed order.

1. `schema_version`
2. `lineage`
3. `asof` (when applicable)
4. Domain fields (`scenario`, `window`, `mode`, ...)
5. Data blocks (`features` or `summary`, `details`)
6. Optional fields in alphabetical order

Nested objects follow the same pattern: required fields first, then optional ones alphabetically. Serialize JSON payloads respecting this order.

## Українська

Щоб JSON був детермінованим та зручним для перевірки, поля виводяться у фіксованому порядку.

1. `schema_version`
2. `lineage`
3. `asof` (якщо є)
4. Предметні поля (`scenario`, `window`, `mode` тощо)
5. Блоки даних (`features` або `summary`, `details`)
6. Необов'язкові поля за алфавітом

Вкладені об'єкти дотримуються тих самих правил: спочатку обов'язкові, потім необов'язкові поля за алфавітом. Серіалізовані JSON слід формувати з урахуванням цього порядку.
