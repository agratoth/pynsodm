import pytest

from pynsodm.rethinkdb_ext import BaseModel
from pynsodm.fields import StringField
from pynsodm.exceptions import ListItemException, ValidateException
from pynsodm.valids import valid_email


def test_table_name():
    class Test123(BaseModel):
        pass

    assert Test123.get_table_name() == Test123.__name__.lower()


def test_custom_table_name():
    custom_name = 'tests'

    class Test123(BaseModel):
        table_name = custom_name

    assert Test123.get_table_name() == custom_name


def test_primary_index():
    class Test123(BaseModel):
        pass

    assert Test123.get_primary_index() == 'id'


def test_string_field_with_items():
    class Test123(BaseModel):
        field = StringField(items=['val0', 'val1'])

    test = Test123()

    try:
        test.field = 'val0'
        assert True
    except Exception:
        assert False


def test_string_field_with_items_invalid_data():
    class Test123(BaseModel):
        field = StringField(items=['val0', 'val1'])

    test = Test123()

    with pytest.raises(ListItemException):
        test.field = 'val2'


def test_fill_object_from_kwargs():
    class Test123(BaseModel):
        field = StringField()

    test = Test123(field='test123')

    assert test.field == 'test123'


def test_fill_object_from_dictionary():
    class Test123(BaseModel):
        field = StringField()

    test = Test123.from_dictionary({'field': 'test123'})

    assert test.field == 'test123'


def test_fill_object_from_dictionary_with_sensitive_data():
    class Test123(BaseModel):
        field = StringField()

    test = Test123.from_dictionary(
        {'id': 'e99bc346-8acd-47be-9ee4-ff1c98dd9eed', 'field': 'test123'})

    assert not test.id


def test_fill_object_from_dictionary_with_validators_invalid_data():
    class Test123(BaseModel):
        email = StringField(valid=valid_email)

    with pytest.raises(ValidateException):
        Test123.from_dictionary({'email': 'test123'})


def test_fill_object_from_dictionary_with_validators_valid_data():
    class Test123(BaseModel):
        email = StringField(valid=valid_email)

    try:
        Test123.from_dictionary({'email': 'test123@test.com'})
        assert True
    except Exception:
        assert False
