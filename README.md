HealthPadi backend — deployment notes

Quick overview

- Django REST Framework application; uses gunicorn + whitenoise for static files.
- Requirements are in `requirements.txt`. Python >= 3.12 is recommended.

Files added for deployment

- `Procfile` : declares the web process for PaaS (Heroku/Render).
- `Dockerfile`: builds a container image for the app.
- `.env.example`: example environment variables for production.

Deploying to Render or Railway (quick)

1. Push this repo to GitHub and connect it to Render or Railway.
2. Add environment variables on the service dashboard: `SECRET_KEY`, `DATABASE_URL` (or DB\_\* values), `DEBUG=false`, `ALLOWED_HOSTS`.
3. Build command: `pip install -r requirements.txt`
4. Start command (Procfile will be used): `gunicorn healthpadi.wsgi --workers 3 --bind 0.0.0.0:$PORT`
5. After deploy, run migrations and collectstatic from the service's console:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Deploying with Docker (local test or container host)

1. Build image:

```bash
docker build -t healthpadi .
```

2. Run container with environment variables (use an `.env` file):

```bash
docker run -p 8000:8000 --env-file .env healthpadi
```

3. Inside container (or via host) run migrations if needed:

```bash
docker exec -it <container_id> python manage.py migrate
```

Notes

- Use a managed Postgres for production and set `DATABASE_URL` accordingly.
- Ensure `SECRET_KEY` is long and random and never committed to the repo.
- Set `DEBUG=False` in production.
