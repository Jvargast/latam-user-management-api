class UserDomainError(Exception):
    pass


class UserNotFoundError(UserDomainError):
    pass


class UserAlreadyExistsError(UserDomainError):
    pass
