from pynsodm.fields import BaseField, IDField, DatetimeField


class BaseModel:

  table_name: str = None
  storage = None

  id = IDField()
  created = DatetimeField(is_index=True)
  updated = DatetimeField(is_index=True)

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
    return [k for k,v in cls.get_fields_values().items() if v.is_index and not v.is_primary]

  @classmethod
  def get_unsensitive_fields(cls): 
    return [k for k,v in cls.get_fields_values().items() if not v.is_sensitive]

  @classmethod
  def get_modified_fields(cls):
    return [k for k,v in cls.get_fields_values().items() if v.is_modified]

  @classmethod
  def get_primary_index(cls):
    primary_indexes = [k for k,v in cls.get_fields_values().items() if v.is_primary]
    if len(primary_indexes) > 0:
      return primary_indexes[0]
    return None

  @classmethod
  def set_storage(cls, value):
    cls.storage = value

  @property
  def dictionary(self):
    return { field_name:getattr(self, field_name) for field_name in self.get_fields() }

  @property
  def modified_dictionary(self):
    return { field_name:getattr(self, field_name) for field_name in self.get_modified_fields() }

  @property
  def unsensitive_dictionary(self):
    return { field_name:getattr(self, field_name) for field_name in self.get_unsensitive_fields() }

  def default(self):
    return self.dictionary

  def save(self):
    if not self.id:
      self.id = self.storage.insert(self)
    else:
      self.updated = None
      self.storage.update(self)

