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

## 7. Déploiement Render

Le projet contient une configuration Render prête à l'emploi :

- `render.yaml` : configuration du service web
- `build.sh` : installation, collecte des fichiers statiques et migrations
- `.python-version` : version Python recommandée

Variables d'environnement à configurer sur Render si vous ne passez pas par `render.yaml` :

```text
DEBUG=False
SECRET_KEY=une-cle-secrete-longue
ALLOWED_HOSTS=gmao-project.onrender.com
CSRF_TRUSTED_ORIGINS=https://gmao-project.onrender.com
DATABASE_URL=postgresql://...
```

Commandes Render :

```bash
bash build.sh
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Après le premier déploiement avec une base PostgreSQL, exécuter une seule fois :

```bash
python manage.py seed_demo_data
```
