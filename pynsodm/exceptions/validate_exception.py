class ValidateException(Exception):
    def __init__(self):
        Exception.__init__(self, 'Invalid value')
