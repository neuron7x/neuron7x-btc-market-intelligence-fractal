# Contributing Guidelines

Дякуємо, що хочете зробити внесок у **BTC Market Intelligence Fractal** 🚀

## Як працювати з кодом
- Використовуйте Python ≥ 3.11.
- Усі залежності мають бути встановлені через:
  ```bash
  pip install -r requirements.txt -c constraints.txt
  pip install .[dev] -c constraints.txt
  ```
- Перед комітом запускайте перевірки стилю та форматування:
  ```bash
  black .
  ruff check .
  ```

## Оновлення залежностей
- Зафіксуйте нові версії в `constraints.txt`.
- Вкажіть ті самі версії в `pyproject.toml` (лише `==`).
- Перегенеруйте `requirements.txt` з `pyproject.toml`:
  ```bash
  pip-compile pyproject.toml --output-file requirements.txt
  ```

