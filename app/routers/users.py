from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("")
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.strftime("%d/%m/%Y")
        }
        for u in users
    ]
