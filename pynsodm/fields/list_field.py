from .base_field import BaseField


class ListField(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)

    def __set__(self, obj, value):
        self.value = list(value)

    def __get__(self, obj, type):
        if not obj:
            return self
        return self.value if self.value else []
