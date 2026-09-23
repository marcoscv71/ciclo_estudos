from sqlalchemy import select
from sqlalchemy.orm import Session

from ciclo_estudos.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def get_by_username_or_email(
        self, username: str, email: str
    ) -> User | None:
        return self.session.scalar(
            select(User).where(
                (User.username == username) | (User.email == email)
            )
        )

    def add(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user
