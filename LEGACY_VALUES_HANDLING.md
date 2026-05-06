# NORMALIZATION & LEGACY VALUE HANDLING - COMPLETION SUMMARY

Date: May 6, 2026  
Status: ✅ COMPLETE

## Overview

All form classes and API endpoints have been updated to safely handle legacy choice values. The system now implements a three-layer defense strategy:

1. **Form Layer** - Clean methods normalize input values
2. **Model Layer** - Choice fields accept both legacy and new values  
3. **API Layer** - Serializers normalize values before validation
4. **Database Cleanup** - Management command converts existing legacy data

---

## Changes Made

### 1. Form-Level Normalization (maintenance/forms.py)

**Utility Functions (Lines 8-32):**
- `LEGACY_PRIORITY_MAP`: Maps old priority values to new ones
  - "Urgente" → "Très urgent"
  - "Normale" → "Normal"
  - "Faible" → "Normal"
  - "Pas urgente" → "Normal"
- `LEGACY_CRITICALITY_MAP`: Maps old criticality values
  - "Haute" → "Élevée"
- `normalize_priority()`: Safely converts priority values
- `normalize_criticality()`: Safely converts criticality values

**Updated Form Classes (4 total):**

1. **IncidentForm** (Lines 33-68)
   - Added `clean()` method
   - Normalizes both priority and criticality
   - Prevents validation errors from legacy values

2. **IncidentOperatorForm** (Lines 70-102)
   - Added `clean()` method  
   - Normalizes priority and criticality
   - Used by operators creating incidents

3. **InterventionForm** (Lines 112-152)
   - Enhanced `clean()` method
   - Normalizes priority values
   - Validates equipment-incident relationship

4. **TechnicianInterventionForm** (Lines 154-176)
   - Standard form for technician updates
   - No priority normalization needed (status/report fields only)

### 2. Model-Level Choice Acceptance

**New Migration: maintenance/migrations/0005_accept_legacy_values.py**
- Incident.priority: Added legacy choices to field definition
- Incident.criticality: Added legacy choices to field definition
- Intervention.priority: Added legacy choices to field definition
- Allows database validation to pass for old values

**New Migration: equipment/migrations/0005_accept_legacy_criticality.py**
- Equipement.criticality: Added legacy "Haute" choice
- Ensures backward compatibility at database level

### 3. API-Level Normalization

**maintenance/serializers.py (Already Updated):**
- `normalize_legacy_choice_values()` function already present
- Both IncidentSerializer and InterventionSerializer use `to_internal_value()` override
- Automatically normalizes legacy values from JSON API requests

### 4. Database Cleanup Command

**New Command: maintenance/management/commands/cleanup_legacy_values.py**

Features:
- Finds all existing legacy values in database
- Converts them to new values in one operation
- Works on all affected models:
  - Incident (priority, criticality)
  - Intervention (priority)
  - Equipement (criticality)
- Provides progress feedback with colorized output

Usage:
```bash
python manage.py cleanup_legacy_values
```

### 5. Build Process Integration

**Updated: build.sh**

New line added:
```bash
python manage.py cleanup_legacy_values
```

Execution order:
1. Migrate (applies new 0005_* migrations)
2. create_superuser
3. **cleanup_legacy_values** ← NEW
4. create_demo_accounts
5. seed_demo_data

This ensures any old data in the database is converted to new values immediately after migration.

---

## Data Flow - Example Scenario

### User submits form with legacy value "Urgente"

```
1. HTML Form Submission
   └─> POST priority="Urgente"

2. Django Form Processing
   └─> IncidentForm.clean() catches value
   └─> normalize_priority("Urgente") returns "Très urgent"
   └─> cleaned_data["priority"] = "Très urgent"

3. Model Validation
   └─> Incident.priority.choices includes "Urgente" (as backup)
   └─> But value is already normalized to "Très urgent"

4. Database Save
   └─> INSERT/UPDATE with "Très urgent"
   └─> No constraint violations
```

### User's API client sends legacy JSON value

```
1. JSON API Request
   └─> POST {"priority": "Urgente", ...}

2. Serializer Processing
   └─> to_internal_value() calls normalize_legacy_choice_values()
   └─> Converts {"priority": "Très urgent", ...}

3. Validation
   └─> validate_priority() receives normalized value
   └─> No validation errors

4. Model Save
   └─> Instance saved with "Très urgent"
```

---

## Verification Steps

### Local Testing

