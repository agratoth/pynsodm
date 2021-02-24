import validators as valid


def valid_email(data=''):
    return valid.email(data)


def valid_uuid(data=''):
    return valid.uuid(data)
