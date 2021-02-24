class NonexistentIDException(Exception):
    def __init__(self):
        Exception.__init__(self, 'ID is not exist')