```bash
# 1. Apply migrations
python manage.py migrate

# 2. Clean up any old test data
python manage.py cleanup_legacy_values

# 3. Test form with legacy value
python manage.py shell
>>> from maintenance.forms import IncidentForm
>>> from maintenance.models import Incident
>>> form_data = {"priority": "Urgente", "criticality": "Haute", ...}
>>> form = IncidentForm(data=form_data)
>>> form.is_valid()  # Should be True
True
>>> # Check cleaned values
>>> form.cleaned_data["priority"]
'Très urgent'

# 4. Test API with legacy value
# Using test client or curl:
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Content-Type: application/json" \
  -d '{"priority": "Urgente", ...}'
# Should succeed and store "Très urgent"
```

### Production Testing (After Deployment)

1. Monitor Render deployment logs for:
   - No migration errors
   - cleanup_legacy_values completes successfully
   - All demo accounts created

2. Manual test:
   - Login with demo account
   - Create new incident via form with old priority value
   - Verify database stores new value

3. Check existing data:
   ```bash
   # SSH into production container
   # Or use Django shell on Render
   >>> Incident.objects.values('priority').distinct()
   # Should show only: Très urgent, Urgent, Normal (no old values)
   ```

---

## Files Modified

| File | Changes | Impact |
|------|---------|--------|
| maintenance/forms.py | Added normalization functions + clean() to 3 forms | Forms now accept legacy values safely |
| maintenance/migrations/0005_accept_legacy_values.py | NEW: Added legacy choices to fields | Database accepts legacy input |
| equipment/migrations/0005_accept_legacy_criticality.py | NEW: Added legacy choices to Equipement | Database accepts legacy input |
| maintenance/management/commands/cleanup_legacy_values.py | NEW: Cleanup command | Converts all existing legacy data |
| maintenance/serializers.py | Already had normalize_legacy_choice_values() | API endpoints safe (no change needed) |
| build.sh | Added cleanup_legacy_values execution | Production auto-cleanup after migration |

---

## Rollback Plan (If Issues Arise)

If legacy value handling causes unexpected behavior:

1. **Revert to Previous State:**
   ```bash
   git revert <commit_hash>  # Revert this commit
   git push origin main
   # Render auto-redeploys
   ```

2. **Manual Database Fix (if needed):**
   ```bash
   # Connect to production database
   UPDATE maintenance_incident SET priority = 'Très urgent' 
   WHERE priority = 'Urgente';
   ```

3. **Remove Legacy Choices (if needed):**
   - Create migration to remove legacy choices from field definitions
   - Run cleanup_legacy_values first to ensure no legacy values exist
   - Then run new migration

---

## Next Steps

1. **Commit and Deploy:**
   ```bash
   git add .
   git commit -m "Complete form normalization & legacy value handling

   - Add clean() methods to all incident/intervention forms
   - Implement database-level acceptance of legacy choices
   - Add cleanup_legacy_values management command
   - Integrate cleanup into build process
   - API serializers already had normalization
   
   Fixes: Users can submit forms with old values; system normalizes them safely"
   
   git push origin main
   ```

2. **Monitor Render Deployment:**
   - Check deployment logs in Render dashboard
   - Verify build.sh executes without errors
   - Confirm "cleanup_legacy_values" message appears

3. **Post-Deployment Verification:**
   - Test login with demo accounts
   - Create new incident/intervention via form
   - Verify values saved correctly in database
   - Check SPA if it has hardcoded choice values

4. **Final Cleanup (if time permits):**
   - Remove legacy choice options from field definitions (in future migration)
   - This step is optional since current approach is backward-compatible

---

## Technical Notes

**Why Three-Layer Defense?**
- **Form Layer:** Catches user input early, prevents bad data from reaching model
- **Model Layer:** Backup validation in case API bypasses forms
- **API Layer:** Ensures direct JSON requests are normalized
- **Database:** Accepts legacy values temporarily during migration period

**Why Keep Legacy Choices in Model?**
- Allows existing data to remain valid
- Supports gradual migration strategy
- Prevents "value not valid choice" errors
- Can be removed in future migration after cleanup period

**Performance Impact:**
- Minimal - normalization is simple dict lookup
- Cleanup command runs once during deployment
- No ongoing performance cost

---

## Deployment Checklist

- [ ] All migrations created (0005_* files)
- [ ] Forms have clean() methods with normalization
- [ ] build.sh updated with cleanup command
- [ ] Git commit created with descriptive message
- [ ] Pushed to main branch
- [ ] Render deployment successful
- [ ] Demo accounts login working
- [ ] Form submission saves normalized values
- [ ] Database verified for old values (none should remain)

---

Generated: 2026-05-06  
Status: Ready for Deployment ✅
