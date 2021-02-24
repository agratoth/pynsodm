PyNSODM (Python NoSQL Object-Document Mapper)
=======

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/pypi/v/pynsodm)](https://pypi.org/project/pynsodm)
[![Python](https://img.shields.io/pypi/pyversions/pynsodm)](https://pypi.org/project/pynsodm)
[![Coverage Status](https://coveralls.io/repos/github/agratoth/pynsodm/badge.svg?branch=master)](https://coveralls.io/github/agratoth/pynsodm?branch=master)

Simple and powerful ODM for various NoSQL databases (RethinkDB, soon - Clickhouse, Redis, MongoDB, InfluxDB, etc.)

## Basic use

```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField

class User(BaseModel):
    table_name = 'users'

    username = StringField()

storage = Storage(db='test_db')
storage.connect()

user = User(username='test_user')
user.save()

print(user.dictionary)

# {'created': datetime.datetime(2021, 2, 24, 5, 53, 29, 411519, tzinfo=<UTC>), 'id': 'fb95ba98-a663-4f0f-b709-2e1d2eb849bd', 'updated': datetime.datetime(2021, 2, 24, 5, 53, 29, 411530, tzinfo=<UTC>), 'username': 'test_user'}
```

## Installation

```
pip install pynsodm
```

## Examples
### Simple object
```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField

class User(BaseModel):
    table_name = 'users'

    username = StringField()

storage = Storage(db='test_db')
storage.connect()

user = User(username='test_user')
user.save()

print(user.dictionary)

# {'created': datetime.datetime(2021, 2, 24, 5, 53, 29, 411519, tzinfo=<UTC>), 'id': 'fb95ba98-a663-4f0f-b709-2e1d2eb849bd', 'updated': datetime.datetime(2021, 2, 24, 5, 53, 29, 411530, tzinfo=<UTC>), 'username': 'test_user'}
```

### Field with validation
```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField
from pynsodm.valids import valid_email
from pynsodm.exceptions import ValidateException

class User(BaseModel):
    table_name = 'users'

    username = StringField()
    email = StringField(valid=valid_email)

storage = Storage(db='test_db')
storage.connect()

try:
  user = User(username='test_user', email='test')
  user.save()
  print('success')
except ValidateException as ex:
  print(str(ex))

# Invalid value

try:
  user = User(username='test_user', email='test@test.loc')
  user.save()
  print('success')
except ValidateException as ex:
  print(str(ex))

# success

print(user.dictionary)

# {'created': datetime.datetime(2021, 2, 24, 7, 8, 11, 262538, tzinfo=<UTC>), 'email': 'test@test.loc', 'id': '8e8fc3d4-6ea3-4219-bbe6-16529fa35a47', 'updated': datetime.datetime(2021, 2, 24, 7, 8, 11, 262550, tzinfo=<UTC>), 'username': 'test_user'}
```

### Delete object
```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.exceptions import NonexistentIDException


class Test123(BaseModel):
  pass

storage = Storage(db='test_db')
storage.connect()

test = Test123()
test.save()

try:
  get_test = Test123.get(test.id)
  print('success')
except NonexistentIDException as ex:
  print(str(ex))

# success

print(Test123.delete(id=test.id))
# True

try:
  get_test = Test123.get(test.id)
  print('success')
except NonexistentIDException as ex:
  print(str(ex))

# ID is not exist
```

## Advanced Examples. Relations
### One-to-One Relation
```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField, OTORelation


class IDCard(BaseModel):
  table_name = 'idcards'

  number = StringField()

class Person(BaseModel):
  table_name = 'persons'

  first_name = StringField()
  last_name = StringField()

  idcard = OTORelation(IDCard, backfield='person')

storage = Storage(db='test_db')
storage.connect()

idcard = IDCard(number='test123')
idcard.save()

person = Person(first_name='John', last_name='Doe', idcard=idcard)
person.save()

get_person = Person.get(person.id)
print(get_person.idcard.number)
# test123

get_idcard = IDCard.get(idcard.id)
print(get_idcard.person.first_name, get_idcard.person.last_name)
# John Doe
```

### One-to-Many Relation
```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField, OTMRelation

class Person(BaseModel):
  table_name = 'persons'

  first_name = StringField()
  last_name = StringField()

class Bike(BaseModel):
  table_name = 'bikes'

  model = StringField()
  owner = OTMRelation(Person, backfield='bikes')

storage = Storage(db='test_db')
storage.connect()

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

for bike in get_person1.bikes:
  print(bike.model)

# Bicystar Explorer 26"
# Altair MTB HT 26 1.0
```

### Several different relationships
```python
from pynsodm.rethinkdb_ext import Storage, BaseModel
from pynsodm.fields import StringField, OTORelation, OTMRelation


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

storage = Storage(db='test_db')
storage.connect()

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

print(finded_bike1.owner.idcard.number)
# test123

print(finded_bike2.owner.idcard.number)
# test456
```