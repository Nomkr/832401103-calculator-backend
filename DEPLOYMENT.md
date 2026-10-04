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

## PythonAnywhere Deployment (Current)

The submitted service is deployed at `https://nomkr.pythonanywhere.com`.

1. Open a PythonAnywhere Bash console and clone this repository as a
   standalone project.
2. Create or activate a virtual environment and install dependencies:
   `pip install -r requirements.txt`.
3. In the **Web** tab, create a Flask application and select the virtual
   environment used above.
4. In the WSGI configuration file, add the project directory to `sys.path`
   and expose the Flask object as `application`:

   ```python
   import sys
   sys.path.insert(0, "/home/<username>/832401103-calculator-backend")
   from app import app as application
   ```

5. Reload the web application and verify:
   `https://<username>.pythonanywhere.com/api/health`.
6. Put the HTTPS URL first in the Android `BACKEND_URLS` list and rebuild
   the APK.

The current deployment passes the health check at
`https://nomkr.pythonanywhere.com/api/health` with HTTP 200.

## Docker Local Verification

The `Dockerfile` remains useful for reproducible local checks and for a
Docker-capable hosting provider. The `render.yaml` file is retained as an
optional alternative deployment description; it is not the service used for
the submitted deployment.

## Owner To-dos

- Keep the PythonAnywhere web application running during the evaluation.
- Check `/api/health` before publishing the blog.
- Install the final APK on an emulator or device and capture demo
  screenshots.

## Data Persistence

The backend supports the `CALCULATOR_DB_FILE` environment variable. Point
it to a `calculator.db` on a persistent disk when the platform provides
one. Without a persistent disk, a service rebuild may clear history, but
the calculate API keeps working.
