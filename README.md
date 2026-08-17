# TechVault — Enterprise Computer & Tech Retail E-Commerce Platform

TechVault is a high-performance, full-stack computer and technology retail e-commerce platform inspired by the shopping experience and information architecture of leading tech retailers (such as Star Tech Bangladesh), featuring an original brand identity, dark modern tech aesthetics, and enterprise features.

---

## 🌟 Key Features

1. **Category Mega Menu & Hotline Bar**:
   - Hotline top bar, instant live search autocomplete, Wishlist link, Compare drawer, and Cart badge.
   - Multi-level Mega Menu navigation bar across Processors, Graphics Cards, Motherboards, RAM, SSDs, PSUs, Cases, and Laptops.

2. **Interactive PC Builder Compatibility Tool**:
   - Step-by-step custom PC assembly (CPU, Motherboard, RAM, Storage, GPU, PSU, Casing).
   - Real-time total power wattage calculation, total build cost summary, and 1-click bulk cart addition.

3. **Dynamic Category EAV Specification System**:
   - Entity-Attribute-Value architecture allowing different categories to feature distinct technical specifications without hardcoding columns into models.
   - Dynamic AJAX multi-select sidebar filtering (Brands, Categories, Price Range, Stock, Socket, VRAM, RAM Standard).

4. **Live Autocomplete Product Search**:
   - Asynchronous AJAX search popup (`/api/search/live/?q=...`) returning matching products with images, prices, model numbers, and brands.

5. **Side-by-Side Product Comparison Matrix**:
   - Compare up to 4 selected products across technical specifications, pricing, brand, and stock status.

6. **Wishlist & Cart Engines**:
   - Wishlist persistence with 1-click "Move to Cart".
   - AJAX Cart with quantity steppers, item removal, and Coupon Engine (`WELCOME10`, `TECH50`).

7. **User Authentication & Customer Dashboard**:
   - User Registration, Login, Logout, Profile management, and Shipping Address book.
   - Order history with tracking timeline (`Pending` -> `Confirmed` -> `Processing` -> `Shipped` -> `Delivered`).

8. **Server-Side Security & Validation**:
   - Server-side stock validation and price enforcement (never trusting frontend prices).
   - `X-CSRFToken` header protection on all asynchronous Fetch API requests.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11 / Django 5.0 / PostgreSQL (`dj-database-url`, `psycopg2-binary`)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript (Fetch API / AJAX)
- **Serving & Static Assets**: Gunicorn & WhiteNoise (`CompressedManifestStaticFilesStorage`)

---

## 🚀 Quickstart & Local Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Seed Demo Inventory & Coupons**:
   ```bash
   python manage.py seed_tech_store
   ```

4. **Collect Static Assets**:
   ```bash
   python manage.py collectstatic --no-input
   ```

5. **Start Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.

---

## ☁️ Production Deployment (Render / Railway)

The project includes pre-configured deployment files:
- `Procfile`: Launches `gunicorn core.wsgi:application`
- `build.sh`: Automatically runs `pip install`, `collectstatic`, and `migrate` during cloud deployment.
