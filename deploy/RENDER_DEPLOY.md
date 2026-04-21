# Render Deployment Notes

## Recommended approach

Use Render's native **Python** web service and deploy this branch as a **new service**:

- Repository: `clhuangtarm-lab/agri-policy-demo`
- Branch: `interactive-traceability-v03`
- Suggested service name: `agri-policy-demo-interactive`

This repo now includes `render.yaml`, so you can also deploy it through Render Blueprint with the same settings pre-filled.

## Important runtime notes

- Python must be pinned to `3.11.11`
- Do **not** run `python -m etl.build_db` on Render
- The deployed app should use the initialized SQLite file already committed in `data/demo.db`

This repository includes:

- `.python-version` = `3.11.11`
- `render.yaml`
- initialized `data/demo.db`

## Render settings

- Runtime: `Python`
- Build command:

```bash
pip install -r requirements.txt
```

- Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

- Health check path:

```text
/healthz
```

## Environment variables

Set these values in Render if they are not auto-populated from `render.yaml`:

```text
PYTHON_VERSION=3.11.11
DATABASE_PATH=/opt/render/project/src/data/demo.db
```

## Why ETL should not run on Render

The ETL builder depends on raw source files that are not guaranteed to exist in the Render runtime environment.
To avoid `no such table` or missing-file failures, the deployment should use the prebuilt SQLite database committed to the repo.

## Create a new Render service

### Option A: Blueprint

1. In Render, choose `New +`
2. Select `Blueprint`
3. Connect the repository `clhuangtarm-lab/agri-policy-demo`
4. Choose branch `interactive-traceability-v03`
5. Render will read `render.yaml`
6. Create the new service `agri-policy-demo-interactive`

### Option B: Manual Web Service

1. In Render, choose `New +`
2. Select `Web Service`
3. Connect `clhuangtarm-lab/agri-policy-demo`
4. Choose branch `interactive-traceability-v03`
5. Enter the settings listed above

## Expected result

After deploy, these routes should return `200`:

- `/`
- `/theme1/map`
- `/theme3/coverage`
- `/scenario`
- `/traceability`
- `/composite`
- `/healthz`
