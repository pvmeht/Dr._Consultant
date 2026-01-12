# DR. Consultant (HealthCO) Project Setup Guide

This guide will help you set up and run the HealthCO project, which consists of a Django Backend and a Tkinter Desktop Application.

## Prerequisites

*   Python 3.8 or higher installed.
*   Git (optional, for cloning).

## 1. Backend Setup

The backend is built with Django and Django REST Framework.

### Step 1: Navigate to the Backend Directory
Open your terminal and navigate to the `backend` folder:
```bash
cd backend
```

### Step 2: Install Dependencies
Since a `requirements.txt` is not yet present, install the necessary packages manually:
```bash
pip install django djangorestframework django-cors-headers requests pillow
```
*Note: `django-cors-headers` is recommended if you plan to connect from different origins, though redundant if same-origin. `requests` and `pillow` are common utilities.*

### Step 3: Apply Database Migrations
Initialize the SQLite database:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 4: Create an Admin User
Create a superuser to access the Django Admin interface:
```bash
python manage.py createsuperuser
```
Follow the prompts to set a username and password.

### Step 5: (Optional) Populate Initial Data
If you want to load some sample cities or data (if scripts are provided):
```bash
python populate_cities.py
python populate_pune_data.py
```

### Step 6: Run the Development Server
Start the backend server:
```bash
python manage.py runserver
```
The server will start at `http://127.0.0.1:8000/`.

---

## 2. Desktop Application Setup

The desktop application is a Python `tkinter` app that communicates with the backend via API.

### Step 1: Prerequisites
Ensure the **Backend Server is running** (Step 6 above) before starting the desktop app.

### Step 2: Navigate to Desktop App Directory
Open a *new* terminal window (keep the backend running in the first one) and navigate to:
```bash
cd desktop_app
```

### Step 3: Install Desktop Dependencies
The desktop app requires `requests` to communicate with the API. Tkinter is usually included with Python.
```bash
pip install requests
```

### Step 4: Run the Application
Launch the desktop interface:
```bash
python main.py
```

---

## 3. Usage Guide

### Web Portal
*   **Guest Access**: Visit `http://127.0.0.1:8000/` and click "Continue as Guest" to book appointments without logging in initially.
*   **Patient Login**: Log in to view dashboard, passed appointments, and profile.
*   **Admin Dashboard**: Log in with your superuser account at `http://127.0.0.1:8000/dashboard/admin/`.

### Desktop App
*   **Login**: Use your credentials to log in.
*   **Features**: View assigned appointments, complete consultations, and manage patient queues.

## Troubleshooting

*   **Connection Error**: If the desktop app fails to connect, ensure `API_URL` in `desktop_app/main.py` matches your running local server (default is `http://127.0.0.1:8000/api/`).
*   **Missing Libraries**: If you get an `ImportError`, use `pip install <package_name>` to fix it.
