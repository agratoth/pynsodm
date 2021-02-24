PyNSODM (Python NoSQL Object-Document Mapper)
=======

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