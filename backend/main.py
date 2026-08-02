from fastapi import FastAPI

app = FastAPI(
    title="PAIOS",
    version="0.0.1"
)

@app.get("/")
def root():
    return {
        "system": "PAIOS",
        "status": "ONLINE",
        "version": "0.0.1"
    }