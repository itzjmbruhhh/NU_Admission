# NU Admission - Smart Admission System

A Django-based student admission system for NU Lipa, allowing student registration, admin management, and future ML integration for processing applications.

---

## **Setup Instructions**

### 1. Clone the Repository
```bash
git clone https://github.com/itzjmbruhhh/NU_Admission.git
cd NU_Admission/dmission_portal
```

---

### 2. Create a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

---

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 4. Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create your admin account.

---

### 6. Run the Development Server
```bash
python manage.py runserver
```

- Open your browser at `http://127.0.0.1:8000/` for the homepage.

Django URL Patterns
-------------------

URL Path                  | View Function      | Template / Notes
--------------------------|------------------|-----------------------------
''                        | index             | templates/index.html
'register/'               | register          | templates/registration.html
'loginAdmin/'             | loginAdmin        | templates/login.html
'adminDash/'              | adminDash         | templates/admin.html / dashboard
'student/<int:pk>/'      | student_detail    | templates/student_detail.html
'super_admin/'            | admin.site.urls   | Django Admin Panel

---

## **Loading Data from Excel (.xlsx)**

1. Make sure your `.xlsx` file matches the `Student` model columns.
2. Use Django Admin with `django-import-export` or your custom import script:
   - Go to **Admin Panel > Students > Import**.
   - Select your Excel file and upload.
   - If you allow empty fields, ensure `Student` model fields have `blank=True, null=True`.

---

## **Folder Overview**

- `admissions/` → Django app for student registration and admin management.
- `templates/` → HTML templates for index, registration, login, and admin views.
- `static/` → CSS, JS, images, and other static assets.
- `requirements.txt` → Python dependencies (Django, django-import-export, etc.)

---

## **Tips / Notes**

- Static files are served via `{% static %}` in templates. Make sure `STATICFILES_DIRS` and `STATIC_URL` are configured in `settings.py`.
- To reset the database, you can delete `db.sqlite3` and re-run migrations.
- For production deployment, configure `ALLOWED_HOSTS`, database settings, and static files properly.

anuga