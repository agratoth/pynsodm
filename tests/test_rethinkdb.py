import pytest

from rethinkdb import r

from pytest_docker_tools import container, fetch

from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField
from pynsodm.exceptions import ListItemException


rethinkdb_image = fetch(repository='rethinkdb:2.4.1-buster-slim')

mock_server = container(
    image='{rethinkdb_image.id}',
    ports={
        '28015' : '35035/tcp',
    },
    command='rethinkdb --bind all --initial-password test123123',
)

test_db_name = 'test_db'
storage = Storage(port='35035', password='test123123', db=test_db_name)

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
  except:
    assert False

def test_string_field_with_items_invalid_data():
  class Test123(BaseModel):
    field = StringField(items=['val0', 'val1'])

  test = Test123()

  with pytest.raises(ListItemException):
    test.field = 'val2'

def test_init_db(mock_server):
  storage.reconnect()
  db_list = storage._driver.db_list().run(storage._connection)
  
  assert test_db_name in db_list

def test_init_table(mock_server):
  class User(BaseModel):
    table_name = 'users'

  storage.reconnect()
  table_list = storage._driver.db(test_db_name).table_list().run(storage._connection)

  assert User.table_name in table_list

def test_init_index(mock_server):
  class User(BaseModel):
    table_name = 'users'

    email = StringField(is_index=True)

  storage.reconnect()
  index_list = storage._driver.db(test_db_name).table(User.table_name).index_list().run(storage._connection)

  assert sorted(User.get_index_fields()) == sorted(index_list)