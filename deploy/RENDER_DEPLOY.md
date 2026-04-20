# Render Deployment Notes

## Root cause of the current failure

Render's native Python runtime currently defaults to Python `3.14.3` for newly created services.
This project pins `rapidfuzz==3.10.1`, which does not build cleanly in that environment.

## Recommended fix

Use Render's Python runtime, but pin Python to `3.11.11`.

This repository includes a `.python-version` file with:

```text
3.11.11
```

You can also set the same value in Render as:

```text
PYTHON_VERSION=3.11.11
```

## Important note about Docker

If you create a **Python** service on Render, Render ignores this repo's `Dockerfile`.
If you want Render to use the `Dockerfile`, create a **Docker** service instead.

## Native Python runtime settings

- Runtime: `Python`
- Build command:

```bash
pip install -r requirements.txt
python -m etl.build_db
```

- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Docker runtime settings

If you prefer not to depend on Render's Python version selection, create a **Docker** service.
In that case Render will use the project's `Dockerfile`, which already starts from `python:3.11-slim`.
