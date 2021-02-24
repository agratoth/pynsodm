from .base_field import BaseField
from .one_to_one_resolver_field import OTOResolver


class OTORelation(BaseField):
    def __init__(self, relation_class, backfield=None, **kwargs):
        self._relation_class = relation_class
        self._backfield = backfield
        self._resolver = OTOResolver

        kwargs['is_relation'] = True

        BaseField.__init__(self, **kwargs)

    def __set__(self, obj, value):
        self.value = value if isinstance(value, str) else value.id

    def __get__(self, obj, type):
        if not obj:
            return self
        return self._relation_class.get(self.value)

    @property
    def relation_class(self): return self._relation_class

    @property
    def backfield(self): return self._backfield

    @property
    def resolver(self): return self._resolver
