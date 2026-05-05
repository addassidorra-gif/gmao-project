# Guide des Comptes de Démonstration - GMAO ENIB

## 🎯 Objectif

Les comptes de démonstration permettent de tester rapidement l'application GMAO ENIB avec différents rôles utilisateur sans créer de nouveaux comptes.

## 📋 Comptes disponibles

### 1. **Admin** 👨‍💼
- **Email** : `admin@enib.tn`
- **Mot de passe** : `admin123`
- **Accès** : Accès complet à toutes les fonctionnalités
- **Permissions** :
  - Gestion complète des utilisateurs
  - Gestion des équipements
  - Gestion des pannes et interventions
  - Consultation des audits

### 2. **Responsable** 📊
- **Email** : `responsable@enib.tn`
- **Mot de passe** : `resp123`
- **Accès** : Gestion complète (sauf administration utilisateurs)
- **Permissions** :
  - Gestion des équipements
  - Gestion des pannes et interventions
  - Rapports de maintenance

### 3. **Opérateur** 🔧
- **Email** : `operateur@enib.tn`
- **Mot de passe** : `oper123`
- **Accès** : Signalement des pannes
- **Permissions** :
  - Créer des pannes
  - Consulter les équipements
  - Voir l'historique des interventions

### 4. **Technicien** 🛠️
- **Email** : `technicien@enib.tn`
- **Mot de passe** : `tech123`
- **Accès** : Gestion des interventions
- **Permissions** :
  - Consulter et traiter les pannes assignées
  - Créer et clôturer des interventions
  - Rédiger des rapports techniques

## 🚀 Utilisation

### Via l'interface web

1. Allez sur https://gmao-project.onrender.com/
2. Cliquez sur l'un des boutons des comptes de démonstration
3. Les identifiants seront pré-remplis automatiquement
4. Cliquez sur "Se connecter"

### Via la ligne de commande (local)

```bash
# Créer/recréer les comptes de démonstration
python manage.py create_demo_accounts

# Vérifier que les comptes existent
python manage.py shell
>>> from users.models import User
>>> User.objects.filter(email__contains='enib.tn').values('email', 'full_name', 'role')
```

## 📝 Données de démonstration

Les comptes de démonstration ont accès à :

- **9 équipements** de test dans différents laboratoires
- **3 pannes** avec différents statuts
- **3 interventions** complètes avec rapports

## ⚠️ Important

- **Les comptes de démonstration sont des comptes partagés** - Ne pas modifier les mots de passe
- **Données de test** - Toutes les données créées peuvent être supprimées à tout moment
- **Droits limités** - Les données de chaque rôle sont filtrées selon leurs permissions

## 🔄 Réinitialiser les comptes

Si les mots de passe ont été modifiés, vous pouvez les réinitialiser avec :

```bash
python manage.py create_demo_accounts
```

Cette commande :
- Recrée tous les comptes de démonstration
- Réinitialise les mots de passe aux valeurs par défaut
- Active les comptes désactivés

## 📚 Pour en savoir plus

- Consultez `DEPLOYMENT_GUIDE.md` pour les instructions de déploiement
- Consultez `CHANGES.md` pour l'historique des modifications
- Consultez `README.md` pour la documentation générale du projet
