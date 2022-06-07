# validator errors
class DataValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)


# api errors, for client catch
class ApiError(Exception):
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
        super().__init__(msg)
