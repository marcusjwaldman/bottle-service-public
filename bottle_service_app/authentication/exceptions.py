class AuthenticationExpiredException(Exception):

    def __init__(self, message="Authentication expired. Please login again."):
        self.message = message
        super().__init__(self.message)


class AuthenticationMissingException(Exception):

    def __init__(self, message="No Authentication found. Please login again."):
        self.message = message
        super().__init__(self.message)
