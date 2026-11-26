# DrSeba - Doctor Appointment Booking

DrSeba is a Django-based healthcare platform for finding doctors, booking appointments, managing patient and provider dashboards, and processing payments. It includes a demo dataset and an optional AI doctor-recommendation app.

## Features

- Patient, doctor, employee, and admin roles with dedicated dashboards
- Doctor directory with specialty, hospital, availability, ratings, and reviews
- Appointment booking, cart, payment records, and invoices
- English and Bangla interface support
- Demo accounts and seeded sample data for local evaluation
- Optional Supabase/PostgreSQL database configuration; SQLite is the local default
- AI-powered doctor recommendations

## Requirements

- Python 3.10 or later
- pip

## Local setup

From the project root:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py create_demo_data
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. On macOS or Linux, activate the environment with `source .venv/bin/activate`; copy `.env.example` to `.env` with `cp .env.example .env`.

The default `.env.example` uses local SQLite. The demo-data command is safe to rerun and writes to the database selected in `.env`.

## Supabase / PostgreSQL

In `.env`, configure a Supabase PostgreSQL connection. Use the connection string from the Supabase project settings and keep it private:

```dotenv
DB_ENGINE=django.db.backends.postgresql
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@HOST:5432/postgres
DB_SSLMODE=require
```

Replace the example values with your own connection details, then run:

```powershell
python manage.py migrate
python manage.py create_demo_data
```

Never commit `.env` or paste database credentials into source code.

## Demo login

When `DEBUG=True`, the login page displays demo accounts and supports click-to-fill. After running `create_demo_data`, the demo accounts share the password configured by `DEMO_LOGIN_PASSWORD` (defaults to `DemoLogin123!` for local development):

| Role | Email |
| --- | --- |
| Patient | `patient@gmail.com` |
| Doctor | `dr.karim@gmail.com` |
| Employee | `rahima@gmail.com` |
| Admin dashboard | `admin.demo@gmail.com` |

These are public demo credentials, not production credentials. Demo logins are disabled when `DEBUG=False`. For production, set a private `SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`, and use private database credentials.

## Useful commands

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py create_demo_data
python manage.py runserver
```

## Main project layout

```text
accounts/       Authentication, user profiles, and roles
appointments/   Appointment booking and scheduling
doctors/        Doctor profiles, specialties, and demo data command
payments/       Payments, earnings, and invoices
dashboards/     Role-specific dashboard views
ai_recommender/ Doctor recommendation integration
drseba-intelligent-doctor-recommendation-main/  Standalone recommendation project
templates/      Django templates
static/         CSS, JavaScript, and images
drseba/         Django project settings and URL configuration
```

The standalone recommendation project expects a doctor dataset and trained model under its `data/` and `models/` directories. Those data/model artifacts are not included in this repository; use approved, sanitized local copies before running that optional project.

## Configuration

Environment variables are loaded from `.env`. See [`.env.example`](.env.example) for the available settings and placeholders. The real `.env` file is intentionally ignored by Git.
