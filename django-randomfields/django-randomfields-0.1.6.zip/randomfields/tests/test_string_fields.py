from django.apps import apps
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.forms.models import model_to_dict
from django.test import TestCase, SimpleTestCase
from django.utils.six import text_type
from randomfields.models.fields.integer import IntegerIdentifier
from randomfields.models.fields import RandomCharField, RandomTextField
from unittest import skipIf
from ..checks import DJANGO_VERSION_17
from . import mock
from .models import TestIdentifierData, TestIdentifierValue, TestPrimaryKey, TestUnique, TestMinLengthPossibilities, TestFixLengthPossibilities, TestNonUniqueIntegrityError, TestUniqueNotExistIntegrityError

class AppConfigTests(SimpleTestCase):
    def test_app_is_installed(self):
        self.assertTrue(apps.is_installed("randomfields"))

class SaveTests(TestCase):
    def _test_identifier_expected_values(self, model_class, attr):
        value_map = (
            (-2147483648, 2147483648),
            (0, 4294967296),
            (2147483647, 6442450943),
        )
        
        for db_value, display_value in value_map:
            self.assertFalse(model_class.objects.filter(**{attr: display_value}).exists())
            self.assertFalse(model_class.objects.filter(**{attr: db_value}).exists())
            
            obj1 = model_class(**{attr: display_value})
            obj1.save()
            
            self.assertTrue(model_class.objects.filter(**{attr: db_value}).exists())
            obj2 = model_class.objects.get(**{attr: db_value})
            
            obj1.full_clean()
            
            for obj in (obj1, obj2):
                value = getattr(obj, attr)
                self.assertTrue(isinstance(value, IntegerIdentifier), "Object attribute '%s' was not an instance of IntegerIdentifier.  It was type %r" % (attr, type(value)))
                self.assertEqual(value.display_value, display_value)
                self.assertEqual(value.db_value, db_value)
                
                key = 'id' if attr == "pk" else attr
                data = model_to_dict(obj)
                text = text_type(value)
                self.assertEqual(data.get(key, None), value, "Key '{}' did not match integer id '{}' in the following dict: {}".format(key, text, data))
    
    @skipIf(DJANGO_VERSION_17, "Not supported on Django 17")
    def test_identifier_expected_values_primary_key_by_fieldname(self):
        self._test_identifier_expected_values(TestIdentifierValue, "id")
    
    @skipIf(DJANGO_VERSION_17, "Not supported on Django 17")
    def test_identifier_expected_values_primary_key_by_pk(self):
        self._test_identifier_expected_values(TestIdentifierValue, "pk")
    
    @skipIf(DJANGO_VERSION_17, "Not supported on Django 17")
    def test_identifier_expected_values_data(self):
        self._test_identifier_expected_values(TestIdentifierData, "data")
    
    def test_identifier_pk_value_on_create(self):
        obj = TestIdentifierValue.objects.create()
        field = TestIdentifierValue._meta.get_field("id")
        expected_value = field.to_python(obj.id)
        expected_value = int(text_type(expected_value))
        value = int(text_type(obj.id))
        self.assertEqual(value, expected_value)
    
    def test_identifier_pk_type_on_create(self):
        obj = TestIdentifierValue.objects.create()
        self.assertIsInstance(obj.id, IntegerIdentifier)
        self.assertIsInstance(obj.pk, IntegerIdentifier)
            
    def test_auto_primary_key(self):
        obj = TestPrimaryKey()
        obj.save()
        all_pks = TestPrimaryKey.objects.all().values_list("pk", flat=True)
        self.assertIn(obj.pk, all_pks)
    
    def test_specified_primary_key(self):
        pk = "test"
        obj = TestPrimaryKey(pk=pk)
        obj.save()
        all_pks = TestPrimaryKey.objects.all().values_list("pk", flat=True)
        self.assertIn(pk, all_pks)
        
        with self.assertRaises(IntegrityError):
            TestPrimaryKey.objects.create(pk=pk)
    
    def test_collision_not_corrected_when_set_manually(self):
        obj1 = TestUnique()
        obj1.save()
        obj2 = TestUnique(unique_field=obj1.unique_field)
        with self.assertRaises(IntegrityError):
            obj2.save()

    def test_collision_correction(self):
        obj1 = TestUnique()
        obj1.save()
        obj2 = TestUnique(unique_field=obj1.unique_field)
        
        # begin hack
        # imitate accidental collision.  under normal circumstances,
        # available_values will only be persisted on a model instance
        # during Field.pre_save() or the monkeypatched instance.save().
        # it should never be set manually because it is used to detect
        # if collision correction should occur
        field = obj2._meta.get_field("unique_field")
        field.persist_available_values(obj2, set())
        # endhack
        
        obj2.save()
        
        all_values = TestUnique.objects.all().values_list("unique_field", flat=True)
        self.assertIn(obj1.unique_field, all_values)
        self.assertIn(obj2.unique_field, all_values)
        self.assertNotEqual(obj1.pk, obj2.pk)
    
    def test_atomic_collision_correction(self):
        with transaction.atomic():
            self.test_collision_correction()
    
    def test_available_values_persist_and_removed(self):
        obj1 = TestUnique()
        field1 = obj1._meta.get_field("unique_field")
        self.assertFalse(hasattr(obj1, field1.available_values_attname))
        
        val1 = field1.pre_save(obj1, True)
        self.assertTrue(val1)
        self.assertTrue(hasattr(obj1, field1.available_values_attname))
        
        obj1.save()
        self.assertEqual(val1, obj1.unique_field)
        self.assertFalse(hasattr(obj1, field1.available_values_attname))
    
    def test_available_values_not_persisted(self):
        obj1 = TestUnique(unique_field="foo")
        field1 = obj1._meta.get_field("unique_field")
        self.assertFalse(hasattr(obj1, field1.available_values_attname))
        
        val1 = field1.pre_save(obj1, True)
        self.assertEqual(val1, "foo")
        self.assertFalse(hasattr(obj1, field1.available_values_attname))
        
        obj1.save()
        self.assertEqual(val1, obj1.unique_field)
        self.assertFalse(hasattr(obj1, field1.available_values_attname))
    
    @mock.patch('randomfields.models.fields.RandomFieldMixin.logger')
    def test_warn_at_percent(self, mocked_logger):
        obj1 = TestMinLengthPossibilities()
        self.assertEqual(obj1._meta.get_field("data").valid_chars, "ab")
        self.assertEqual(obj1._meta.get_field("data").max_length, 2)
        self.assertEqual(obj1._meta.get_field("data").min_length, 1)
        self.assertEqual(6, obj1._meta.get_field("data").possibilities)
        self.assertEqual(0, TestMinLengthPossibilities.objects.count())
        
        warn_at = 0.55
        
        for i in (1, 2, 3, 4, 5, 6, 7):
            obj = TestMinLengthPossibilities()
            obj._meta.get_field("data").warn_at_percent = warn_at
            if i == 7:
                with self.assertRaises(IntegrityError):
                    obj.save()
            else:
                obj.save()
                if i < 5:
                    self.assertFalse(mocked_logger.warning.called)
                else:
                    count = i - 4# 4==1, 5==2, 6==3
                    self.assertEqual(count, mocked_logger.warning.call_count)
    
    def test_min_length_possibilities(self):
        # ensure possibilities are calculated properly for min_length
        obj1 = TestMinLengthPossibilities()
        self.assertEqual(obj1._meta.get_field("data").valid_chars, "ab")
        self.assertEqual(obj1._meta.get_field("data").max_length, 2)
        self.assertEqual(obj1._meta.get_field("data").min_length, 1)
        """
            possibilities:
                a
                aa
                ab
                ba
                bb
                b
        """
        self.assertEqual(6, obj1._meta.get_field("data").possibilities)
        
        # ensure all possibilities are saved
        while TestMinLengthPossibilities.objects.count() < 6:
            TestMinLengthPossibilities().save()
        
        all_values = TestMinLengthPossibilities.objects.all().values_list("data", flat=True)
        self.assertIn('a', all_values)
        self.assertIn('aa', all_values)
        self.assertIn('ab', all_values)
        self.assertIn('ba', all_values)
        self.assertIn('bb', all_values)
        self.assertIn('b', all_values)
        
        # ensure an integrity error is thrown on subsequent saves
        self.assertRaises(IntegrityError, TestMinLengthPossibilities().save)
    
    def test_fix_length_possibilities(self):
        obj1 = TestFixLengthPossibilities()
        self.assertEqual(obj1._meta.get_field("data").valid_chars, "ab")
        self.assertEqual(obj1._meta.get_field("data").max_length, 2)
        self.assertIs(obj1._meta.get_field("data").min_length, 2)
        """
            possibilities:
                aa
                ab
                ba
                bb
        """
        self.assertEqual(4, obj1._meta.get_field("data").possibilities)
        
        # ensure all possibilities are saved
        while TestFixLengthPossibilities.objects.count() < 4:
            TestFixLengthPossibilities().save()
        
        all_values = TestFixLengthPossibilities.objects.all().values_list("data", flat=True)
        self.assertNotIn('a', all_values)
        self.assertIn('aa', all_values)
        self.assertIn('ab', all_values)
        self.assertIn('ba', all_values)
        self.assertIn('bb', all_values)
        self.assertNotIn('b', all_values)
        
        # ensure an integrity error is thrown on subsequent saves
        self.assertRaises(IntegrityError, TestFixLengthPossibilities().save)
    
    def test_non_unique_survives_integrity_error(self):
        obj1 = TestNonUniqueIntegrityError()
        obj1.unique_int_field = 1
        obj1.save()
        
        obj2 = TestNonUniqueIntegrityError()
        obj2.unique_int_field = obj1.unique_int_field
        field2 = obj2._meta.get_field("non_unique_field")
        val2 = field2.pre_save(obj2, True)
        
        with self.assertRaises(IntegrityError):
            obj2.save()
        
        self.assertEqual(obj2.non_unique_field, val2)
        
        obj2.unique_int_field += 1
        obj2.save()
        self.assertEqual(obj2.non_unique_field, val2)
    
    def test_unique_not_exist_survives_integrity_error(self):
        obj1 = TestUniqueNotExistIntegrityError()
        obj1.unique_int_field = 1
        obj1.unique_rand_field = "foo"
        obj1.save()
        
        obj2 = TestUniqueNotExistIntegrityError()
        obj2.unique_int_field = obj1.unique_int_field
        field2 = obj2._meta.get_field("unique_rand_field")
        val2 = field2.pre_save(obj2, True)
        
        with self.assertRaises(IntegrityError):
            obj2.save()
        
        self.assertEqual(obj2.unique_rand_field, val2)
        
        obj2.unique_int_field += 1
        obj2.save()
        self.assertEqual(obj2.unique_rand_field, val2)
    
    def test_string_length_validation(self):
        for field_cls in (RandomCharField, RandomTextField):
            field = field_cls(min_length=10, max_length=10)
            form_field = field.formfield()
            
            valid_value = field.random()
            long_value = valid_value + text_type("a")
            short_value = valid_value[1:]
            
            #
            # form field validation
            #
            with self.assertRaises(ValidationError):
                form_field.clean(long_value)
            with self.assertRaises(ValidationError):
                form_field.clean(short_value)
            
            # no exceptions
            form_field.clean(valid_value)
            
            #
            # model field validation
            #
            with self.assertRaises(ValidationError):
                field.run_validators(long_value)
            
            # no exceptions -- validated in form layer so db values
            # do not become invalid as requirements shift
            field.run_validators(valid_value)
            field.run_validators(short_value)
    
    def _test_string_field_kwargs(self, exeception_class, kwargs):
        for field_cls in (RandomCharField, RandomTextField):
            with self.assertRaises(exeception_class):
                field_cls(**kwargs)
    
    def test_string_field_kwargs_max_length(self):
        self._test_string_field_kwargs(TypeError, {})
        self._test_string_field_kwargs(TypeError, {"max_length": None})
        self._test_string_field_kwargs(ValueError, {"max_length": "foo"})
        self._test_string_field_kwargs(ValueError, {"max_length": 0})
    
    def test_string_field_kwargs_min_length(self):
        self._test_string_field_kwargs(TypeError, {"max_length": 50, "min_length": None})
        self._test_string_field_kwargs(ValueError, {"max_length": 50, "min_length": "foo"})
        self._test_string_field_kwargs(ValueError, {"max_length": 50, "min_length": -1})
    
    def test_string_field_kwargs_min_max_length(self):
        self._test_string_field_kwargs(ValueError, {"max_length": 50, "min_length": 51})
    
    def test_string_field_kwargs_valid_chars(self):
        self._test_string_field_kwargs(TypeError, {"max_length": 50, "valid_chars": 1})
    
    def _test_string_field_formfield_validation(self, model_field_cls, kwargs, value):
        field = model_field_cls(**kwargs)
        field.formfield().clean(value)
    
    def _test_string_field_validation(self, field_cls, kwargs, value):
        field = field_cls(**kwargs)
        field.run_validators(value)
            
    def test_string_field_valid_chars_validation(self):
        for field_cls in (RandomCharField, RandomTextField):
            kwargs = {"max_length": 3, "valid_chars": "b"}
            
            # no exception
            self._test_string_field_formfield_validation(field_cls, kwargs, "bbb")
            
            with self.assertRaises(ValidationError):
                self._test_string_field_formfield_validation(field_cls, kwargs, "abb")
            with self.assertRaises(ValidationError):
                self._test_string_field_formfield_validation(field_cls, kwargs, "bab")
            with self.assertRaises(ValidationError):
                self._test_string_field_formfield_validation(field_cls, kwargs, "bba")
            
            # no exception unicode
            pi = b'\u03c0'.decode("unicode-escape")
            pi_value = text_type("bb%s") % pi
            self.assertEqual(len(pi_value), 3)
            self._test_string_field_formfield_validation(field_cls, {"max_length": 3, "valid_chars": pi_value}, "bbb")
            
            with self.assertRaises(ValidationError):
                self._test_string_field_formfield_validation(field_cls, kwargs, pi_value)
            
            # model field should not raise exception so that valid chars
            # can change without invalidating the database value
            self._test_string_field_validation(field_cls, kwargs, "bba")
            self._test_string_field_validation(field_cls, kwargs, pi_value)