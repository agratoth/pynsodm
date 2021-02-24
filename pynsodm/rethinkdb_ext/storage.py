import os

from rethinkdb import RethinkDB

from pynsodm.rethinkdb_ext import BaseModel


class Storage:
    def __init__(self, **kwargs):
        self._driver = RethinkDB()
        self._connection = kwargs.get('connection', None)

        self._host = kwargs.get(
            'host', os.environ.get('RETHINKDB_HOST', 'localhost'))
        self._port = int(kwargs.get(
            'port', os.environ.get('RETHINKDB_PORT', '28015')))
        self._user = kwargs.get(
            'user', os.environ.get('RETHINKDB_USER', 'admin'))
        self._password = kwargs.get(
            'password', os.environ.get('RETHINKDB_PASSWORD', ''))
        self._db = kwargs.get(
            'db', os.environ.get('RETHINKDB_DATABASE', 'test'))

        _models = kwargs.get('models', os.environ.get('RETHINKDB_MODELS', ''))
        self._models = [m for m in _models.split(',') if len(m) > 0]

    def _init_db(self):
        if not self._connection:
            self._connection = self._driver.connect(
                host=self._host,
                port=self._port,
                db=self._db,
                user=self._user,
                password=self._password)
        else:
            self._connection.reconnect()

        db_list = self._driver.db_list().run(self._connection)
        if self._db not in db_list:
            self._driver.db_create(self._db).run(self._connection)

    def _init_index(self, table_name, index):
        index_list = self._driver.table(table_name).index_list().run(
            self._connection)
        if index not in index_list:
            self._driver.table(table_name).index_create(index).run(
                self._connection)
        self._driver.table(table_name).index_wait(index).run(
            self._connection)

    def _init_table(self, table_name, indexes=[]):
        table_list = self._driver.table_list().run(self._connection)

        if table_name not in table_list:
            self._driver.table_create(table_name).run(self._connection)

        for index in indexes:
            self._init_index(table_name, index)

    def connect(self):
        self._init_db()

        subclasses = BaseModel.__subclasses__()

        for subclass in subclasses:
            if len(self._models) > 0 and \
                    subclass.get_model_name() not in self._models:
                continue

            table_name = subclass.get_table_name()

            self._init_table(table_name, subclass.get_index_fields())

            subclass.set_storage(self)
            for relation_field in subclass.get_relation_fields():
                relation_field_obj = getattr(subclass, relation_field)
                if relation_field_obj.backfield:
                    setattr(
                        relation_field_obj.relation_class,
                        relation_field_obj.backfield,
                        relation_field_obj.resolver(subclass))

    def reconnect(self):
        self._connection = None
        self.connect()

    def insert(self, data_obj):
        obj_data = data_obj.dictionary
        obj_data.pop('id')

        for rel_field in data_obj.get_relation_fields():
            rel_object = obj_data.get(rel_field)
            obj_data.pop(rel_field)
            obj_data[rel_field] = rel_object.id

        result = self._driver\
            .table(data_obj.get_table_name())\
            .insert(obj_data)\
            .run(self._connection)

        if 'generated_keys' in result and \
                len(result['generated_keys']) == 1:
            return result['generated_keys'][0]

    def update(self, data_obj):
        obj_data = data_obj.modified_dictionary
        obj_data.pop('id')

        for rel_field in data_obj.get_relation_fields():
            rel_object = obj_data.get(rel_field)
            obj_data.pop(rel_field)
            obj_data[rel_field] = rel_object.id

        self._driver\
            .table(data_obj.get_table_name())\
            .filter({'id': data_obj.id})\
            .update(obj_data)\
            .run(self._connection)

    def get(self, table_name, obj_id):
        return self._driver.table(table_name).get(obj_id).run(self._connection)

    def find(self, table_name, fil):
        return self._driver.table(table_name).filter(fil).run(self._connection)

    def delete(self, table_name, fil):
        result = self._driver\
            .table(table_name)\
            .filter(fil)\
            .delete()\
            .run(self._connection)
        if 'deleted' in result and result['deleted'] > 0:
            return True
        return False
