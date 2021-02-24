import pytest

from rethinkdb import r

from pytest_docker_tools import container, fetch

from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField, OTORelation, OTMRelation
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

def test_one_to_many_relation(mock_server):
  class Person(BaseModel):
    table_name = 'persons'

    first_name = StringField()
    last_name = StringField()

  class Bike(BaseModel):
    table_name = 'bikes'

    model = StringField()
    owner = OTMRelation(Person, backfield='bikes')

  storage.reconnect()

  person1 = Person(first_name='John', last_name='Doe')
  person1.save()

  person2 = Person(first_name='Jane', last_name='Doe')
  person2.save()

  bike1 = Bike(model='Altair MTB HT 26 1.0', owner=person1)
  bike1.save()

  bike2 = Bike(model='Bicystar Explorer 26"', owner=person1)
  bike2.save()

  bike3 = Bike(model='Horn Forest FHD 7.1 27.5', owner=person2)
  bike3.save()

  get_person1 = Person.get(person1.id)
  get_person2 = Person.get(person2.id)

  assert len(get_person1.bikes) == 2 and len(get_person2.bikes) == 1

def test_one_to_many_relation_id_checking(mock_server):
  class Person(BaseModel):
    table_name = 'persons'

    first_name = StringField()
    last_name = StringField()

  class Bike(BaseModel):
    table_name = 'bikes'

    model = StringField()
    owner = OTMRelation(Person, backfield='bikes')

  storage.reconnect()

  person1 = Person(first_name='John', last_name='Doe')
  person1.save()

  person2 = Person(first_name='Jane', last_name='Doe')
  person2.save()

  bike1 = Bike(model='Altair MTB HT 26 1.0', owner=person1)
  bike1.save()

  bike2 = Bike(model='Bicystar Explorer 26"', owner=person1)
  bike2.save()

  bike3 = Bike(model='Horn Forest FHD 7.1 27.5', owner=person2)
  bike3.save()

  bike_ids = []
  bike_ids.append(bike1.id)
  bike_ids.append(bike2.id)

  get_person1 = Person.get(person1.id)

  assert sorted(bike_ids) == sorted([b.id for b in get_person1.bikes])

def test_complex_relations(mock_server):
  class IDCard(BaseModel):
    table_name = 'idcards'

    number = StringField()

  class Person(BaseModel):
    table_name = 'persons'

    first_name = StringField()
    last_name = StringField()
    idcard = OTORelation(IDCard, backfield='person')

  class Bike(BaseModel):
    table_name = 'bikes'

    model = StringField()
    number = StringField()
    owner = OTMRelation(Person, backfield='bikes')

  storage.reconnect()

  idcard1 = IDCard(number='test123')
  idcard1.save()

  idcard2 = IDCard(number='test456')
  idcard2.save()

  person1 = Person(first_name='John', last_name='Doe', idcard=idcard1)
  person1.save()

  person2 = Person(first_name='Jane', last_name='Doe', idcard=idcard2)
  person2.save()

  bike1 = Bike(model='Altair MTB HT 26 1.0', number='bike123', owner=person1)
  bike1.save()

  bike2 = Bike(model='Bicystar Explorer 26"', number='bike456', owner=person1)
  bike2.save()

  bike3 = Bike(model='Horn Forest FHD 7.1 27.5', number='bike789', owner=person2)
  bike3.save()

  finded_bike1 = Bike.find(number='bike123')[0]
  finded_bike2 = Bike.find(number='bike789')[0]

  assert finded_bike1.owner.idcard.number == 'test123' and finded_bike2.owner.idcard.number == 'test456'

def test_delete_object(mock_server):
  class Test123(BaseModel):
    pass

  storage.reconnect()

  test = Test123()
  test.save()

  Test123.delete(id=test.id)

  with pytest.raises(NonexistentIDException):
    Test123.get(test.id)