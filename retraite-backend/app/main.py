import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .admin_router import router as admin_stats_router
from .assistant.admin_router import router as assistant_admin_router
from .assistant.client_router import router as assistant_client_router
from .auth_router import router as auth_router
from .database import Base, engine
from .logging_config import setup_logging
from .reservations_router import router as reservations_router
from .seed import seed_initial_users

setup_logging()
logger = logging.getLogger("retraite.main")

app = FastAPI(title="Réservation - Collège Catholique Bilingue de la Retraite")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed_initial_users()
    logger.info("Application démarrée.")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Erreur non gérée sur %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur."})


app.include_router(auth_router)
app.include_router(reservations_router)
app.include_router(assistant_client_router)
app.include_router(assistant_admin_router)
app.include_router(admin_stats_router)


@app.get("/health")
def health():
    return {"status": "ok"}
