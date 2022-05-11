import enum

class AccessLevel(int, enum.Enum):
    ADMIN = 0
    MANAGER = 1
    CASHIER = 2


class PermissionDenied(RuntimeError):
    def __init__(self, access_level, required_level):
        super().__init__(f'Permission denied to {access_level}, required: {required_level}')
