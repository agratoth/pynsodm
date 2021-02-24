class ListItemException(Exception):
    def __init__(self):
        Exception.__init__(
            self, 'Value is not included in the list of valid values')
