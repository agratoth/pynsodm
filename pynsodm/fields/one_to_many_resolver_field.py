from .base_field import BaseField


class OTMResolver(BaseField):
    def __init__(self, relation_class, **kwargs):
        self._relation_class = relation_class

        kwargs['is_resolver'] = True
        kwargs['is_multiple'] = True
        kwargs['is_field'] = False

        BaseField.__init__(self, **kwargs)

    def __set__(self, obj, value):
        self.value = value

    def __get__(self, obj, type):
        if not obj:
            return self
        return self.value

    @property
    def relation_class(self):
        return self._relation_class
