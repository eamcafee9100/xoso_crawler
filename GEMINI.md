# Instructions for xoso_crawler

## 1. Project Architecture & Folder Structure
- **core/**: Business logic, models, and service classes. All functions/services must return clear data types (dict with consistent schema, or list/queryset with specified element type).
- **web/**: HTML templates (Bootstrap 5), JS, CSS. Use Bootstrap classes for layout and components.
- **api/**: Django REST Framework APIs. Serializers must specify all fields and types.
- **utils/**: Utility functions. Each must have a docstring describing input/output types.

## 2. Data Communication Rules
- **Views**: Only call service/manager and expect dict/list/queryset with clear structure. Never return ambiguous objects or tuples.
- **APIs**: Always return JSON with a consistent schema. Example:
  ```json
  {
    "ngay": "2025-06-30",
    "giai_db": "12345",
    "cham_dau": 1,
    "cham_duoi": 5
  }
  ```
- **Templates**: Only render context as dict. Do not pass complex objects.

## 3. Return Type Annotation
- Always document return types in function/service/API docstrings.
- Example:
  ```python
  def get_ketqua_by_date(date: datetime.date) -> dict:
      '''
      Returns: {
        "ngay": date,
        "giai_db": str,
        "cham_dau": int,
        "cham_duoi": int
      }
      '''
  ```
- API Serializers: Define all fields and types in Meta.

## 4. General Coding Rules
- Never return multiple values as tuple/list without clear structure. Use dict with explicit keys.
- Ensure all inter-component communication uses a consistent, verifiable schema.

## 5. Django/Python Best Practices
- Use clear, PEP8-compliant names for functions, variables, and classes.
- Each model must have a `__str__` method.
- Use `ModelForm` for input forms; avoid duplicate validation logic.
- Separate business logic (service/manager) from views.
- Write tests for all important services, APIs, and models.

## 6. HTML/Bootstrap 5
- Always use Bootstrap classes for layout and components. Do not write custom CSS for basic layout.
- Use Bootstrap components (alert, modal, table, form, nav, etc.).
- If custom CSS is needed, use BEM naming and place in a separate file.

## 7. CSS
- Place all custom CSS in a separate file. Do not use inline styles.
- Prefer CSS variables for colors, fonts, spacing.
- Avoid overriding Bootstrap classes unless necessary.

## 8. JavaScript
- Place all custom JS in a separate file. Do not use inline JS.
- Use `data-attribute` for passing data from HTML to JS.
- Always handle AJAX errors clearly for the user.
- Prefer template engine or JS framework over direct DOM manipulation.

## 9. Django Templates
- Avoid complex logic in templates. Only render processed data.
- Use `{% include %}` to split templates for reuse.
- Always escape output to prevent XSS.

## 10. API Design
- Use clear, RESTful endpoint names (e.g., `/api/results/`, `/api/analysis/`).
- Return correct HTTP error codes (400, 404, 500, etc.).
- Document API response schema in docstrings or API docs.

## 11. Miscellaneous
- Clearly mark all TODO, FIXME in code.
- Refactor regularly; remove dead code and outdated comments.
- Ensure all team members understand and follow these rules.

---

**For AI agents:**
- Always follow the above conventions for code generation, refactoring, and review.
- When in doubt, prefer explicit, documented, and type-annotated code.
- If a rule is unclear, default to Django/Python/Bootstrap best practices.
