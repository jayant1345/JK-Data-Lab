# JK Data Lab — Portfolio Website

A professional portfolio website for **JK Data Lab**, an AI and Data Science freelancing business owned by **Kinjal Jayantkumar Jayswal**, based in Ahmedabad, Gujarat, India.

Built with **Python Flask**, **SQLite**, and a dark glassmorphism design. Deployable on **Railway.app**.

---

## Features

- **Public website** — Home, About, Services, Portfolio, Blog, Contact pages
- **Admin panel** — Full CRUD for projects, services, testimonials, blog posts, messages, skills, and site settings
- **Particle canvas** hero with typing animation and floating hexagons
- **Portfolio filtering** by category with animated project cards
- **Testimonial slider** with auto-advance
- **Animated stat counters** and skill progress bars
- **Contact form** with rate limiting (3 submissions/hour/IP) and email notification
- **SEO** — meta tags, robots.txt, sitemap.xml, JSON-LD structured data
- **Security** — CSRF protection, password hashing, login-required admin routes, safe file uploads
- **Export** — messages to CSV, full database to JSON
- **Railway.app ready** — Procfile and railway.json included

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask |
| Database | SQLite via SQLAlchemy |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Authentication | Flask-Login |
| Email | Flask-Mail (Zoho SMTP) |
| Deployment | Railway.app |
| Domain | jkdatalab.com (Hostinger DNS) |

---

## Project Structure

```
jkdatalab/
├── app.py                    # Flask application factory
├── config.py                 # Configuration classes
├── models.py                 # SQLAlchemy models
├── requirements.txt
├── Procfile                  # Railway deployment
├── railway.json
├── .env                      # Environment variables (not in git)
├── .env.example
│
├── routes/
│   ├── public.py             # Public page routes
│   ├── admin.py              # Admin panel routes
│   └── api.py                # JSON API endpoints
│
├── utils/
│   ├── helpers.py            # Slug, image, pagination utilities
│   ├── email.py              # Contact email sender
│   └── seed_data.py          # Initial database seeder
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── about.html
│   ├── services.html
│   ├── portfolio.html
│   ├── portfolio_detail.html
│   ├── blog.html
│   ├── blog_detail.html
│   ├── contact.html
│   ├── 404.html
│   ├── 500.html
│   └── admin/
│       ├── base_admin.html
│       ├── login.html
│       ├── dashboard.html
│       ├── projects.html / project_form.html
│       ├── services.html / service_form.html
│       ├── testimonials.html / testimonial_form.html
│       ├── blog.html / blog_form.html
│       ├── messages.html
│       ├── skills.html / skill_form.html
│       └── settings.html
│
└── static/
    ├── css/
    │   ├── style.css         # Main dark glassmorphism styles
    │   ├── admin.css
    │   └── animations.css
    ├── js/
    │   ├── main.js           # Typing effect, counters, slider, filters
    │   ├── particles.js      # Canvas particle background
    │   └── admin.js
    ├── images/               # Logo, favicon
    └── uploads/              # User-uploaded images (gitignored)
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/jkdatalab-website.git
cd jkdatalab-website/jkdatalab
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-very-secret-key
FLASK_ENV=development
DEBUG=True

DATABASE_URL=sqlite:///jkdatalab.db

ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password

MAIL_SERVER=smtp.zoho.in
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=kinjal@jkdatalab.com
MAIL_PASSWORD=your-zoho-app-password
MAIL_DEFAULT_SENDER=kinjal@jkdatalab.com
CONTACT_RECEIVER=kinjal@jkdatalab.com

SITE_URL=http://localhost:5000
SITE_NAME=JK Data Lab
```

### 5. Run the application

```bash
python app.py
```

The app will automatically create the database and seed it with sample data on first run.

- **Website:** http://localhost:5000
- **Admin Panel:** http://localhost:5000/admin/login

---

## Admin Panel

| Route | Description |
|-------|-------------|
| `/admin/login` | Admin login |
| `/admin/dashboard` | Overview stats and recent messages |
| `/admin/projects` | Add / edit / delete portfolio projects |
| `/admin/services` | Edit service descriptions and pricing |
| `/admin/testimonials` | Manage client testimonials |
| `/admin/blog` | Write and publish blog posts |
| `/admin/messages` | View contact form submissions, export CSV |
| `/admin/skills` | Manage skill proficiency bars |
| `/admin/settings` | Business info, social links, SEO, hero text |

Default credentials (set in `.env`):
- **Username:** `admin`
- **Password:** `JKAdmin@2026`

---

## Database Models

| Model | Purpose |
|-------|---------|
| `Admin` | Admin user with hashed password |
| `Project` | Portfolio projects with images and tech stack |
| `Service` | Service offerings with pricing tiers |
| `Testimonial` | Client reviews with star ratings |
| `BlogPost` | Blog articles with rich text content |
| `ContactMessage` | Contact form submissions |
| `SiteSetting` | Key-value store for all site settings |
| `Skill` | Skills with proficiency percentages |

---

## Deployment on Railway.app

1. Push the project to a GitHub repository
2. Go to [railway.app](https://railway.app) and create a new project from GitHub
3. Add the following environment variables in Railway's dashboard (same as `.env`)
4. Railway will auto-detect Python via Nixpacks and deploy using the `Procfile`

```
web: gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT
```

5. Connect your custom domain `jkdatalab.com` via Hostinger DNS → Railway settings

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask session secret key |
| `FLASK_ENV` | `development` or `production` |
| `DEBUG` | `True` or `False` |
| `DATABASE_URL` | SQLite path or PostgreSQL URL |
| `ADMIN_USERNAME` | Admin login username |
| `ADMIN_PASSWORD` | Admin login password |
| `MAIL_SERVER` | SMTP server (e.g. `smtp.zoho.in`) |
| `MAIL_PORT` | SMTP port (587 for TLS) |
| `MAIL_USE_TLS` | `True` or `False` |
| `MAIL_USERNAME` | SMTP login email |
| `MAIL_PASSWORD` | SMTP app password |
| `MAIL_DEFAULT_SENDER` | From address for outgoing emails |
| `CONTACT_RECEIVER` | Email address to receive contact form submissions |
| `SITE_URL` | Full site URL including scheme |
| `SITE_NAME` | Site display name |

---

## Security

- All admin routes protected with `@login_required`
- Passwords hashed with Werkzeug `pbkdf2`
- Contact form rate-limited to 3 submissions per IP per hour
- File uploads validated by extension (jpg, jpeg, png, gif, webp) and size (max 5 MB)
- SQL injection prevented via SQLAlchemy ORM
- XSS prevented via Jinja2 auto-escaping
- HTTPS enforced in production (Railway handles SSL)

---

## Contact

**JK Data Lab**
- Owner: Kinjal Jayantkumar Jayswal
- Email: kinjal@jkdatalab.com
- Phone: +91-9157938887
- Website: [www.jkdatalab.com](https://jkdatalab.com)
- Address: C 102 Aaron Elegance, New C.G. Road, Chandkheda, Ahmedabad, Gujarat - 382424, India
- MSME: UDYAM-GJ-01-0638170

---

*Built with Flask · Deployed on Railway.app · © 2026 JK Data Lab*
