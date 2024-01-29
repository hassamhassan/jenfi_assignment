from typing import Dict
from fastapi import FastAPI
from routes.user import user_router
from routes.parcel import parcel_router
from routes.train import train_router

app = FastAPI(title="Jenfi Long Mail Service - API Documentation")


@app.get("/ping", tags=["Health"])
async def read_root() -> Dict:
    return {"message": "pong"}


app.router.prefix = "/api/v1"  # noqa

app.include_router(user_router, prefix="/users", tags=["Users"])
app.include_router(parcel_router, prefix="/parcels", tags=["Parcels"])
app.include_router(train_router, prefix="/trains", tags=["Trains"])
