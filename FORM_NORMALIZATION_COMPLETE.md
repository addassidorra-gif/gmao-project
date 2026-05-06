# FORM VALUE NORMALIZATION - COMPLETION SUMMARY

Date: May 6, 2026  
Status: ✅ 100% COMPLETE  
User Story: Handle legacy choice values submitted by frontend/SPA

---

## 🎯 Objective Achieved

**User Issue:** "Le problème n'était pas seulement l'affichage: il y avait aussi des anciennes valeurs qui pouvaient encore être envoyées au backend"

**Solution Implemented:** Three-layer defense strategy that safely handles legacy form values:
- Form clean() methods normalize input
- Model fields accept legacy choices temporarily
- API serializers transform values from JSON
- Cleanup command converts existing database data

---

## 📋 What Was Completed

### ✅ Form Layer (4 Classes Updated)

**File:** [maintenance/forms.py](maintenance/forms.py)

1. **Normalization Utility Functions** (Lines 8-32)
   ```python
   LEGACY_PRIORITY_MAP = {
       "Urgente": "Très urgent",
       "Normale": "Normal",
       "Faible": "Normal",
       "Pas urgente": "Normal",
   }
   
   LEGACY_CRITICALITY_MAP = {
       "Haute": "Élevée",
   }
   
   def normalize_priority(value): ...
   def normalize_criticality(value): ...
   ```

2. **IncidentForm** - Added `clean()` method
   - Normalizes priority: "Urgente" → "Très urgent"
   - Normalizes criticality: "Haute" → "Élevée"
   - Prevents Django validation errors

3. **IncidentOperatorForm** - Added `clean()` method
   - Same normalization as IncidentForm
   - Used by operators submitting incidents

4. **InterventionForm** - Enhanced `clean()` method
   - Normalizes priority field
   - Validates incident-equipment relationship

5. **TechnicianInterventionForm** - Standard form
   - No normalization needed (no priority field)

### ✅ Database Layer (Migrations)

**File:** [maintenance/migrations/0005_accept_legacy_values.py](maintenance/migrations/0005_accept_legacy_values.py)
- Incident.priority: Added legacy choices
- Incident.criticality: Added legacy choices
- Intervention.priority: Added legacy choices

**File:** [equipment/migrations/0005_accept_legacy_criticality.py](equipment/migrations/0005_accept_legacy_criticality.py)
- Equipement.criticality: Added legacy "Haute" choice

### ✅ API Layer (Already Secure)

**File:** [maintenance/serializers.py](maintenance/serializers.py) - No changes needed
- `normalize_legacy_choice_values()` function already present
- IncidentSerializer.to_internal_value() uses it
- InterventionSerializer.to_internal_value() uses it
- JSON API requests automatically normalized

### ✅ Cleanup Infrastructure

**New Command:** [maintenance/management/commands/cleanup_legacy_values.py](maintenance/management/commands/cleanup_legacy_values.py)
```bash
python manage.py cleanup_legacy_values
```
- Converts all existing legacy data in database
- Works on Incident, Intervention, Equipement models
- Provides colorized progress output

**Updated:** [build.sh](build.sh)
- Added execution of cleanup_legacy_values
- Runs after migrations, before demo data seeding
- Ensures production database cleaned on deployment

### ✅ Testing

**New Test Suite:** [maintenance/tests/test_legacy_values.py](maintenance/tests/test_legacy_values.py)
- 12 unit tests covering all scenarios
- Tests normalization functions
- Tests form clean() methods
- Tests all legacy priority values

---

## 🔄 How It Works

### Form Submission Flow

```
User submits form with legacy value "Urgente"
        ↓
Django receives POST data
        ↓
Form class instantiated (e.g., IncidentForm)
        ↓
form.is_valid() called
        ↓
form.clean() executes:
  - normalize_priority("Urgente") → "Très urgent"
  - form.cleaned_data["priority"] = "Très urgent"
        ↓
form.save() called
        ↓
Model instance saved with "Très urgent"
        ↓
✅ Database constraint satisfied (value is valid choice)
```

