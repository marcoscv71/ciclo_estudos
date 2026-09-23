from ciclo_estudos.exceptions import UserAlreadyExistsError
from ciclo_estudos.models import User
from ciclo_estudos.repositories.users import UserRepository
from ciclo_estudos.security import get_password_hash


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create(self, username: str, email: str, password: str) -> User:
        if self.repository.get_by_username_or_email(username, email):
            raise UserAlreadyExistsError(email)

        return self.repository.add(
            User(
                username=username,
                email=email,
                password=get_password_hash(password),
            )
        )
