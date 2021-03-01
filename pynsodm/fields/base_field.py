from pynsodm.exceptions import ValidateException


class BaseField:
    def __init__(self, **kwargs):
        self._is_index = kwargs.get('is_index', False)
        self._is_field = kwargs.get('is_field', True)
        self._is_primary = kwargs.get('is_primary', False)
        self._is_sensitive = kwargs.get('is_sensitive', False)
        self._is_relation = kwargs.get('is_relation', False)
        self._is_resolver = kwargs.get('is_resolver', False)
        self._is_multiple = kwargs.get('is_multiple', False)
        self._valid = kwargs.get('valid', None)
        self._handler = kwargs.get('handler', None)
        self._value = None
        self._is_modified = False

    @property
    def is_index(self) -> bool: return self._is_index

    @property
    def is_field(self) -> bool: return self._is_field

    @property
    def is_primary(self) -> bool: return self._is_primary

    @property
    def is_modified(self) -> bool: return self._is_modified

    @property
    def is_sensitive(self) -> bool: return self._is_sensitive

    @property
    def is_relation(self) -> bool: return self._is_relation

    @property
    def is_resolver(self) -> bool: return self._is_resolver

    @property
    def is_multiple(self) -> bool: return self._is_multiple

    @property
    def value(self): return self._value

    @value.setter
    def value(self, val):
        if self._valid and not self._valid(val):
            raise ValidateException()

        if self._handler:
            self._value = self._handler(val)
        else:
            self._value = val
        self._is_modified = True

    @property
    def safety_value(self): return self._value

    @safety_value.setter
    def safety_value(self, val):
        if self._valid and not self._valid(val):
            raise ValidateException()

        self._value = val
        self._is_modified = True