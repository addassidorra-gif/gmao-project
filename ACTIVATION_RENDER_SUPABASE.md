# Activation des changements sur Render et Supabase

## 1. Vérifier localement

Dans PowerShell :

```powershell
cd C:\Users\HP\OneDrive\Bureau\GMAO-CODEX\gmao_project
python manage.py check
python manage.py migrate
python manage.py audit_supabase_connection --write-test
python manage.py collectstatic --no-input --dry-run
```

Si `audit_supabase_connection` affiche `sqlite`, le projet local n'utilise pas encore Supabase.

## 2. Configurer Supabase dans Render

Dans Render > Web Service > Environment, ajouter ou corriger :

```text
DEBUG=False
SECRET_KEY=une-valeur-secrete-longue
ALLOWED_HOSTS=gmao-project.onrender.com
CSRF_TRUSTED_ORIGINS=https://gmao-project.onrender.com
DATABASE_URL=postgresql://postgres.PROJECT_REF:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres?sslmode=require
ADMIN_EMAIL=admin@enib.tn
ADMIN_PASSWORD=un-mot-de-passe-fort
DJANGO_SUPERUSER_FULL_NAME=Administrateur ENIB
```

Important :

- Ne pas mettre `DATABASE_URL=` dans la valeur Render, seulement l'URL.
- Ne pas coller une commande `psql`.
- Ne pas ajouter de guillemets.
- Le mot de passe Supabase doit être encodé si nécessaire.
- Ne jamais laisser `ADMIN_PASSWORD` avec une valeur de test.

## 3. Déployer

Après commit et push GitHub :

```powershell
git add .
git commit -m "Add account approval, Supabase audit, and PDF Excel exports"
git push origin main
```

Si ta branche est `master` :

```powershell
git push origin master
```

Render doit relancer automatiquement le build. Sinon, cliquer sur `Manual Deploy`.

## 4. Vérifier après déploiement

Dans les logs Render, vérifier que ces étapes passent :

```text
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn config.wsgi:application
```

Le build ne charge plus automatiquement les données de démonstration.

Sur le site :

- Créer un compte depuis l'écran de connexion.
- Se connecter en admin.
- Aller dans Utilisateurs.
- Vérifier que le compte est en attente.
- Cliquer sur Accepter ou Refuser.
- Tester les exports PDF/Excel selon le rôle.

## 5. Données d'exemple

Ne pas lancer `seed_demo_data` sur Supabase sauf si vous voulez vraiment insérer les données de démonstration.

Commande protégée :

```powershell
python manage.py seed_demo_data
```

Sur PostgreSQL/Supabase, cette commande s'arrête automatiquement.

Forcer volontairement :

```powershell
python manage.py seed_demo_data --allow-production
```
