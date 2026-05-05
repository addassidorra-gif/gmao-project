# Rapport de vérification Supabase et fonctionnalités GMAO

Date : 2026-05-04

## Résumé exécutif

L'application est structurée pour utiliser une base réelle via Django ORM. Si `DATABASE_URL` pointe vers Supabase, les opérations DRF existantes écrivent bien dans la base PostgreSQL/Supabase. En revanche, plusieurs exigences annoncées ne sont pas encore complètement implémentées côté produit :

- Export PDF et Excel : implémenté via endpoints API sécurisés.
- Création de compte avec validation administrateur : implémentée avec statut `en attente / accepté / refusé`.
- Bascule contrôlée données réelles / mock data : les données de démonstration ne sont pas un mode runtime, mais la commande de seed est maintenant protégée sur PostgreSQL/Supabase.
- Connexion Supabase live : vérifiable seulement avec un `DATABASE_URL` valide dans l'environnement d'exécution. Les logs Render reçus indiquent actuellement un `DATABASE_URL` mal formé.

## Connexion Supabase

Le fichier `config/settings.py` configure la base via la variable d'environnement `DATABASE_URL`. Cela signifie que l'application n'utilise pas directement le SDK Supabase côté navigateur ; elle passe par Django, DRF et PostgreSQL.

État constaté :

- `DATABASE_URL` vide ou absent : fallback SQLite local.
- `DATABASE_URL` PostgreSQL valide : utilisation de PostgreSQL, compatible Supabase.
- Logs Render fournis : échec pendant `migrate` avec `UnicodeError: label empty or too long`, ce qui indique très probablement une URL de base mal copiée dans Render.

Commande de vérification ajoutée :

```powershell
python manage.py audit_supabase_connection
```

Test CRUD réel, avec création puis suppression d'une ligne temporaire :

```powershell
python manage.py audit_supabase_connection --write-test
```

Cette commande n'affiche pas de mot de passe et ne conserve aucune ligne de test.

## CRUD réel

Les endpoints suivants utilisent des `ModelViewSet` DRF et donc la base réelle configurée dans Django :

- Équipements : création, lecture, modification, suppression via `EquipementViewSet`.
- Pannes : création, lecture, modification, suppression via `IncidentViewSet`.
- Interventions : création, lecture, modification, suppression via `InterventionViewSet`.
- Utilisateurs : gestion admin via `UserViewSet`.
- Audit : lecture via `AuditLogViewSet`.

Conclusion : les CRUD ne sont pas uniquement simulés côté interface si le site est connecté à PostgreSQL/Supabase. Ils deviennent simulés uniquement si l'environnement pointe vers SQLite local ou si les données affichées proviennent d'un seed de démonstration.

## Cohérence des données

Les vues API lisent les données depuis l'ORM. Le dashboard et les tableaux SPA chargent les collections via API, puis calculent les indicateurs côté navigateur. La normalisation des libellés de laboratoires a été améliorée pour éviter des doublons comme `Laboratoire Génie Industriel` écrit sous plusieurs formes.

Risque restant :

- Le dashboard charge des listes complètes. Avec beaucoup de données, il faudra ajouter pagination, filtres serveur et index.
- Les données déjà présentes dans Supabase peuvent encore contenir des libellés historiques dupliqués si elles n'ont pas été nettoyées en base.

## Exports

État actuel :

- CSV : présent dans les vues classiques.
- PDF : présent via API JWT.
- Excel `.xlsx` : présent via API JWT.

Endpoints :

- `/api/equipements/export/pdf/`
- `/api/equipements/export/xlsx/`
- `/api/incidents/export/pdf/`
- `/api/incidents/export/xlsx/`
- `/api/interventions/export/pdf/`
- `/api/interventions/export/xlsx/`

Conclusion : l'exigence PDF/Excel est maintenant satisfaite côté API. Les exports utilisent les mêmes querysets visibles par rôle.

## Mock data

État actuel :

- Les comptes de démonstration dans `spa.js` servent à préremplir les identifiants.
- La commande de seed, si présente dans l'environnement utilisé, insère des données dans la base active.
- Il n'y a pas de vrai sélecteur `mock / réel`.

Conclusion : les mock data ne sont pas un mode séparé dans l'interface, mais elles ne sont plus injectables par erreur en production. Sur PostgreSQL/Supabase ou `DEBUG=False`, `seed_demo_data` s'arrête sauf si `--allow-production` est explicitement fourni.

## Comptes utilisateurs et validation admin

État actuel :

- Le modèle utilisateur contient un rôle, `is_active` et `approval_status`.
- Un utilisateur peut demander un compte via `/api/auth/register/`.
- Le compte créé est `pending` et `is_active=False`.
- L'admin peut accepter ou refuser depuis `/api/users/<id>/approve/` et `/api/users/<id>/reject/`.
- La connexion est refusée tant que le compte n'est pas accepté.

Conclusion : la création de comptes avec validation admin est maintenant opérationnelle côté API et visible dans le dashboard utilisateurs.

## Gestion des erreurs

L'API possède une base de gestion d'erreurs DRF. Côté interface, il faut encore vérifier les cas suivants en environnement réel :

- Perte réseau.
- Base indisponible.
- JWT expiré.
- Accès refusé par rôle.
- Erreur de validation formulaire.

Recommandation : afficher des messages utilisateur homogènes et conserver les détails techniques dans les logs uniquement.

## Sécurité

Les permissions applicatives par rôle sont présentes côté DRF. Les règles critiques sont contrôlées côté API, ce qui empêche de tricher simplement via l'interface.

Point important Supabase :

- Si Django se connecte à Supabase avec une connexion PostgreSQL serveur, la sécurité principale est l'API Django, pas les politiques RLS Supabase côté navigateur.
- Les clés ou URLs sensibles ne doivent jamais être exposées dans le JavaScript public.
- Si Supabase RLS est activé, il faut vérifier qu'elle ne bloque pas les migrations Django et qu'elle correspond au mode de connexion utilisé.

## Performances

La commande `audit_supabase_connection` mesure les temps de réponse simples (`SELECT 1` et `COUNT`). Pour une mesure complète, il faut tester :

- Liste équipements avec beaucoup de lignes.
- Dashboard avec beaucoup de pannes/interventions.
- Export de données volumineuses.
- Création/modification simultanée par plusieurs utilisateurs.

Recommandations :

- Ajouter pagination API.
- Ajouter filtres serveur.
- Ajouter index sur `code`, `status`, `location`, `created_at`, `operator`, `technician`.
- Éviter de charger toute la base dans le dashboard.

## Logs et audit

L'application crée des logs métier pour les actions importantes : login, logout, création, modification et suppression. Il reste à compléter l'observabilité technique :

- Logs Render pour erreurs serveur.
- Logs Supabase pour requêtes lentes ou erreurs SQL.
- Alertes sur échecs de connexion.
- Journalisation des refus d'accès.

## Recommandations prioritaires

1. Corriger `DATABASE_URL` dans Render avec l'URL PostgreSQL Supabase exacte.
2. Lancer `python manage.py audit_supabase_connection --write-test` en local avec le même `DATABASE_URL`.
3. Ajouter pagination, filtres serveur et index.
4. Nettoyer en base les libellés dupliqués de laboratoires.
5. Documenter clairement le mode production et le mode données d'exemple.
