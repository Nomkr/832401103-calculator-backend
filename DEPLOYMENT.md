# Backend Deployment Guide

## Pre-deployment Checks

```bash
python -m unittest discover -v
docker build -t calculator-backend .
docker run --rm -p 5000:5000 calculator-backend
```

Verify in another terminal:

```bash
curl http://127.0.0.1:5000/api/health
curl -X POST http://127.0.0.1:5000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{"expression":"(1+2)*3"}'
```

## Render Steps

1. Sign up or log in to Render and prepare a GitHub repository.
2. Push this directory as a standalone repository root to GitHub.
3. Create a Web Service, connect the repository, and choose Docker as
   the runtime.
4. Use the `Dockerfile` at the repository root and set the health check
   path to `/api/health`.
5. After the build finishes, open
   `https://<service-name>.onrender.com/api/health`.
6. Put this HTTPS URL first in the Android `BACKEND_URLS` list and
   rebuild the APK.

## Owner To-dos

- Log in to the deployment platform and confirm the free instance plan.
- Create two separate GitHub repositories for the Android and Flask
  projects.
- Fill the public HTTPS backend URL into the Android code.
- Install the final APK on an emulator or device and capture demo
  screenshots.

## Data Persistence

The backend supports the `CALCULATOR_DB_FILE` environment variable. Point
it to a `calculator.db` on a persistent disk when the platform provides
one. Without a persistent disk, a service rebuild may clear history, but
the calculate API keeps working.
