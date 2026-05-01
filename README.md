# GMAO ENIB

Application web GMAO simple avec :

- Django
- Django REST Framework
- JWT
- PostgreSQL Supabase ou SQLite en secours
- Interface HTML/CSS/JavaScript avec templates Django

## 1. Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configuration

Copier `.env.example` en `.env` si vous voulez utiliser Supabase.

Si `DATABASE_URL` est vide, Django utilisera `db.sqlite3`.

## 3. Lancer le projet

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data
python manage.py runserver
```

## 4. API

- `POST /api/auth/login/`
- `POST /api/auth/refresh/`
- `POST /api/auth/logout/`
- `GET /api/auth/me/`
- `GET /api/users/`
- `GET /api/equipements/`
- `GET /api/incidents/`
- `GET /api/interventions/`
- `GET /api/audit-logs/`

## 5. Interface web

- `/login/`
- `/dashboard/`
- `/equipements/`
- `/pannes/`
- `/interventions/`
- `/utilisateurs/`

## 6. Comptes de démonstration

Commande :

```bash
python manage.py seed_demo_data
```

Comptes créés :

- `admin@enib.tn` / `admin123`
- `responsable@enib.tn` / `resp123`
- `operateur@enib.tn` / `oper123`
- `technicien@enib.tn` / `tech123`
