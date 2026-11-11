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

- Email-based sign-up with expiring 6-digit email verification codes, sign-in, sign-out, and password change
- Multiple user-owned transaction accounts, each with its own currency, balance, and history; existing transactions are assigned to a default Cash account
- Cash in and cash out transactions with category, search, type, and daily/weekly/monthly/yearly filters
- Balance overview, monthly totals, six-month cash-flow chart, and recent transactions
- Personal notes with create, edit, and delete actions
- Monthly calendar with date-specific events and reminders
- Currency-aware cash calculator for counting bills and coins
- Profile name and default currency settings for new accounts

SQLite is configured for local development. Before deployment, set a private SECRET_KEY, turn off DEBUG, configure ALLOWED_HOSTS, use HTTPS, and choose a production database.

In development, verification emails are printed to the runserver console unless `EMAIL_HOST` or `EMAIL_BACKEND` is configured. For inbox delivery, set `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL` in the environment before starting Django; setting `EMAIL_HOST` automatically selects SMTP. Verification codes expire after 10 minutes by default; set `EMAIL_VERIFICATION_OTP_TTL_SECONDS` (seconds) to change that period. Resends are limited to once per minute and codes allow five attempts by default.
