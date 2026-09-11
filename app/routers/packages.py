from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app import models
import datetime

router = APIRouter(prefix="/api/packages", tags=["Packages"])

@router.get("")
def list_packages(
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Package)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (models.Package.package_id.ilike(s)) | 
            (models.Package.tracking_number.ilike(s))
        )
    if status and status != "All":
        query = query.filter(models.Package.status == status)

    packages = query.order_by(models.Package.created_at.desc()).all()
    results = []
    for p in packages:
        results.append({
            "package_id": p.package_id,
            "tracking_number": p.tracking_number,
            "weight_kg": p.weight_kg,
            "volume_m3": p.volume_m3,
            "status": p.status,
            "category": p.category,
            "location_id": p.location_id or "Chưa xếp",
            "gate_id": p.gate_id or "Chưa phân",
            "dispatch_order_id": p.dispatch_order_id or "-",
            "created_at": p.created_at.strftime("%H:%M %d/%m/%Y")
        })
    return results

@router.get("/{package_id}")
def get_package_detail(package_id: str, db: Session = Depends(get_db)):
    pkg = db.query(models.Package).filter(models.Package.package_id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy kiện hàng")

    history_records = db.query(models.InventoryHistory).filter(
        models.InventoryHistory.package_id == package_id
    ).order_by(models.InventoryHistory.timestamp.asc()).all()

    timeline = []
    for h in history_records:
        timeline.append({
            "history_id": h.history_id,
            "from_location": h.from_location or "Điểm đầu",
            "to_location": h.to_location or "Đích đến",
            "action_type": h.action_type,
            "performed_by": h.performed_by,
            "timestamp": h.timestamp.strftime("%H:%M:%S %d/%m/%Y"),
            "notes": h.notes
        })

    return {
        "package_id": pkg.package_id,
        "tracking_number": pkg.tracking_number,
        "weight_kg": pkg.weight_kg,
        "volume_m3": pkg.volume_m3,
        "status": pkg.status,
        "category": pkg.category,
        "location_id": pkg.location_id,
        "gate_id": pkg.gate_id,
        "dispatch_order_id": pkg.dispatch_order_id,
        "timeline": timeline
    }

@router.post("/{package_id}/status")
def update_package_status(package_id: str, new_status: str, db: Session = Depends(get_db)):
    pkg = db.query(models.Package).filter(models.Package.package_id == package_id).first()
    if not pkg:
        raise HTTPException(status_code=404, detail="Không tìm thấy kiện hàng")

    old_status = pkg.status
    pkg.status = new_status
    pkg.updated_at = datetime.datetime.utcnow()

    # Tự động ghi nhật ký biến động InventoryHistory
    hist = models.InventoryHistory(
        package_id=package_id,
        from_location=pkg.location_id or "Khu tiếp nhận",
        to_location=pkg.location_id or "Băng chuyền",
        action_type=f"StatusChanged_{new_status}",
        performed_by="Admin Console",
        notes=f"Chuyển trạng thái từ {old_status} sang {new_status}"
    )
    db.add(hist)
    db.commit()
    return {"message": "Cập nhật trạng thái thành công", "new_status": new_status}
