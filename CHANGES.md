# Changelog - Mai 4, 2026

## 🎯 Objectifs
- Intégrer le logo ENIB dans l'application
- Éliminer les champs dupliqués dans les formulaires
- Standardiser les données et améliorer l'expérience utilisateur

## ✅ Changements appliqués

### 1. Intégration du logo ENIB
**Fichiers modifiés :**
- `static/images/enib_logo.svg` (nouveau)
- `templates/base.html`
- `static/css/app.css`

**Détails :**
- Logo ENIB SVG créé et intégré dans la barre latérale
- Remplace le placeholder "G" par le logo officiel
- Styling CSS adapté pour un affichage professionnel

### 2. Refonte des priorités

**Avant :**
```
Urgente
Normale
Faible
```

**Après :**
```
Très urgent
Urgent
Normal
```

**Raison :** Éviter la confusion avec le champ "Criticité" qui avait aussi "Faible"

**Fichiers affectés :**
- `maintenance/models.py` - Incident.Priority et Intervention
- `maintenance/migrations/0003_alter_maintenance_priorities.py`
- `maintenance/migrations/0004_data_migration_update_choices.py`
- `maintenance/management/commands/seed_demo_data.py`

### 3. Suppression de "Haute" dans les criticités

**Avant :**
```
Très élevée
Élevée
Haute         ← SUPPRIMÉ (doublon avec Élevée)
Moyenne
Faible
```

**Après :**
```
Très élevée
Élevée
Moyenne
Faible
```

**Fichiers affectés :**
- `equipment/models.py`
- `maintenance/models.py`
- `equipment/migrations/0002_alter_equipment_criticality.py`
- `equipment/migrations/0003_data_migration_update_criticality.py`
- `maintenance/migrations/0004_data_migration_update_choices.py`

### 4. Standardisation des localisations

**Consolidations appliquées :**
| Avant | Après |
|-------|-------|
| Labo industriel | Labo Industriel (GI) |
| Labo industriel (GI) | Labo Industriel (GI) |
| Labo mécanique | Labo Mécanique |
| Labo Mécanique | Labo Mécanique |
| Labo matériaux (GM) | Labo Matériaux (GM) |
| Labo Automatisme | Labo Automatisme |
| Atelier Robot | Labo Automatisme |
| Labo Info | Labo Informatique |

**Fichiers affectés :**
- `maintenance/management/commands/seed_demo_data.py`
- `equipment/migrations/0004_clean_locations.py`

## 📊 Migrations Django

### Equipment app
| Migration | Type | Description |
|-----------|------|-------------|
| 0002_alter_equipment_criticality.py | Schema | ALTER FIELD pour les choices |
| 0003_data_migration_update_criticality.py | Data | Conversion Haute → Élevée |
| 0004_clean_locations.py | Data | Nettoyage des localisations |

### Maintenance app
| Migration | Type | Description |
|-----------|------|-------------|
| 0003_alter_maintenance_priorities.py | Schema | ALTER FIELD pour Incident et Intervention |
| 0004_data_migration_update_choices.py | Data | Conversion priorités et criticités |

## 🔄 Ordre d'exécution

1. **Schema migrations** (ALTER FIELD) :
   - Permet à Django d'accepter les anciennes données
   - Ajoute les nouvelles choices aux champs

2. **Data migrations** (RunPython) :
   - Convertit les valeurs existantes
   - Crée la cohérence dans la base de données

## ✨ Améliorations de l'UX

- Logo professionnel visible dans la barre latérale
- Listes déroulantes sans termes redondants
- Terminologie cohérente à travers l'application
- Pas de doublons de localisations

## 📋 Checklist de déploiement

- [ ] Git push des changements
- [ ] Vérification du déploiement Render
- [ ] Vérification du logo dans la barre latérale
- [ ] Test des formulaires (création/modification)
- [ ] Vérification des listes déroulantes
- [ ] Vérification de l'absence de doublons

## 🔐 Notes de compatibilité

- **Reversible** : Les migrations incluent des fonctions reverse()
- **Idempotent** : Les data migrations peuvent être appliquées plusieurs fois
- **Safe** : Les ALTER FIELD n'affectent que les definitions, pas les données existantes

## 📞 Support

Pour des questions ou problèmes après le déploiement, consultez `DEPLOYMENT_GUIDE.md`
