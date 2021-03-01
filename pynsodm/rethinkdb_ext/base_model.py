import copy

from pynsodm.fields import IDField, DatetimeField
from pynsodm.exceptions import NonexistentIDException


class BaseModel:
    table_name: str = None
    storage = None

    id = IDField()
    created = DatetimeField(is_index=True, is_sensitive=True)
    updated = DatetimeField(is_index=True, is_sensitive=True)

    def __init__(self, **kwargs):
        self._exist_object = False
        self.fields = {}

        for field_name, field_value in self.get_fields_values().items():
            self.fields[field_name] = copy.deepcopy(field_value)

        for resolver_name in self.get_resolver_fields():
            resolver_value = getattr(self.__class__, resolver_name)
            self.fields[resolver_name] = copy.deepcopy(resolver_value)

        for field_name, field_value in kwargs.items():
            if field_name in dir(self):
                setattr(self, field_name, field_value)

    @classmethod
    def from_dictionary(cls, data, sensitive_fields=False):
        obj = cls()
        obj._exist_object = True

        fields_list = cls.get_fields() \
            if sensitive_fields \
            else cls.get_unsensitive_fields()

        for field_name, field_value in data.items():
            if field_name in fields_list:
                setattr(obj, field_name, field_value)

        return obj

    @classmethod
    def get_table_name(cls):
        if cls.table_name:
            return cls.table_name
        return cls.__name__.lower()

    @classmethod
    def get_model_name(cls):
        return cls.__name__

    @classmethod
    def get_fields_values(cls):
        fields = dir(cls)
        result = {}

        for field in fields:
            field_value = getattr(cls, field)

            if 'is_field' in dir(field_value):
                if field_value.is_field:
                    result[field] = field_value
        return result

    @classmethod
    def get_fields(cls):
        return list(cls.get_fields_values().keys())

    @classmethod
    def get_index_fields(cls):
        return [
            k for k, v
            in cls.get_fields_values().items()
            if v.is_index and not v.is_primary]

    @classmethod
    def get_unsensitive_fields(cls):
        return [
            k for k, v
            in cls.get_fields_values().items()
            if not v.is_sensitive]

    @classmethod
    def get_relation_fields(cls):
        return [k for k, v in cls.get_fields_values().items() if v.is_relation]

    @classmethod
    def get_resolver_fields(cls):
        fields = dir(cls)
        result = []

        for field in fields:
            field_value = getattr(cls, field)

            if 'is_resolver' in dir(field_value):
                if field_value.is_resolver:
                    result.append(field)
        return result

    @classmethod
    def get_modified_fields(cls):
        return [k for k, v in cls.get_fields_values().items() if v.is_modified]

    @classmethod
    def get_primary_index(cls):
        primary_indexes = [
            k for k, v
            in cls.get_fields_values().items()
            if v.is_primary]
        if len(primary_indexes) > 0:
            return primary_indexes[0]
        return None

    @classmethod
    def set_storage(cls, value):
        cls.storage = value

    @classmethod
    def get(cls, id):
        data = cls.storage.get(cls.get_table_name(), id)
        if not data:
            raise NonexistentIDException()

        get_obj = cls.from_dictionary(data, sensitive_fields=True)

        for resolver_field in cls.get_resolver_fields():
            resolver_field_obj = getattr(cls, resolver_field)

            parent_class = resolver_field_obj.relation_class
            parent_class_table = parent_class.get_table_name()
            parent_relation_fields = parent_class.get_relation_fields()
            for parent_relation_field in parent_relation_fields:
                parent_relation_field_obj = getattr(
                    parent_class, parent_relation_field)

                if parent_relation_field_obj.relation_class == cls:
                    data = [
                        elem for elem
                        in cls.storage.find(
                            parent_class_table,
                            {parent_relation_field: get_obj.id})]
                    if len(data) > 0:
                        if not resolver_field_obj.is_multiple:
                            parent = parent_class(**dict(data[0]))
                            setattr(get_obj, resolver_field, parent)
                        else:
                            elements = []
                            for row in data:
                                elements.append(parent_class(**dict(row)))
                                setattr(get_obj, resolver_field, elements)

        return get_obj

    @classmethod
    def find(cls, **fil):
        data = cls.storage.find(cls.get_table_name(), fil)

        return [
            cls.from_dictionary(row, sensitive_fields=True) for row
            in data]

    @classmethod
    def delete(cls, **fil):
        return cls.storage.delete(cls.get_table_name(), fil)

    @property
    def dictionary(self):
        return {
            field_name: getattr(self, field_name) for field_name
            in self.get_fields()}

    @property
    def modified_dictionary(self):
        return {
            field_name: getattr(self, field_name) for field_name
            in self.get_modified_fields()}

    @property
    def unsensitive_dictionary(self):
        return {
            field_name: getattr(self, field_name) for field_name
            in self.get_unsensitive_fields()}

    def __str__(self):
        return f'{self.__class__.__name__}: id {self.id}'

    def __setattr__(self, name, value):
        if name in self.__dict__.get('fields', {}):
            self.__dict__['fields'][name].__set__(self, value)
        else:
            self.__dict__[name] = value

    def __getattribute__(self, name):
        if name == '__dict__':
            return object.__getattribute__(self, '__dict__')
        elif name in self.__dict__.get('fields', {}):
            return self.__dict__['fields'][name].__get__(self, None)
        else:
            return object.__getattribute__(self, name)

    def default(self):
        return self.dictionary

    def save(self):
        if not self.id:
            self.id = self.storage.insert(self)
        else:
            self.updated = None
            self.storage.update(self)
