# Ciclo de Estudos - API

## Contexto do projeto

API de gestao de ciclo de estudos para concurso publico. Uso pessoal, um usuario.

Dominio:

- Disciplina (subject): nome unico e meta de horas.
- Sessao de estudo (study session): bloco de minutos registrado em uma disciplina.
- Ciclo (cycle): rodada atual. Fecha quando todas as metas sao atingidas e um novo comeca.

Regra central: o progresso e **derivado** da soma das sessoes do ciclo aberto. Nao existe coluna de horas concluidas. Apagar uma sessao corrige o progresso sozinho.

## Stack

- Python 3.14, FastAPI, SQLAlchemy 2 (modelos como dataclasses), Pydantic v2
- SQLite, migracoes com Alembic
- uv (dependencias), Ruff (lint e format), pytest, Poe (tarefas)
- API REST sincrona. Nao usar async sem pedido explicito.

## Arquitetura

Tres camadas, dependencia sempre para baixo:

```
routers/       HTTP: recebe, chama o servico, traduz excecao de dominio em status code
services/      regras de negocio
repositories/  acesso a dados
```

Regras invioláveis:

- `routers/` nao pode importar SQLAlchemy, `select`, `Session` nem repositorios. So `dependencies.py`, schemas, excecoes.
- `services/` nao pode importar FastAPI, `HTTPException` nem status codes. Levanta excecao de `exceptions.py`.
- `repositories/` e o unico lugar com SQL. Devolve `None` quando nao acha, nunca levanta erro de dominio.
- A montagem das camadas vive em `dependencies.py`. Nenhum router monta servico por conta propria.

Arquivos de apoio:

- `domain.py`: objetos de progresso, com campos calculados por `@property`
- `exceptions.py`: erros de dominio, sem status HTTP
- `schemas.py`: contratos de entrada e saida
- `security.py`: hash de senha e JWT
- `settings.py`: configuracao via `.env`

## Convencoes

- Codigo, nomes, testes e mensagens de commit em ingles. Texto exibido ao usuario final em portugues.
- Commits no padrao Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `test:`).
- Tempo e armazenado em minutos inteiros. Horas sao calculadas na exibicao.
- Datas sempre em UTC, expostas no JSON com sufixo `Z`.
- O servidor decide o `cycle_id` de uma sessao. O cliente nunca envia.

## Padroes de API

- POST cria e devolve 201. GET devolve 200. Recurso inexistente devolve 404.
- Conflito de unicidade devolve 409. Dado invalido devolve 422 (validacao do Pydantic).
- 401 e falta de autenticacao. 403 e operacao proibida para todos.
- Toda rota de `/subjects/`, `/sessions/` e `/cycles/` exige JWT.
- Listagens aceitam `offset` e `limit` via `FilterPage`.

## Testes

- Toda rota nova precisa de teste de sucesso e de cada caminho de erro.
- Regra de negocio nova precisa de teste de unidade do servico, com repositorio falso, sem HTTP e sem banco.
- Testes nao podem depender do arquivo `.env`. Configuracao em teste entra por `dependency_overrides`.
- Fixtures disponiveis em `conftest.py`: `session`, `client`, `user`, `token`, `subject`, `mock_db_time`.
- A ordem dos testes e aleatoria. Cada teste prepara o que precisa.

## Comandos

```
uv sync                       instala dependencias
uv run poe lint               ruff check
uv run poe format             corrige e formata
uv run poe test               lint + pytest + cobertura
uv run poe serve              servidor local
uv run poe seed               cria disciplinas e usuario inicial
uv run alembic revision --autogenerate -m "mensagem"
uv run alembic upgrade head
```

## Criterios de sucesso

Uma tarefa so esta pronta quando:

1. `uv run poe format` roda sem erro.
2. `uv run poe test` passa, com todos os testes verdes.
3. Nenhuma camada foi violada (checar com `grep -rn "Repository\|get_session\|sqlalchemy" src/ciclo_estudos/routers/`).
4. Mudanca de modelo tem migracao gerada, revisada e aplicada.
5. Mudanca de contrato da API esta refletida nos tipos do frontend (repositorio separado) e isso foi avisado.

## Estrategia de execucao

1. Escrever o plano com criterios verificaveis por etapa antes de codar.
2. Executar uma etapa por vez, rodando os testes a cada uma.
3. Apresentar evidencia de cada correcao: saida do comando, nao afirmacao.
4. Parar e perguntar quando a tarefa exigir decisao de produto ou mudanca irreversivel de dados.

## Padroes de codigo

1. Simplicidade acima de tudo. Nao antecipar necessidade, nao criar abstracao sem uso real.
2. Nao adicionar dependencia nova sem justificar.
3. Nao programar defensivamente sem motivo: validacao de entrada e responsabilidade do Pydantic.
4. Sem emojis no codigo, nos commits e nos arquivos do repositorio.
5. Limite de 79 caracteres por linha, aspas simples (configuracao do Ruff).

## Fora de escopo

Nao implementar sem pedido: multiusuario, compartilhamento, notificacoes no servidor, cache, fila, GraphQL, async, Docker.
