class DomainError(Exception):
    """Base class for all business rule errors."""


class SubjectNotFoundError(DomainError):
    """The requested subject does not exist."""


class SubjectAlreadyExistsError(DomainError):
    """A subject with this name is already registered."""


class UserAlreadyExistsError(DomainError):
    """The username or email is already registered."""


class InvalidCredentialsError(DomainError):
    """The email or password is incorrect."""
