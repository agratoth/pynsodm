PyNSODM (Python NoSQL Object-Document Mapper)
=======

|PyPI| |Python| |Downloads|

.. |PyPI| image:: https://img.shields.io/pypi/v/pynsodm
    :target: https://pypi.org/project/pynsodm
    :alt: PyPI

.. |Python| image:: https://img.shields.io/pypi/pyversions/pynsodm
    :target: https://pypi.org/project/pynsodm
    :alt: PyPI - Python Version

.. |Downloads| image:: https://img.shields.io/pypi/dm/pynsodm
    :target: https://pypi.org/project/pynsodm
    :alt: PyPI - Downloads

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