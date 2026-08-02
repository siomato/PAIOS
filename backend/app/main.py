from fastapi import FastAPI
from app.routes.chat import router

app = FastAPI(
    title="PAIOS",
    version="0.0.1"
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "system": "PAIOS",
        "status": "ONLINE",
        "version": "0.0.1"
    }