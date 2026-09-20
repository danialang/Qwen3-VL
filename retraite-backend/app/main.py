from fastapi import FastAPI

from .auth_router import router as auth_router
from .database import Base, engine
from .reservations_router import router as reservations_router
from .seed import seed_initial_users

app = FastAPI(title="Réservation - Collège Catholique Bilingue de la Retraite")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_initial_users()


app.include_router(auth_router)
app.include_router(reservations_router)


@app.get("/health")
def health():
    return {"status": "ok"}
