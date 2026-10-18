# Cashbook

A private Django cashbook for tracking cash in and cash out, with email and password accounts, personal notes, calendar reminders, and profile settings.

## Run locally

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
~~~

Open <http://127.0.0.1:8000/> and create an account. Its transactions, notes, and events are only visible to that account.

## Included

- Email-based sign-up, sign-in, sign-out, and password change
- Cash in and cash out transactions with category, search, type, and daily/weekly/monthly/yearly filters
- Balance overview, monthly totals, six-month cash-flow chart, and recent transactions
- Personal notes with create, edit, and delete actions
- Monthly calendar with date-specific events and reminders
- Currency-aware cash calculator for counting bills and coins
- Profile name and display currency settings

SQLite is configured for local development. Before deployment, set a private SECRET_KEY, turn off DEBUG, configure ALLOWED_HOSTS, use HTTPS, and choose a production database.
