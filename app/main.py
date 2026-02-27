from fastapi import FastAPI
from app.api.v1 import leads, dashboard
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="CRM Backend")

app.include_router(leads.router)
app.include_router(dashboard.router)


@app.get("/")
async def health():
    return {"status": "ok"}

