import os
import pytz
from datetime import datetime

from .base_field import BaseField

TIMEZONE = os.environ.get('TIMEZONE', 'UTC')


class DatetimeField(BaseField):
    def __init__(self, **kwargs):
        BaseField.__init__(self, **kwargs)

        self._timezone = pytz.timezone(TIMEZONE)

    def __set__(self, obj, value):
        if not value:
            self.value = self._timezone.localize(datetime.utcnow())
        else:
            self.value = self._timezone.localize(value) \
                if not value.tzinfo \
                else value

    def __get__(self, obj, type):
        if not obj:
            return self
        return self.value \
            if self.value \
            else self._timezone.localize(datetime.utcnow())
