# CATS — MIST EECE Portal

Visit: https://eece-cats.mist.ac.bd

A Django-based portal for managing Lab Test requests, Consultancy projects, user dashboards, and report verification for CATS–MIST (Department of EECE).

## Features

- User authentication and profile management
- Lab Test requests with itemized pricing and attachments
- Consultancy requests and status updates
- Admin dashboards and status management, including delivered report verification codes
- Payment receipt uploads and document previews
- Mobile-friendly dashboard layouts with tabbed views

## Tech Stack

- Python (Django)
- SQLite (development)
- HTML templates (Django), CSS, minimal JS

## Directory Structure

```
// Directory tree (3 levels, limited to 200 entries)
├── .venv\
│   ├── .gitignore
│   ├── Include\
│   ├── Lib\
│   │   └── site-packages\
│   ├── Scripts\
│   │   ├── Activate.ps1
│   │   ├── activate
│   │   ├── activate.bat
│   │   ├── activate.fish
│   │   ├── deactivate.bat
│   │   ├── django-admin.exe
│   │   ├── pip.exe
│   │   ├── pip3.13.exe
│   │   ├── pip3.exe
│   │   ├── python.exe
│   │   ├── pythonw.exe
│   │   └── sqlformat.exe
│   └── pyvenv.cfg
├── cats_site\
│   ├── __init__.py
│   ├── __pycache__\
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3
├── home\
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── migrations\
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── media\
│   ├── consultancy_requests\
│   ├── lab_requests\
│   ├── payment_receipts\
│   └── profiles\
├── static\
│   ├── css\
│   ├── image\
│   └── js\
└── templates\
    ├── base.html
    ├── dashboard.html
    ├── lab_tests_dashboard.html
    ├── consultancy_dashboard.html
    ├── profile_dashboard.html
    ├── lab_test_request_detail.html
    ├── admin_overview.html
    ├── how_to_pay.html
    ├── help_dashboard.html
    ├── home.html
    ├── login.html
    ├── signup.html
    └── more...
```

## Getting Started

### Prerequisites

- Python 3.10+ (project’s dev environment shows Python 3.13)

### Setup (Development)

1. Create and activate a virtual environment (optional if using the included `.venv`):
   - Windows PowerShell: `python -m venv .venv && .\.venv\Scripts\Activate.ps1`
2. Install dependencies (if not using the included `.venv`):
   - `pip install django`
3. Apply migrations:
   - `python manage.py migrate`
4. Create a superuser (admin):
   - `python manage.py createsuperuser`
5. Run the development server:
   - `python manage.py runserver`

Visit `http://127.0.0.1:8000/` to access the site.

## Key URLs

- Home: `/`
- Dashboard: `/dashboard/`
- Lab Tests: `/dashboard/lab-tests/`
- Consultancy: `/dashboard/consultancy/`
- Profile: `/dashboard/profile/`
- How to Pay: `/dashboard/how-to-pay/`
- Get Help: `/dashboard/get-help/`
- Admin Overview: `/admin/overview/`
- Django Admin: `/admin/`
- Report Verification: `/verify-report/`

## Notes

- Media files (sample docs and receipts) are stored under `media/`.
- The dashboard includes an admin-only toggle to reveal “Previous Delivered Reports” for both Lab Tests and Consultancy.
- Static styles live in `static/css/` (notably `dashboard.css` for layout and responsive behavior).
