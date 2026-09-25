"""Cria o usuário inicial e as disciplinas do ciclo."""

import sys
from getpass import getpass

from sqlalchemy.orm import Session

from ciclo_estudos.database import engine
from ciclo_estudos.exceptions import (
    SubjectAlreadyExistsError,
    UserAlreadyExistsError,
)
from ciclo_estudos.repositories.subjects import SubjectRepository
from ciclo_estudos.repositories.users import UserRepository
from ciclo_estudos.services.subjects import SubjectService
from ciclo_estudos.services.users import UserService

MIN_PASSWORD_LENGTH = 8

SUBJECTS = [
    ('TI - Engenharia de Software & Governança', 3.0),
    ('Gerais - Língua Portuguesa', 2.0),
    ('TI - Banco de Dados & IA', 3.0),
    ('Gerais - Raciocínio Lógico-Matemático', 2.0),
    ('TI - Segurança & Redes', 3.0),
    ('TI - Cloud & Infraestrutura', 3.0),
    ('Gerais - Legislação Institucional', 1.0),
    ('Discursiva - Estudo de Caso (TI)', 3.0),
]


def seed_subjects(session: Session) -> None:
    service = SubjectService(SubjectRepository(session))

    for name, target_hours in SUBJECTS:
        try:
            service.create(name, target_hours)
            print(f'  + {name} ({target_hours}h)')
        except SubjectAlreadyExistsError:
            print(f'  = {name} (já existe)')


def seed_user(session: Session) -> None:
    print('\nUsuário inicial (deixe o e-mail vazio para pular):')
    email = input('  E-mail: ').strip()

    if not email:
        print('  Pulado.')
        return

    username = input('  Nome de usuário: ').strip()
    password = getpass('  Senha: ')

    if len(password) < MIN_PASSWORD_LENGTH:
        print(f'  Senha muito curta (mínimo {MIN_PASSWORD_LENGTH}).')
        sys.exit(1)

    service = UserService(UserRepository(session))

    try:
        user = service.create(username, email, password)
        print(f'  + Usuário {user.username} criado.')
    except UserAlreadyExistsError:
        print('  = Usuário ou e-mail já cadastrado.')


def main() -> None:
    print('Disciplinas:')

    with Session(engine) as session:
        seed_subjects(session)
        seed_user(session)

    print('\nPronto.')


if __name__ == '__main__':
    main()
