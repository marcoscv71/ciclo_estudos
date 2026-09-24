from fastapi import FastAPI

from ciclo_estudos.routers import (
    auth,
    cycles,
    health,
    study_sessions,
    subjects,
    users,
)

app = FastAPI(title='Ciclo de Estudos TCE-GO')

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(subjects.router)
app.include_router(study_sessions.router)
app.include_router(cycles.router)
