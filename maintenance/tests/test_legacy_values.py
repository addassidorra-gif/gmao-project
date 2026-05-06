import unittest
from django.test import TestCase
from django.contrib.auth import get_user_model

from equipment.models import Equipement, EquipementCategory
from maintenance.forms import (
    IncidentForm, IncidentOperatorForm, InterventionForm,
    normalize_priority, normalize_criticality,
)
from maintenance.models import Incident, Intervention

User = get_user_model()


class LegacyValueNormalizationTest(TestCase):
    """Tests for legacy choice value normalization"""

    @classmethod
    def setUpTestData(cls):
        """Create test fixtures"""
        # Create test users
        cls.admin = User.objects.create_user(
            email='admin@test.com',
            password='test123',
            role=User.Role.ADMIN,
        )
        cls.tech = User.objects.create_user(
            email='tech@test.com',
            password='test123',
            role=User.Role.TECHNICIEN,
        )
        cls.operator = User.objects.create_user(
            email='operator@test.com',
            password='test123',
            role=User.Role.OPERATEUR,
        )

        # Create test equipment
        category = EquipementCategory.objects.create(
            name='Test Category',
            code='TEST_CAT',
        )
        cls.equipment = Equipement.objects.create(
            name='Test Equipment',
            code='EQ001',
            category=category,
            criticality=Equipement.Criticality.MOYENNE,
        )

    def test_normalize_priority_urgente(self):
        """Test legacy priority 'Urgente' normalizes to 'Très urgent'"""
        result = normalize_priority('Urgente')
        self.assertEqual(result, 'Très urgent')

    def test_normalize_priority_normale(self):
        """Test legacy priority 'Normale' normalizes to 'Normal'"""
        result = normalize_priority('Normale')
        self.assertEqual(result, 'Normal')

    def test_normalize_priority_faible(self):
        """Test legacy priority 'Faible' normalizes to 'Normal'"""
        result = normalize_priority('Faible')
        self.assertEqual(result, 'Normal')

    def test_normalize_priority_new_value(self):
        """Test that new priority values pass through unchanged"""
        result = normalize_priority('Très urgent')
        self.assertEqual(result, 'Très urgent')

    def test_normalize_priority_empty(self):
        """Test that empty/None values are handled safely"""
        self.assertIsNone(normalize_priority(None))
        self.assertEqual(normalize_priority(''), '')

    def test_normalize_criticality_haute(self):
        """Test legacy criticality 'Haute' normalizes to 'Élevée'"""
        result = normalize_criticality('Haute')
        self.assertEqual(result, 'Élevée')

    def test_normalize_criticality_new_value(self):
        """Test that new criticality values pass through unchanged"""
        result = normalize_criticality('Élevée')
        self.assertEqual(result, 'Élevée')

    def test_incident_form_normalizes_legacy_priority(self):
        """Test that IncidentForm.clean() normalizes legacy priority"""
        form_data = {
            'equipment': self.equipment.id,
            'technician': self.tech.id,
            'title': 'Test Incident',
            'description': 'Test Description',
            'priority': 'Urgente',  # Legacy value
            'criticality': 'Moyenne',
        }
        form = IncidentForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['priority'], 'Très urgent')

    def test_incident_form_normalizes_legacy_criticality(self):
        """Test that IncidentForm.clean() normalizes legacy criticality"""
        form_data = {
            'equipment': self.equipment.id,
            'technician': self.tech.id,
            'title': 'Test Incident',
            'description': 'Test Description',
            'priority': 'Normal',
            'criticality': 'Haute',  # Legacy value
        }
        form = IncidentForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['criticality'], 'Élevée')

    def test_incident_operator_form_normalizes_legacy_values(self):
        """Test that IncidentOperatorForm normalizes legacy values"""
        form_data = {
            'equipment': self.equipment.id,
            'technician': self.tech.id,
            'title': 'Test Incident',
            'description': 'Test Description',
            'priority': 'Urgente',  # Legacy value
            'criticality': 'Haute',  # Legacy value
        }
        form = IncidentOperatorForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        self.assertEqual(form.cleaned_data['priority'], 'Très urgent')
        self.assertEqual(form.cleaned_data['criticality'], 'Élevée')

    def test_form_with_all_legacy_priority_values(self):
        """Test that all legacy priority values normalize correctly"""
        legacy_values = {
            'Urgente': 'Très urgent',
            'Normale': 'Normal',
            'Faible': 'Normal',
            'Pas urgente': 'Normal',
        }

        for legacy, expected in legacy_values.items():
            form_data = {
                'equipment': self.equipment.id,
                'technician': self.tech.id,
                'title': 'Test Incident',
                'description': 'Test Description',
                'priority': legacy,
                'criticality': 'Moyenne',
            }
            form = IncidentForm(data=form_data)
            self.assertTrue(
                form.is_valid(),
                f"Form invalid for legacy priority '{legacy}': {form.errors}"
            )
            self.assertEqual(
                form.cleaned_data['priority'], expected,
                f"Priority '{legacy}' should normalize to '{expected}'"
            )

    def test_form_with_new_priority_values(self):
        """Test that new priority values are accepted as-is"""
        new_values = ['Très urgent', 'Urgent', 'Normal']

        for priority in new_values:
            form_data = {
                'equipment': self.equipment.id,
                'technician': self.tech.id,
                'title': 'Test Incident',
                'description': 'Test Description',
                'priority': priority,
                'criticality': 'Moyenne',
            }
            form = IncidentForm(data=form_data)
            self.assertTrue(
                form.is_valid(),
                f"Form should accept new priority value '{priority}': {form.errors}"
            )
            self.assertEqual(form.cleaned_data['priority'], priority)


if __name__ == '__main__':
    unittest.main()
