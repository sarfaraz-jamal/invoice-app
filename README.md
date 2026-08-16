# InvoicePK — FBR-Integrated Invoicing (Multi-Tenant)

## Stack
- **Frontend**: HTMX 1.9 + Jinja2 templates
- **Backend**: FastAPI + Python
- **Database**: PostgreSQL (via SQLAlchemy async + asyncpg)
- **Queue**: Redis + Celery (FBR retry jobs)
- **FBR**: PRAL API integration (IRN + QR code)

---

## Project structure

```
fbr-invoice/
├── main.py                      ← FastAPI app, all routes (expand into routers/)
├── requirements.txt
├── static/
│   ├── css/app.css              ← Design system + all component styles
│   └── js/app.js                ← HTMX hooks, line item calc, toasts
└── templates/
    ├── base.html                ← Shell: sidebar, topbar, nav, user footer
    ├── auth/
    │   ├── login.html           ← Sign-in page
    │   └── tenant_select.html   ← Post-login: pick which business
    ├── dashboard.html           ← KPI cards + recent invoices + FBR alert
    ├── invoices/
    │   ├── list.html            ← Invoice list with search/filter
    │   ├── form.html            ← New / edit invoice (line items + FBR notice)
    │   └── detail.html          ← Invoice view + print + FBR strip + QR
    ├── customers/
    │   └── list.html            ← Customer list
    ├── reports/
    │   ├── fbr_log.html         ← FBR sync attempt log
    │   └── gst_summary.html     ← Monthly GST summary
    ├── settings/
    │   ├── index.html           ← Settings shell with sidebar nav
    │   ├── business.html        ← Business profile panel
    │   ├── fbr.html             ← FBR/PRAL credentials panel
    │   └── users.html           ← Team members + roles panel
    └── partials/                ← HTMX fragments (swapped into pages)
        ├── invoices_table.html
        ├── customers_table.html
        ├── customer_modal.html
        ├── fbr_log_table.html
        └── gst_summary.html
```

---

## HTMX patterns used

| Pattern | Where |
|---|---|
| `hx-get` + `hx-trigger="load"` | Lazy-load tables on page open |
| `hx-get` + `hx-trigger="keyup changed delay:300ms"` | Live search |
| `hx-trigger="change"` on selects | Filter/sort without page reload |
| `hx-post` + `hx-target="#modal-root"` | Load forms into modal overlay |
| `hx-delete` + `hx-swap="outerHTML"` | Delete rows in-place |
| `hx-indicator` | Spinner on every async action |
| `hx-confirm` | Native confirm dialog before destructive actions |
| `hx-include` | Pass sibling filter values with requests |
| `hx-push-url` | Update URL on navigation |
| `X-Toast` response header | Server-triggered toast messages |

---

## Setup

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Start PostgreSQL and Redis (Docker)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=dev postgres:16
docker run -d -p 6379:6379 redis:7

# 3. Set env vars
cp .env.example .env

# 4. Run migrations
alembic upgrade head

# 5. Start the app
uvicorn main:app --reload --port 8000

# 6. Start Celery worker (FBR retry queue)
celery -A tasks worker --loglevel=info
```

---

## Multi-tenancy model

- Each **business** is a `Tenant` with its own NTN, STRN, FBR POS ID, and credentials
- Users can belong to multiple tenants with different roles per tenant
- After login → tenant select screen → session stores `tenant_id`
- All DB queries are scoped to `WHERE tenant_id = :current_tenant`
- FBR credentials are stored **per tenant**, encrypted at rest

## FBR integration flow

```
User submits invoice
        │
        ▼
Invoice saved to DB (status=pending)
        │
        ▼
Celery task: POST to FBR PRAL API
        │
   ┌────┴────┐
   │         │
Success    Failure
   │         │
IRN + QR   Schedule retry
saved       (exponential backoff)
   │         │
status=    status=pending
synced     (up to N retries)
                │
            Max retries hit
                │
            status=rejected
            → Alert shown in UI
```

## FBR-required invoice fields

| Field | Source |
|---|---|
| Seller NTN | Tenant settings |
| Seller STRN | Tenant settings |
| FBR POS ID | Tenant FBR settings |
| Buyer NTN / CNIC | Invoice form |
| Invoice number | Auto-generated sequential |
| Invoice date | Invoice form |
| HS Code per item | Line item |
| Tax rate per item | Line item |
| Total + GST | Computed |
| IRN | Returned by FBR after sync |
| QR code | Returned by FBR, printed on invoice |
