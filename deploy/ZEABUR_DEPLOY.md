# Zeabur Deployment Notes

This project is intended to deploy as a single FastAPI service on Zeabur.

## Important deployment decision

The current `demo_platform/` folder does **not** contain the full upstream ETL source tree used by `etl/build_db.py`.
Because of that, cloud build environments should deploy with the already-built `data/demo.db` included in the repo.

## What must be committed

- `app/`
- `etl/`
- `requirements.txt`
- `Dockerfile`
- `zeabur.json`
- `data/demo.db`

`data/demo.db` is about 88 MB, which is large but still below GitHub's 100 MB per-file limit.

## Local preflight

Run these before pushing:

```powershell
cd output\demo_platform
python -m etl.build_db
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

Confirm:

- `/`
- `/theme1/map`
- `/theme3/coverage`
- `/composite`
- `/detail`

## GitHub push flow

```powershell
git init
git branch -M main
git add .
git commit -m "Prepare agri policy demo for Zeabur deployment"
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Zeabur setup

1. Create a new service from GitHub.
2. Point Zeabur to this repository root.
3. Keep the generated service port as HTTP `8080`.
4. Keep `DATABASE_PATH=/app/data/demo.db`.
5. Deploy.

## Runtime expectations

- The image runs `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}`.
- The app expects `data/demo.db` to exist inside the container image.
