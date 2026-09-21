from fastapi import FastAPI

app = FastAPI(title="Ciclo de Estudos TCE-GO")


@app.get("/")
def read_root():
    return {"message": "API do Ciclo de Estudos TCE-GO"}
