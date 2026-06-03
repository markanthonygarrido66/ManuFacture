# Manufacturing Yield & Command Room — Django Dashboard

A full-stack Django command center for manufacturing plant tracking:
yield accumulation, material purchases, production line status, and
JWT-authenticated IoT sensor API endpoints.

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Apply database migrations
python manage.py migrate

# 3. Seed demo data (creates admin user + sample records)
python manage.py seed_data

# 4. Run the development server
python manage.py runserver
```

Visit **https://manufacturing-dashboard-oyc4.onrender.com/dashboard/** and log in with:
- Username: `admin`  Password: `admin123`

---

## Features

### Dashboard (executives & managers)
- Accumulated yield, defect rate, material spend, OEE efficiency KPIs
- Hourly yield trend chart per production line (Chart.js)
- Per-line status table with yield% progress bars
- Live IoT sensor event feed
- Process efficiency gauges
- Material purchase tracker with delivery status

### Filters (auto-submitting dropdowns)
- Filter by production line, date range, or shift
- Every dropdown change immediately reloads filtered data (no submit button)

### Security
- **Rolling session window**: 15-minute inactivity logout (`SESSION_SAVE_EVERY_REQUEST = True`)
- **Session modal**: warns user at 60s remaining with countdown timer
- `RollingSessionMiddleware`: server-side inactivity enforcement
- CSRF protection on all forms
- `@login_required` on all dashboard views

### Yield input form
- Factory floor managers submit: line, shift, units produced, defectives, OEE%, notes
- Server-side validation with user-friendly error messages

### JWT API (IoT sensors)
All endpoints require `Authorization: Bearer <token>`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/token/` | Get JWT token pair |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/v2/yield/push` | Push yield data from a sensor |
| GET  | `/api/v2/yield/stream` | Stream aggregated yield (last N hours) |
| GET  | `/api/v2/lines/status` | Current status of all production lines |
| POST | `/api/v2/sensors/event` | Log a sensor event (warn/error/ok) |

#### Example: Sensor pushing yield data
```bash
# 1. Get token
curl -X POST https://manufacturing-dashboard-oyc4.onrender.com/dashboard/ api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"iot_sensor","password":"sensor_secret_42"}'

# 2. Push yield data
curl -X POST https://manufacturing-dashboard-oyc4.onrender.com/dashboard/ api/v2/yield/push \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "S-14",
    "line_code": "LINE-A",
    "units_produced": 680,
    "units_defective": 12,
    "oee_efficiency": 91.4,
    "shift": "morning"
  }'
```

---

## Project structure

```
manufacturing_dashboard/
├── manage.py
├── requirements.txt
├── manufacturing_dashboard/
│   ├── settings.py        # Django config, JWT, session settings
│   └── urls.py            # Root URL routing
└── dashboard/
    ├── models.py          # ProductionLine, YieldRecord, MaterialPurchase, SensorEvent
    ├── views.py           # Dashboard & yield input views
    ├── api_views.py       # DRF JWT-authenticated API endpoints
    ├── urls.py            # Dashboard URL patterns
    ├── api_urls.py        # API URL patterns
    ├── middleware.py      # RollingSessionMiddleware
    ├── admin.py           # Django admin registration
    ├── migrations/
    └── templates/dashboard/
        ├── index.html     # Main command room dashboard
        ├── login.html     # Login page
        └── yield_input.html  # Floor manager yield form
```

---

## Production checklist
- [ ] Set `SECRET_KEY` from environment variable
- [ ] Set `DEBUG = False`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use PostgreSQL (set `DATABASES` in settings)
- [ ] Run `python manage.py collectstatic`
- [ ] Use gunicorn + nginx
- [ ] Set `SIMPLE_JWT['ALGORITHM']` to `RS256` with real key pair