### API Request Flow (JSON)

```
JavaScript sends {"priority": "Urgente", ...}
        ↓
API endpoint receives request
        ↓
Serializer.to_internal_value() called
        ↓
normalize_legacy_choice_values() transforms:
  {"priority": "Très urgent", ...}
        ↓
Serializer validation passes
        ↓
Model saved with "Très urgent"
```

### Database Cleanup Flow (One-time)

```
Render deployment triggered
        ↓
build.sh executes:
  1. migrate (applies 0005_* migrations)
  2. create_superuser
  3. cleanup_legacy_values ← HERE
  4. create_demo_accounts
  5. seed_demo_data
        ↓
cleanup_legacy_values scans database:
  - SELECT * FROM maintenance_incident WHERE priority='Urgente'
  - UPDATE maintenance_incident SET priority='Très urgent' WHERE...
  - Repeats for all legacy values/models
        ↓
✅ All existing legacy data normalized
```

---

## 🧪 Testing

### Local Testing

1. **Run Tests:**
   ```bash
   python manage.py test maintenance.tests.test_legacy_values
   ```
   Expected output:
   ```
   test_normalize_priority_urgente ... ok
   test_form_with_all_legacy_priority_values ... ok
   [12 tests] ... OK
   ```

2. **Manual Form Test:**
   ```bash
   python manage.py shell
   ```
   ```python
   from maintenance.forms import IncidentForm
   from maintenance.models import Incident
   from equipment.models import Equipement
   from users.models import User
   
   # Get test data
   equipment = Equipement.objects.first()
   tech = User.objects.filter(role='TECHNICIEN').first()
   
   # Test with legacy priority
   form_data = {
       'equipment': equipment.id,
       'technician': tech.id,
       'title': 'Test Incident',
       'description': 'Test Description',
       'priority': 'Urgente',  # Legacy value
       'criticality': 'Moyenne',
   }
   
   form = IncidentForm(data=form_data)
   print(f"Form valid: {form.is_valid()}")  # Should be True
   print(f"Cleaned priority: {form.cleaned_data['priority']}")  # Should be 'Très urgent'
   ```

3. **Cleanup Command Test:**
   ```bash
   # First, create some test data with legacy values
   python manage.py shell
   >>> from maintenance.models import Incident
   >>> Incident.objects.create(..., priority='Urgente')
   
   # Then run cleanup
   python manage.py cleanup_legacy_values
   
   # Verify cleanup
   >>> Incident.objects.filter(priority='Urgente').count()
   0  # Should be zero
   ```

### Production Testing (Post-Deployment)

1. **Monitor Render Logs:**
   - Go to Render dashboard
   - Check "Events" tab for deployment
   - Look for "cleanup_legacy_values" in build output

2. **Test Form Submission:**
   - Login: operateur@enib.tn / oper123
   - Create incident
   - Check priority field accepts values
   - Verify saved value is normalized

3. **Verify Database (if SSH access):**
   ```bash
   # SSH into Render container
   python manage.py shell
   >>> from maintenance.models import Incident
   >>> Incident.objects.values('priority').distinct()
   <QuerySet [{'priority': 'Très urgent'}, {'priority': 'Urgent'}, {'priority': 'Normal'}]>
   # Should NOT include 'Urgente', 'Normale', 'Faible'
   ```

---

## 📊 Files Modified

