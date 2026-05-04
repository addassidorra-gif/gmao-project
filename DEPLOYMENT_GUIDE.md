# Guide de déploiement des migrations sur Render

## Résumé des changements appliqués (Mai 4, 2026)

### 🎨 Logo ENIB
- Ajout du logo ENIB en SVG dans `/static/images/enib_logo.svg`
- Intégration dans la barre latérale (`templates/base.html`)
- Styling CSS adapté (`static/css/app.css`)

### 📊 Nettoyage des champs
1. **Criticité** : Suppression de l'option dupliquée "Haute"
   - Avant : Très élevée, Élevée, Haute, Moyenne, Faible
   - Après : Très élevée, Élevée, Moyenne, Faible

2. **Priorité** : Refonte pour éviter les doublons avec Criticité
   - Avant : Urgente, Normale, Faible
   - Après : Très urgent, Urgent, Normal

3. **Localisations** : Consolidation des doublons
   - Labo industriel → Labo Industriel (GI)
   - Labo mécanique → Labo Mécanique
   - Labo Info → Labo Informatique
   - Atelier Robot → Labo Automatisme

## Migrations créées

### Equipment app
- **0002_alter_equipment_criticality.py** : ALTER FIELD pour les choices
- **0003_data_migration_update_criticality.py** : Conversion des données
- **0004_clean_locations.py** : Nettoyage des localisations

### Maintenance app
- **0003_alter_maintenance_priorities.py** : ALTER FIELD pour les choices
- **0004_data_migration_update_choices.py** : Conversion des données

## Procédure de déploiement

### Automatique (Recommended)
1. **Push vers Git** :
   ```bash
   git add .
   git commit -m "Apply ENIB logo, fix duplicate fields and standardize data"
   git push origin main
   ```

2. **Render déploie automatiquement** :
   - Le `build.sh` exécute automatiquement :
     ```bash
     python manage.py migrate
     python manage.py seed_demo_data
     ```

### Manuel (Si nécessaire)
Si les migrations ne s'appliquent pas, connectez-vous à la shell Render :
```bash
python manage.py migrate
python manage.py seed_demo_data
```

## Vérification après déploiement

1. Visitez https://gmao-project.onrender.com/
2. Vérifiez le logo ENIB dans la barre latérale
3. Vérifiez les listes déroulantes :
   - ✅ Criticité : pas de "Haute"
   - ✅ Priorité : "Très urgent", "Urgent", "Normal"
   - ✅ Localisations : pas de doublons

## Rollback (si nécessaire)

Si vous devez revenir en arrière :
```bash
git revert HEAD
git push origin main
# Les migrations Django géreront automatiquement les rollbacks
```

## Notes
- Les migrations ALTER FIELD appliquent les changements de choices à la base de données
- Les migrations RunPython convertissent les données existantes
- L'ordre des migrations est crucial : d'abord ALTER FIELD, puis RunPython
