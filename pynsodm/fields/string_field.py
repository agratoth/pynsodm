from pynsodm.exceptions import ListItemException

from .base_field import BaseField


class StringField(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)
        self._items = kwargs.get('items', [])

    def __set__(self, obj, value):
        str_val = str(value)
        if not obj._exist_object:
            if len(self._items) > 0 and str_val not in self._items:
                raise ListItemException()
            self.value = str_val
        else:
            self.safety_value = str_val

    def __get__(self, obj, type):
        if not obj:
            return self
        return self.value if self.value else ''
