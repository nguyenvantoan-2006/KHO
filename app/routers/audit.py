from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(prefix="/api/audit", tags=["Audit"])

@router.get("")
def list_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(50).all()
    results = []
    for l in logs:
        user_name = "Hệ thống"
        if l.user:
            user_name = f"{l.user.full_name} ({l.user.role})"
        results.append({
            "log_id": l.log_id,
            "user_name": user_name,
            "endpoint": l.endpoint,
            "http_method": l.http_method,
            "ip_address": l.ip_address,
            "action_desc": l.action_desc,
            "status_code": l.status_code,
            "created_at": l.created_at.strftime("%H:%M:%S %d/%m/%Y")
        })
    return results
