# Kairo

Kairo is a Django based API that exposes endpoints for user authentication,
matching, messaging and premium features. The project bundles a basic
configuration for running locally with SQLite.

## Setup

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Apply migrations and start the development server:

   ```bash
   python manage.py migrate
   python manage.py runserver
   ```

Environment variables such as `DJANGO_SECRET_KEY` and `DJANGO_DEBUG` can be set
in an `.env` file or exported in your shell.

## Running tests

Tests are executed with `pytest` and currently include a simple check that
`manage.py check` succeeds.

```bash
pytest
```

## Continuous Integration

A GitHub Actions workflow in `.github/workflows/tests.yml` installs the
project's dependencies and runs the test suite on every push and pull request.
