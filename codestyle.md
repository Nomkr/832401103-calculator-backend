# Code Style

Python code in this repository follows **PEP 8**.

Source: https://peps.python.org/pep-0008/

## Naming

| Kind | Rule | Example |
|---|---|---|
| Functions | snake_case | `add_history`, `calculate` |
| Variables | snake_case | `tokens`, `created_at` |
| Classes | PascalCase | `Parser`, `CalculationError` |
| Constants | UPPER_SNAKE_CASE | `DB_FILE` |

## Formatting

- 4-space indentation (no tabs).
- Every function and class has a docstring describing its purpose.
- Comments explain *why*, not *what*.
- Lines kept under 79 characters where practical.

## Structure

One function, one responsibility. Layers are separated:

| File | Layer | Responsibility |
|---|---|---|
| `app.py` | Controller | Routing, requests, responses |
| `calculator.py` | Service | Expression parsing and evaluation |
| `database.py` | Data | Database access |

## Security & Robustness

- `eval`/`exec` are never used on user input.
- All SQL uses parameterized queries (`?` placeholders) to prevent
  injection.
- Invalid input and division by zero raise `CalculationError` with a
  user-friendly message instead of crashing.
