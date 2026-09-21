from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, UserRole
from .schemas import AdminOverviewOut
from .security import require_roles
from .stats import monthly_overview

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminOverviewOut)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.dev)),
):
    return monthly_overview(db)
