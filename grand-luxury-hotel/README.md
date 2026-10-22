# Grand Luxury Hotel

Django REST Framework + React/TypeScript premium hotel booking and operations platform.

## Quick start

Python 3.11+, Node.js 20+ recommended.

```bash
cd backend
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env # Windows: copy .env.example .env
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py test
python manage.py runserver
```

In a second terminal:
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:5173; staff admin: http://localhost:8000/admin.

## Features
- 5 room categories, actual physical room inventory, rich descriptions and images.
- Date-scoped availability and genuine reservation records; overlapping stays on the same physical room are prevented in the backend.
- Optional PostgreSQL exclusion constraint migration for **database-level protection** against concurrent overlapping stays. SQLite is for development only and serializes writes differently.
- User registration/login, personal dashboard, reference codes, cancellation policy and printable confirmation.
- Staff CRUD in Django admin: inventory, housekeeping, pricing, seasonal rates, promo codes, restaurant, services, reviews and staff roles.
- Staff real-time database-backed business metrics.
- Discount codes, seasonal price calculations, Telegram admin booking alerts (optional).
- Responsive luxury frontend with Uzbek, English, Russian labels and dark/light theme.

## API endpoints
POST /api/auth/register/, /api/auth/login/, /api/auth/logout/
GET /api/auth/me/
GET /api/room-types/, /api/services/, /api/restaurant/, /api/reviews/, /api/gallery/
GET /api/availability/?check_in=YYYY-MM-DD&check_out=YYYY-MM-DD&guests=2
GET, POST /api/bookings/
GET /api/bookings/<id>/
POST /api/bookings/<id>/cancel/
GET /api/admin/stats/ (staff only)
POST /api/contact/

## Environment
See backend/.env.example. By default SQLite. Set DATABASE_URL=postgresql://USER:PASSWORD@HOST/DB for PostgreSQL. For production, configure SSL, allowed hosts, CORS origins, object storage, HTTPS, outgoing email or Telegram notifications, and a payment provider. Demo images are remote Unsplash links; inspect [Unsplash licensing](https://unsplash.com/license) before production use and replace with images licensed for your business. Contact address and branding are demo information.

**Important:** Reservation records are not payment captures. Pricing is computed and stored when reserved. No dummy reservation actions. Admin analytics report recorded booking amounts (not settled cash revenue). Email delivery, restaurant table bookings, live customer review submission and payment processing are future integrations. Run automated tests before deployment.
