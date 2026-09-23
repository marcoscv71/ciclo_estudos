from ciclo_estudos.exceptions import InvalidCredentialsError
from ciclo_estudos.repositories.users import UserRepository
from ciclo_estudos.security import create_access_token, verify_password


class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def login(self, email: str, password: str) -> str:
        user = self.repository.get_by_email(email)

        if not user or not verify_password(password, user.password):
            raise InvalidCredentialsError()

        return create_access_token(data={'sub': user.email})
