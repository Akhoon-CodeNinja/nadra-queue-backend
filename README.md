# NADRA Queue Management System - Backend 🏢🎫

This is the backend repository for the **NADRA Queue Management System**, built to digitize and streamline the token booking process for NADRA centers. This API serves the Flutter mobile application, handling token generation, user profiles, office locations, and AI chatbot responses.

## 🚀 Tech Stack
* **Language:** Python 3.x
* **Framework:** Django & Django REST Framework (DRF)
* **Database:** SQLite (Development) / PostgreSQL (Production ready)

## ✨ Core Features
* **User Authentication:** Secure profile management.
* **Smart Token Booking:** Book tokens for specific districts and offices.
* **Real-time Queue Status:** Track active, completed, or cancelled tokens.
* **Geographical Data:** APIs for fetching cities, districts, and NADRA offices.
* **AI Chatbot Integration:** Endpoint to process user queries in Urdu/English regarding NADRA services.

## ⚙️ Installation & Setup (Local Development)

Follow these steps to run the backend on your local machine:

**1. Clone the repository:**
```bash
git clone [https://github.com/yourusername/nadra-queue-backend.git](https://github.com/yourusername/nadra-queue-backend.git)
cd nadra-queue-backend
```

**2. Create and activate a virtual environment:**
```bash
python -m venv env
# On Windows
env\Scripts\activate
# On Mac/Linux
source env/bin/activate
```

**3. Install dependencies:**
```bash
pip install -r requirements.txt
```

**4. Run database migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Create a superuser (Admin):**
```bash
python manage.py createsuperuser
```

**6. Start the development server:**
```bash
python manage.py runserver
```
The API will be available at `http://127.0.0.1:8000/`.

## 📡 Key API Endpoints
* `GET /api/cities/` - Fetch all available cities.
* `GET /api/districts/?city_id=<id>` - Fetch districts for a specific city.
* `GET /api/offices/?district_id=<id>` - Fetch NADRA offices.
* `POST /api/tokens/create/` - Book a new token.
* `GET /api/tokens/my-tokens/?user_id=<id>` - Fetch user's token history.

## 👨‍💻 Author
**Dilawer Khan** - *AI & Data Science Engineer (Team Lead)*
