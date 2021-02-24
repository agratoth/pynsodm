import json

from datetime import datetime

from pynsodm.rethinkdb_ext import BaseModel


def encoder(sensitive_fields=False, dt_format='%Y.%m.%d %H:%M:%S.%f'):
    class ModelEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, BaseModel):
                if sensitive_fields:
                    return obj.dictionary
                else:
                    return obj.unsensitive_dictionary
            elif isinstance(obj, datetime):
                return obj.strftime(dt_format)
    return ModelEncoder
