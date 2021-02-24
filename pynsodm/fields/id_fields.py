from .base_field import BaseField


class IDField(BaseField):
    def __init__(self, **kwargs):
        if 'is_primary' not in kwargs:
            kwargs['is_primary'] = True
            kwargs['is_index'] = True

        if 'is_sensitive' not in kwargs:
            kwargs['is_sensitive'] = True

        BaseField.__init__(self, **kwargs)

    def __set__(self, obj, value):
        self.value = str(value) if value else None

    def __get__(self, obj, type):
        if not obj:
            return self
        return self.value if self.value else None
