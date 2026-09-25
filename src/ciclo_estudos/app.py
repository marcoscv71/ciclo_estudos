from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ciclo_estudos.routers import (
    auth,
    cycles,
    health,
    study_sessions,
    subjects,
    users,
)

app = FastAPI(title='Ciclo de Estudos')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173', 'https://127.0.0.1:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(study_sessions.router)
app.include_router(cycles.router)
