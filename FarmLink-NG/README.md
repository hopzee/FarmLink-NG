# FarmLink NG
**Connecting Farmers Directly to Buyers.**

FarmLink NG is a Python + Streamlit agricultural marketplace for Nigerian produce. Farmers can manage listings and respond to purchase requests; buyers can search listings, send enquiries, submit requests and cancel pending requests; administrators moderate listings and user access. Prices are shown in naira (₦). **The app does not collect payments or arrange delivery.**

## Requirements
- Python 3.11 or newer
- Git (for GitHub)

## Run locally
Run these commands from the project root (`FarmLink-NG`):

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m farmlink.cli init-db
python -m farmlink.cli create-admin
streamlit run app.py
```

On Windows Command Prompt, use `copy .env.example .env` instead of `cp`.
The app applies the checked-in Alembic migrations on startup. The initial administrator is created through the terminal; public sign-up cannot create an administrator.

## Automated tests
```bash
pytest -q
```
Tests use an isolated temporary SQLite database and do not use the application's normal database.

## GitHub safety
- Commit `.env.example`, but **never commit `.env` or `.streamlit/secrets.toml`**.
- `.gitignore` excludes local databases, uploaded images, virtual environments and secrets.
- Do not put database passwords or API keys in Python source files.

## Deployment notes
The application can be deployed on a Python-capable Streamlit host. For a public deployment, configure a managed PostgreSQL database with a secret `DATABASE_URL`, for example `postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME`, and create the initial administrator through a secure terminal session or deployment job. Run migrations with `python -m farmlink.cli init-db` before opening the app to users.

**Image storage limitation:** this ZIP uses local image storage. On hosted services, local files may be ephemeral and can be lost on restart/redeploy. Before using this with real customers, connect persistent/object storage and update the image adapter. Do not treat local uploaded images as durable in production. Streamlit Cloud's filesystem should not be used as permanent user-upload storage.

## Included features
- Farmer and buyer accounts with Argon2 password hashing and normalized unique emails.
- Administrator accounts created through CLI only.
- Farmer product creation, editing, availability, soft removal, and incoming request accept/reject.
- Administrator approval/rejection of listings, account suspension/reactivation and audit log.
- Marketplace category, location, keyword, price-range and price/date sorting filters.
- Buyer enquiries, purchase requests and cancellation of pending requests.
- SQLAlchemy models, Alembic initial migration, SQLite local database and PostgreSQL driver.
- JPEG/PNG/WebP image validation and upload-size limit.
- Poppins headings, Inter body text and responsive agricultural-green UI styling.

## Scope and responsible use
Purchase requests are coordination records only; they are not payments, confirmed contracts, delivery bookings or proof of payment. Email/SMS notifications, payment processing, logistics, external image storage, rate limiting and production monitoring are not included. Review security and storage configuration before public launch.
