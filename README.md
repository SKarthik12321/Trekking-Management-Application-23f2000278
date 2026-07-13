# TrekFlow - Trekking Management Application

TrekFlow is a comprehensive, responsive web application designed for adventure organizations to manage trekking activities, guides (trek staff), and participants (trekkers). It provides a secure, role-based environment that streamlines trek booking, coordinator assignments, approval workflows, and booking statistics.

---

## ⛰️ Key Features

### 1. 🔑 Secure Authentication & Role-Based Access Control (RBAC)
- Multi-user system with distinct roles: **Admin**, **Trek Staff**, and **User (Trekker)**.
- Secure self-registration for Trekkers and Staff members.
- Robust security filtering using Flask-Login and role-based decorator validation to block unauthorized path traversal.
- Blacklisted users and staff are blocked immediately from logging in.

### 2. 👑 Admin Dashboard
- **Key Metrics:** Total treks, total bookings, active users, and staff counts.
- **Data Visualization:** Built-in charts displaying bookings per trek route.
- **Trek Management (CRUD):** Create, view, edit, and delete trekking routes.
- **Staff Approval & Access Management:**
  - Approve or reject pending staff registrations.
  - Blacklist staff or reactivate previously suspended staff.
  - Assign approved guides/staff to trekking events.
- **Trekker Control:** Monitor registered trekkers, suspend/blacklist accounts, or reactivate them as needed.
- **Global Search:** Quickly search treks, users, and staff by Name or unique ID.
- **All Bookings:** Centralized log to view and monitor all booking histories in real time.

### 3. 🥾 Trek Staff Dashboard
- **Guides View:** Shows assigned treks and the list of registered users/trekkers for each assigned trek.
- **Trek Lifecycle Management:**
  - Update slot capacity.
  - Adjust trek status (Open / Closed / Completed).
  - Track guide schedule updates.

### 4. 🏕️ Trekker (User) Dashboard
- **Interactive Slider:** An elegant, auto-sliding banner carousel showcasing upcoming trails.
- **Trek Explorer:** Dynamic filtering by location and difficulty levels (Easy, Moderate, Hard).
- **Online Booking:** One-click booking with auto-updates of slot counts and strict overbooking prevention.
- **Booking Management:** Cancel active bookings (restores slots instantly) and view trekking history.
- **Profile Customization:** Edit personal contact details and user credentials.

---

## 🛠️ Technology Stack

- **Backend:** Flask, Flask-Login, Werkzeug (Security utilities)
- **Database ORM:** SQLite via Flask-SQLAlchemy (Programmatic schema generation and transaction handling)
- **Frontend Engine:** Jinja2 Templating
- **UI & Layout:** Bootstrap 5, FontAwesome 6, custom CSS (Fully responsive on desktop, tablet, and mobile with a custom off-canvas sidebar drawer)
- **Testing:** Python unittest module

---

## 📂 Project Architecture

```
TrekkingManagementApplication/
│
├── app.py                 # Application factory, route registration, DB creation/seeding
├── config.py              # Server and database configuration
├── extensions.py          # SQLAlchemy and LoginManager instance initialization
├── models.py              # Database Models: User, Trek, Booking
├── seed.py                # Schema bootstrapper and default Admin seeding
│
├── routes/                # Blueprint controller logic separation
│   ├── __init__.py
│   ├── admin_routes.py    # Admin operations
│   ├── staff_routes.py    # Staff coordinator actions
│   ├── user_routes.py     # Trekker browsing and bookings
│   ├── auth_routes.py     # User registration, login, logout
│   └── api_routes.py      # REST APIs
│
├── templates/             # Jinja2 layouts and components
│   ├── base.html          # Global layout template & responsive off-canvas mobile drawer
│   ├── admin/             # Admin dashboard & controls
│   ├── auth/              # Registration & Login pages
│   ├── staff/             # Guide schedules and trek states
│   └── user/              # Booking logs, trail filters, profile details
│
├── static/                # Static assets
│   ├── css/
│   │   └── custom.css     # Dark-mode navbar, mobile view media queries, hover transitions
│   └── img/
│       └── treks/         # High-resolution landscape trek images
│
└── test_app.py            # Suite of 4 automated backend validation tests
```

---

## 🚀 Getting Started

### 1. Prerequisite Installations
Ensure Python 3.9+ is installed on your local machine.

### 2. Set Up the Project Environment
Navigate to the root folder, set up a python virtual environment, and install dependencies:
```bash
# Set up virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Initialize and Run the Application
Start the Flask development server. On startup, the system will programmatically build the database schema and seed a default administrator user:
```bash
# Start the application
python app.py
```
Open **[http://127.0.0.1:5001](http://127.0.0.1:5001)** in your web browser. (Note: Port `5001` is used to prevent port conflicts with macOS AirPlay receiver).

### 🔑 Seeding Credentials
To log in immediately, use the default administrator credentials:
- **Username / Email:** `admin@trek.com`
- **Password:** `admin123`

---

## 🧪 Testing
The project includes a robust test suite covering auth logic, overbooking prevention, and double-booking controls. Run the automated tests with:
```bash
python -m unittest test_app.py
```

---

## 🌐 API Reference

TrekFlow exposes REST APIs returning JSON response format:

### 1. Get All Treks
- **Endpoint:** `GET /api/treks`
- **Response:** JSON list containing details of all treks.

### 2. Get Trek Details
- **Endpoint:** `GET /api/treks/<int:id>`
- **Response:** JSON object of the requested trek route details.

### 3. Get All Bookings
- **Endpoint:** `GET /api/bookings`
- **Response:** JSON list containing all booking transactions.
