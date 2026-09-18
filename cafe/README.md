# Brewline — Cafe Management System

Full‑stack Cafe Management System built with **Python Flask + MySQL + HTML/CSS/JS**.

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
