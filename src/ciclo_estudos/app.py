from fastapi import FastAPI

from ciclo_estudos.routers import auth, health, subjects, users

app = FastAPI(title='Ciclo de Estudos TCE-GO')

app.include_router(health.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(subjects.router)
