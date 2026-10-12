from fastapi import APIRouter

from .tariffs import catalog

router = APIRouter(prefix="/tariffs", tags=["tarifs"])


@router.get("")
def get_tariffs():
    """Grille tarifaire complète du Collège (publique : ce sont des prix affichés)."""
    return catalog()