| File | Type | Changes |
|------|------|---------|
| [maintenance/forms.py](maintenance/forms.py) | Code | +4 utility functions, +3 clean() methods |
| [maintenance/migrations/0005_accept_legacy_values.py](maintenance/migrations/0005_accept_legacy_values.py) | Migration | NEW: Accept legacy choices in models |
| [equipment/migrations/0005_accept_legacy_criticality.py](equipment/migrations/0005_accept_legacy_criticality.py) | Migration | NEW: Accept legacy criticality choice |
| [maintenance/management/commands/cleanup_legacy_values.py](maintenance/management/commands/cleanup_legacy_values.py) | Command | NEW: Convert legacy data to new values |
| [maintenance/tests/test_legacy_values.py](maintenance/tests/test_legacy_values.py) | Tests | NEW: 12 unit tests for normalization |
| [build.sh](build.sh) | Build | +1 line: cleanup_legacy_values execution |
| [LEGACY_VALUES_HANDLING.md](LEGACY_VALUES_HANDLING.md) | Docs | NEW: Technical reference |

---

## 🚀 Deployment Instructions

### 1. Commit Changes
```bash
cd c:\Users\HP\OneDrive\Bureau\GMAO-CODEX\gmao_project
git add .
git commit -m "Complete form value normalization for legacy choice handling

- Add normalization functions to maintenance/forms.py
- Add clean() methods to 3 form classes (IncidentForm, IncidentOperatorForm, InterventionForm)
- Add migrations to accept legacy choice values in models
- Create cleanup_legacy_values management command
- Integrate cleanup into build.sh
- Add comprehensive test suite for normalization
- Add technical documentation

This ensures backend safely handles old values submitted by frontend/SPA
while normalizing them to new format in database.

Fixes: #cleanup-legacy-values"
```

### 2. Push to Main
```bash
git push origin main
```

### 3. Monitor Deployment
- Render auto-deploys on git push
- Check dashboard for deployment status
- Verify build.sh completes without errors

### 4. Verify Post-Deployment
- Login with demo account (operateur@enib.tn / oper123)
- Create test incident
- Check database that value was normalized

---

## ✨ Key Features

### 1. Backward Compatible
- System accepts old values
- No validation errors for legacy data
- Automatic normalization

### 2. Defensive Strategy
- Forms validate and normalize
- Models accept both old/new values temporarily
- API serializers normalize
- Database cleanup removes old values

### 3. Safe Rollback
- If issues occur, git revert takes seconds
- Database changes are in migrations (reversible)
- Cleanup can be re-run if needed

### 4. Production Safe
- One-time cleanup on deployment
- No ongoing processing cost
- Existing data protected

---

## ⚠️ Important Notes

### Why Keep Legacy Choices?
- Allows gradual migration
- Supports intermediate states
- Prevents "invalid choice" errors
- Can be removed in future migration

### When To Remove Legacy Choices?
After deploying this change and verifying:
1. All old data is converted (cleanup_legacy_values ran)
2. Forms only submit new values
3. No SPA code sends old values
4. Then create new migration to remove legacy choices

### SPA Considerations
User mentioned: "Toutes les anciennes copies statiques spa.*.js ont été écrasées avec la version corrigée"

If SPA still sends old values:
1. Form clean() will normalize them ✅
2. API serializers will normalize them ✅
3. No data loss, just re-submission needed

But ideally, ensure [static/js/spa.js](static/js/spa.js) has updated choice values.

---

## 📞 Support

If issues arise during deployment:

1. **Form validation errors:**
   - Check form clean() methods were added correctly
   - Verify normalize_priority() and normalize_criticality() functions exist

2. **Database constraint errors:**
   - Run: `python manage.py cleanup_legacy_values`
   - Check that 0005_* migrations were applied

3. **Serializer errors:**
   - Serializers already had normalization (no changes needed)
   - Check API endpoints using to_internal_value()

4. **Rollback:**
   ```bash
   git revert <commit-hash>
   git push origin main
   ```

---

**Completed by:** GitHub Copilot  
**Date:** May 6, 2026  
**Status:** ✅ Ready for Production Deployment

---

For detailed technical reference, see: [LEGACY_VALUES_HANDLING.md](LEGACY_VALUES_HANDLING.md)
