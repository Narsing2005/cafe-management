# Brewline — Cafe Management System

Full‑stack Cafe Management System built with **Python Flask + MySQL + HTML/CSS/JS**.
Warm‑cafe themed UI (palette: `#1a1410`, `#3d2817`, `#c9882a`, `#f5e6d3`).

## Features
- Admin login / logout, Flask session, form validation, flash messages
- Dashboard: total orders, revenue, menu items, recent orders, quick actions, chart (Chart.js)
- Menu management: add/edit/delete items, image upload, category, price, search + filter
- Order management: create order (multi‑item), live total in JS, status updates, history, invoice print/export
- Customer interface: browse menu, cart (localStorage), place order, bill summary
- Responsive sidebar, navbar, footer, glassmorphism cards, animations
- Custom 404 + login error pages

## Stack
- Backend: Flask 3, Flask-MySQLdb, bcrypt
- DB: MySQL (XAMPP)
- Frontend: HTML5, CSS3, vanilla JS, Chart.js (CDN), Font Awesome (CDN), Google Fonts

## Setup (VS Code + XAMPP)

1. **Start MySQL** in XAMPP control panel.
2. **Create database** — open phpMyAdmin → Import → select `database/schema.sql`.
   Default admin: **username `admin` / password `admin123`**.
3. **Create a virtualenv & install deps**
   ```bash
   python -m venv venv
   # Windows: venv\Scripts\activate
   source venv/bin/activate
   pip install -r requirements.txt
   ```
   > On Windows, if `mysqlclient` fails: `pip install mysqlclient` from a wheel
   > (https://www.lfd.uci.edu/~gohlke/pythonlibs/#mysqlclient) or use
   > `pip install pymysql` and change `MYSQL_*` config to use pymysql.
4. **Configure DB** — edit `app/config.py` (defaults match XAMPP: host `localhost`,
   user `root`, password ``, db `cafe_db`).
5. **Run**
   ```bash
   python run.py
   ```
   Open <http://localhost:5000>.

## Folder structure
```
cafe/
├── run.py
├── database/
│   └── schema.sql
└── app/
    ├── __init__.py
    ├── config.py
    ├── routes.py
    ├── static/
    │   ├── css/style.css
    │   ├── js/main.js  
    └── templates/
        ├── base.html
        ├── login.html
        ├── dashboard.html
        ├── menu.html
        ├── menu_form.html
        ├── orders.html
        ├── order_new.html
        ├── order_view.html
        ├── customer.html
        ├── 404.html
        └── login_error.html
```
