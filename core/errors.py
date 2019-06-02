

class ValidationError(Exception):

    def __init__(self, error=None):
        self.error = error
