# TrekFlow — Trekking Management Application (V2)

**Course:** Modern Application Development II (MAD-II)  
**Student Name:** S Karthik  
**Roll Number:** `23f2000278`  
**Email:** `23f2000278@ds.study.iitm.ac.in`  
**Institution:** Indian Institute of Technology Madras (IITM BS Degree)  
**GitHub Repository:** [SKarthik12321/Trekking-Management-Application-23f2000278](https://github.com/SKarthik12321/Trekking-Management-Application-23f2000278)

---

## 📖 Executive Summary & Overview

Adventure organizations coordinate multi-day treks across diverse geographical terrains involving trek organizers, field guides, and participants. Traditional coordination via disparate spreadsheets and manual calls frequently causes booking collisions, overbooked slots, untracked participant rosters, and lack of real-time schedule updates.

**TrekFlow V2** is a production-grade, full-stack Trekking Management Application (TMA) designed and implemented strictly in adherence to the IIT Madras MAD-II curriculum. It provides dedicated role-based portals for **Platform Administrators**, **Trek Staff (Field Guides)**, and **Trekkers (Users)** with an asynchronous batch architecture, in-memory caching, transactional booking constraints, and interactive visual analytics.

---

## 🛠️ Mandatory Technology Stack

| Component | Framework / Technology | Purpose |
| :--- | :--- | :--- |
| **Backend API** | Flask 3.0 (Python 3) | RESTful API server, route blueprints, serialization |
| **Database** | SQLite (strictly) | Relational database created programmatically via SQLAlchemy |
| **Authentication & RBAC** | PyJWT | Signed JSON Web Tokens with encrypted payload and role guards |
| **Caching Layer** | Redis 5.0 | High-performance route listing cache with TTL & invalidation |
| **Asynchronous Jobs** | Celery 5.4 + Redis | Distributed batch jobs for reminders, reports, and exports |
| **Job Scheduler** | Celery Beat | Periodic crontab scheduler for automated daily/monthly tasks |
| **Report Generation** | ReportLab 4.2 | Dynamic PDF report generator for administrative activity summaries |
| **Frontend Framework** | Vue.js 3 (SFC) + Vite | Component-based Single Page Application (SPA) |
| **Styling & UI** | Bootstrap 5.3 + Icons | Responsive mobile & desktop UI (strictly Bootstrap, no other CSS framework) |
| **Data Visualizations**| Chart.js 4.4 | Interactive charts for trek popularity and slot distribution |

---

## 👥 Roles & Capabilities

### 1. Platform Administrator
* **Pre-existing Superuser:** Created programmatically during startup database initialization (no public admin registration permitted).
* **Trek Route Management:** Full CRUD capabilities for trekking routes, difficulty ratings, durations, pricing, slot capacity, and itineraries.
* **Staff Management:** Add, configure, and monitor trek staff members and their guide credentials.
* **Guide Assignment:** Assign designated staff coordinators to individual treks.
* **Platform Oversight:** Monitor all platform-wide users, guides, and participant bookings.
* **Governance Controls:** Search, filter, deactivate, or blacklist offending users or staff accounts.
* **Analytics & Reports:** Real-time analytics dashboard with Chart.js visualizations, plus automated monthly activity reports (PDF and HTML).

### 2. Trek Staff (Field Guides)
* **Access Control:** Log in using credentials created and provisioned by the Administrator.
* **Assigned Trek Hub:** View treks specifically assigned to them by the Admin with live participant headcounts.
* **Slot Management:** Update available slot capacities in real time.
* **Trek Lifecycle Control:** Update status (`Open`, `Closed`, `Completed`). Marking a trek as `Completed` automatically marks all active bookings as completed and dispatches participant notifications.
* **Participant Roster:** View full rosters of registered trekkers with emergency contacts and manage individual trekker status.

### 3. User (Trekker)
* **Self-Registration:** Seamless public sign-up and JWT authentication.
* **Trek Discovery:** Search and filter treks dynamically by difficulty (`Easy`, `Moderate`, `Hard`), location, duration, and price.
* **Booking Engine:** Book open treks with real-time seat decrement, payment simulation, and concurrency validation.
* **Email Receipts:** Receive a styled booking confirmation with a PDF receipt after each successful booking when SMTP is enabled.
* **Booking History & Status:** Track upcoming and completed treks with full details.
* **Cancellation:** Cancel bookings prior to trek commencement with automated slot restoration.
* **Async CSV Export:** Trigger background batch export of complete booking history via Celery with in-app alert notifications.
* **Profile Management:** Update contact numbers, emergency details, and passwords.

---

## ⚡ Background Batch Jobs (Celery & Redis)

1. **Scheduled Daily Reminders:**
   * Runs daily at **08:00 AM IST** via Celery Beat.
   * Identifies treks scheduled to depart within the next 3 days.
   * Saves in-app notifications and sends email when SMTP is enabled.

2. **Scheduled Monthly Activity Report:**
   * Triggers automatically on the **1st of every month at midnight** via Celery Beat.
   * Compiles monthly metrics: total conducted treks, active participants, top popular routes, and revenue.
   * Generates formatted **PDF** (via ReportLab) and responsive **HTML** reports, saving them to `backend/reports/`; emails the HTML report to Admin when SMTP is enabled.

3. **User-Triggered Async CSV Export:**
   * Trekkers click "Export CSV" on their dashboard.
   * A Celery background worker asynchronously queries and serializes the user's booking history into CSV format under `backend/exports/`.
   * Sends an instant in-app notification with a secure download link upon completion.

---

## 🚀 Caching & Performance (Redis)

* **Cached Endpoints:** Frequently queried trek catalog listings (`/api/treks`) are cached in Redis with a 300-second (5-minute) TTL.
* **Cache Status Headers:** Returns `X-Cache-Status: HIT` or `X-Cache-Status: MISS` in API responses for transparent observability.
* **Cache Invalidation:** Route creation, updates, deletions, or status changes automatically invalidate the `treks:*` Redis cache pattern, guaranteeing fresh data without stale reads.
* **In-Memory Fallback:** Includes automatic in-memory dictionary caching fallback if the Redis daemon is unavailable during grading.

---

## 📂 Project Directory Structure

```
trekking_management_app_23f2000278/
│
├── backend/
│   ├── app.py                      # Flask Application Factory & SPA router
│   ├── config.py                   # Central configuration (DB, JWT, Redis, Celery)
│   ├── database.py                 # SQLAlchemy instance initialization
│   ├── init_db.py                  # Programmatic DB & Superuser Admin seeder
│   ├── test_app.py                 # Comprehensive end-to-end integration test suite
│   ├── requirements.txt            # Python dependencies
│   ├── trekking.db                 # SQLite database (auto-generated programmatically)
│   │
│   ├── models/                     # Programmatic SQLAlchemy ORM Models
│   │   ├── __init__.py             # Model exports
│   │   ├── user.py                 # Unified User entity (Admin, Staff, Trekker)
│   │   ├── staff_profile.py        # Staff qualifications & emergency info
│   │   ├── trek.py                 # Trek routes, slots, difficulty, itineraries
│   │   ├── booking.py              # Booking transactions & seat allocations
│   │   └── notification.py         # Alerts, reminders, and export links
│   │
│   ├── routes/                     # Modular REST API Controllers (Blueprints)
│   │   ├── __init__.py
│   │   ├── auth_routes.py          # /api/auth (Login, Register, Profile, Alerts)
│   │   ├── trek_routes.py          # /api/treks (CRUD, Redis caching, search)
│   │   ├── booking_routes.py       # /api/bookings (Reservations, cancel, CSV export)
│   │   ├── admin_routes.py         # /api/admin (Stats, users, staff, reports)
│   │   └── staff_routes.py         # /api/staff (Assigned treks, slots, rosters)
│   │
│   ├── tasks/                      # Celery Background Batch Workers
│   │   ├── __init__.py
│   │   └── celery_app.py           # Reminders crontab, monthly report, CSV export
│   │
│   ├── utils/                      # Helper Modules
│   │   ├── __init__.py
│   │   ├── auth.py                 # JWT token generation, decoding & RBAC decorators
│   │   ├── cache.py                # Redis caching decorators & invalidation
│   │   ├── email_service.py        # Optional SMTP mail delivery
│   │   └── pdf_generator.py        # ReportLab PDF & HTML report builder
│   │
│   ├── exports/                    # Auto-generated user CSV exports
│   ├── reports/                    # Auto-generated monthly PDF & HTML reports
│   └── static/trek_images/         # Uploaded local trek banner images
│
├── frontend/                       # Vue.js 3 Single Page Application
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── dist/                       # Production pre-built SPA bundle (served by Flask)
│   └── src/
│       ├── main.js                 # App initialization & plugin registration
│       ├── App.vue                 # Root component
│       ├── router/index.js         # Vue Router with navigation auth guards
│       ├── store/auth.js           # Reactive auth & state management
│       ├── components/             # Reusable Bootstrap UI components
│       │   ├── Navbar.vue
│       │   ├── Footer.vue
│       │   ├── TrekCard.vue
│       │   ├── BookingModal.vue
│       │   ├── StatsChart.vue      # Chart.js analytics chart component
│       │   └── ToastAlert.vue
│       └── views/                  # Role-specific dashboard views
│           ├── LandingView.vue
│           ├── LoginView.vue
│           ├── RegisterView.vue
│           ├── UserDashboardView.vue
│           ├── UserTreksView.vue
│           ├── UserBookingsView.vue
│           ├── UserProfileView.vue
│           ├── StaffDashboardView.vue
│           ├── StaffTrekDetailView.vue
│           ├── AdminDashboardView.vue
│           ├── AdminTreksView.vue
│           ├── AdminStaffView.vue
│           ├── AdminUsersView.vue
│           ├── AdminBookingsView.vue
│           └── AdminReportsView.vue
│
├── Project_Report_23f2000278.pdf   # Official Project Report (PDF format)
└── README.md                       # Comprehensive documentation
```

---

## 🔑 Default Pre-Configured Credentials

Upon initial launch, `init_db.py` automatically populates the database with the pre-existing superuser admin and sample accounts for instant viva evaluation:

| Role | Username / Email | Password | Details |
| :--- | :--- | :--- | :--- |
| **Superuser Admin** | `admin@trekapp.com` (or `admin@gmail.com`) | `Admin@123` (or `admin123`) | Pre-existing superuser with complete access |
| **Trek Staff (Guide)** | `ravi@trekapp.com` | `Staff@123` | Senior Himalayan Mountain Guide (7 yrs exp) |
| **Trek Staff (Guide)** | `ananya@trekapp.com` | `Staff@123` | Western Ghats Specialist (4 yrs exp) |
| **Trek Staff (Guide)** | `arjun@trekapp.com` | `Staff@123` | Mountaineering Expedition Leader (9 yrs exp) |
| **Trekker (User)** | `rohit@example.com` | `User@123` | Sample registered trekker with active bookings |
| **Trekker (User)** | `sneha@example.com` | `User@123` | Sample registered trekker |

---

## ⚙️ Quick Start & Execution Guide

### Optional: test outgoing email locally with MailHog (Docker)

Gmail SMTP in `backend/.env` sends to real inboxes and does not require Docker. Use MailHog only if you want captured test messages that are not delivered to Gmail, IITM, or any other real mailbox.

Start MailHog in Docker (run once):
```bash
docker run -d --name tma-mailhog -p 1025:1025 -p 8025:8025 mailhog/mailhog:v1.0.1
```
If the container already exists, start it with `docker start tma-mailhog`. Open its inbox at `http://127.0.0.1:8025`.

In the terminal where Flask will run, enable SMTP before starting the backend:
```bash
cd backend
source .venv/bin/activate
export SMTP_ENABLED=true
export SMTP_HOST=127.0.0.1
export SMTP_PORT=1025
export SMTP_USE_TLS=false
export SMTP_FROM_EMAIL=no-reply@trekflow.local
python app.py
```
Register with an email address you control, then look for the welcome message in the MailHog inbox. After a successful demo booking, look for a styled confirmation email with a PDF receipt attached. The payment is simulated; no real charge is made. The address is only used as the message recipient; MailHog does not contact that address. When SMTP is disabled (the default), the app says no email was sent.

To send scheduled reminders or monthly reports through MailHog, set the same `SMTP_*` variables in the Celery worker terminal before starting it. Stop MailHog with `docker stop tma-mailhog`.

For real delivery through Gmail, use `smtp.gmail.com`, port `587`, and STARTTLS (`SMTP_USE_TLS=true`) with a Google App Password. Put those values in your local, ignored `backend/.env`, then run `source .env` from the backend directory before starting Flask or the Celery worker. The `.env` file is excluded from Git; never commit credentials. MailHog is safer for local-only demos.

### Prerequisites
- Python 3.10+
- Node.js 18+ (optional, since production frontend is pre-built in `dist/`)
- Redis Server (running on `localhost:6379`)

### 1. Launch Backend API
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (first time setup)
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Load local SMTP credentials (edit backend/.env first)
source .env

# Start Flask API server (creates DB & seeds admin programmatically)
python app.py
```
*The Flask API always uses `http://127.0.0.1:5001`. Start only one Flask instance; if it is already running, reuse it. To reload configuration, press Ctrl+C in its terminal before starting it again. It initializes the SQLite database and seeds the pre-existing superuser Admin and demo treks.*

### 2. Launch Celery Worker & Beat Scheduler
Open two separate terminal windows for background batch jobs:

**Terminal 2 (Celery Worker):**
```bash
cd backend
source .venv/bin/activate
source .env
export PYTHONPATH="$(pwd)"
python -m celery -A tasks.celery_app.celery_app worker --pool=solo --concurrency=1 --loglevel=info
```

**Terminal 3 (Celery Beat Periodic Scheduler):**
```bash
cd backend
source .venv/bin/activate
source .env
export PYTHONPATH="$(pwd)"
python -m celery -A tasks.celery_app.celery_app beat --loglevel=info --schedule=/tmp/tma-demo-celerybeat-schedule
```

### 3. Frontend Development (Optional)
The Flask server directly serves the pre-compiled production build from `frontend/dist/`. To run the Vite hot-reloading dev server:
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Testing Suite

A comprehensive integration test suite is included in `backend/test_app.py`, verifying all business constraints, RBAC security, Redis caching, and Celery tasks:

```bash
cd trekking_management_app_23f2000278/backend
python test_app.py
```

### Test Coverage Highlights:
1. `test_01_public_endpoints`: Health check and landing platform statistics.
2. `test_02_authentication_and_rbac`: Token generation and strict role boundary enforcement.
3. `test_03_registration_and_validation`: Trekker registration, field validation, and duplicate rejection.
4. `test_04_trek_caching_and_crud`: Redis caching headers (`HIT`/`MISS`) and Admin trek CRUD.
5. `test_05_booking_business_rules`:
   - Slot decrement upon booking.
   - Overbooking rejection beyond available capacity (`400 Bad Request`).
   - Duplicate active booking prevention for the same trek (`409 Conflict`).
   - Slot restoration upon user cancellation.
6. `test_06_deactivation_and_blacklisting`: Administrative account blacklisting with immediate token revocation (`403 Forbidden`).
7. `test_07_batch_jobs_execution`: Celery Daily Reminders, Monthly PDF/HTML report generation, and User CSV export.

---

## 📜 Academic Integrity Declaration

This project was developed by **S Karthik (Roll No: 23f2000278)** for the Modern Application Development II (MAD-II) course at IIT Madras. All database models, business logic, RBAC security, API routes, and frontend views conform strictly to course instructions and evaluation rubrics.
