import pytest

from rethinkdb import r

from pytest_docker_tools import container, fetch

from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField, OTORelation, OTOResolver
from pynsodm.valids import valid_uuid
from pynsodm.exceptions import NonexistentIDException


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

def test_save_object(mock_server):
  class User(BaseModel):
    table_name = 'users'

    username = StringField()

  storage.reconnect()

  user = User(username='test')
  user.save()

  assert valid_uuid(user.id)

def test_get_object(mock_server):
  class User(BaseModel):
    table_name = 'users'

    username = StringField()

  storage.reconnect()

  user = User(username='test')
  user.save()

  get_user = User.get(user.id)

  assert user.id == get_user.id

def test_get_object_fake_id(mock_server):
  class User(BaseModel):
    table_name = 'users'

    username = StringField()

  storage.reconnect()

  with pytest.raises(NonexistentIDException):
    get_user = User.get('test123')

def test_find_objects_count(mock_server):
  class User(BaseModel):
    table_name = 'users'

    username = StringField()

  storage.reconnect()

  User(username='test1').save()
  User(username='test2').save()

  assert len(User.find()) == 2

def test_find_objects_with_filter(mock_server):
  class User(BaseModel):
    table_name = 'users'

    username = StringField()
    role = StringField()

  storage.reconnect()

  User(username='test1', role='role1').save()
  User(username='test2', role='role1').save()
  User(username='test3', role='role2').save()
  User(username='test4', role='role1').save()

  assert len(User.find(role='role1')) == 3

def test_find_objects_with_id_checking(mock_server):
  class User(BaseModel):
    table_name = 'users'

    username = StringField()
    role = StringField()

  storage.reconnect()

  data = [
    ('test1', 'role1'),
    ('test2', 'role1'),
    ('test3', 'role2'),
    ('test4', 'role1'),
  ]

  ids = []

  for elem in data:
    user = User(username=elem[0], role=elem[1])
    user.save()
    if elem[1] == 'role1':
      ids.append(user.id)

  finded_users = User.find(role='role1')
  finded_ids = [u.id for u in finded_users]
  
  assert sorted(ids) == sorted(finded_ids)

def test_one_to_one_relation(mock_server):
  class IDCard(BaseModel):
    table_name = 'idcards'

    number = StringField()

  class Person(BaseModel):
    table_name = 'persons'

    first_name = StringField()
    last_name = StringField()

    idcard = OTORelation(IDCard)

  storage.reconnect()

  idcard = IDCard(number='test123')
  idcard.save()

  person = Person(first_name='John', last_name='Doe', idcard=idcard)
  person.save()

  get_person = Person.get(person.id)

  assert get_person.idcard.number == 'test123'

def test_one_to_one_relation_backfield(mock_server):
  class IDCard(BaseModel):
    table_name = 'idcards'

    number = StringField()

  class Person(BaseModel):
    table_name = 'persons'

    first_name = StringField()
    last_name = StringField()

    idcard = OTORelation(IDCard, backfield='person')

  storage.reconnect()

  idcard = IDCard(number='test123')
  idcard.save()

  person = Person(first_name='John', last_name='Doe', idcard=idcard)
  person.save()

  get_idcard = IDCard.get(idcard.id)

  assert get_idcard.person.first_name == 'John'