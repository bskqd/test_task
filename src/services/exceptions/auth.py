class IncorrectPasswordException(Exception):
    def __init__(self):
        super().__init__("Incorrect password")


class InvalidNicknameException(Exception):
    def __init__(self):
        super().__init__("User with such nickname is not found")
