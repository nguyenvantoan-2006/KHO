from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import random

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_packages = db.query(models.Package).count()
    stored_count = db.query(models.Package).filter(models.Package.status == "Stored").count()
    sorted_count = db.query(models.Package).filter(models.Package.status == "Sorted").count()
    received_count = db.query(models.Package).filter(models.Package.status == "Received").count()
    dispatched_count = db.query(models.Package).filter(models.Package.status == "Dispatched").count()

    total_locations = db.query(models.StorageLocation).count()
    occupied_locations = db.query(models.StorageLocation).filter(models.StorageLocation.is_occupied == True).count()
    occupancy_rate = round((occupied_locations / total_locations * 100), 1) if total_locations > 0 else 0

    total_robots = db.query(models.Robot).count()
    active_robots = db.query(models.Robot).filter(models.Robot.status.in_(["Moving", "Carrying"])).count()

    active_gates = db.query(models.SortingGate).filter(models.SortingGate.is_active == True).count()

    return {
        "total_packages": total_packages,
        "received_today": received_count + sorted_count + stored_count,
        "dispatched_today": dispatched_count,
        "stored_count": stored_count,
        "sorted_count": sorted_count,
        "occupancy_rate": occupancy_rate,
        "occupied_locations": occupied_locations,
        "total_locations": total_locations,
        "total_robots": total_robots,
        "active_robots": active_robots,
        "active_gates": active_gates,
        "ai_status": "Operational (99.8% Accuracy)"
    }

@router.get("/charts")
def get_chart_data(db: Session = Depends(get_db)):
    # 1. Dữ liệu lưu lượng nhập/xuất theo các khung giờ trong ngày
    hours = ["06:00", "08:00", "10:00", "12:00", "14:00", "16:00", "18:00", "20:00"]
    inbound_data = [45, 120, 240, 180, 310, 290, 150, 80]
    outbound_data = [20, 60, 140, 220, 260, 350, 210, 110]

    # 2. Phân bổ tồn kho theo Zone
    zone_a = db.query(models.StorageLocation).filter(models.StorageLocation.zone_id == "Zone A", models.StorageLocation.is_occupied == True).count()
    zone_b = db.query(models.StorageLocation).filter(models.StorageLocation.zone_id == "Zone B", models.StorageLocation.is_occupied == True).count()
    zone_c = db.query(models.StorageLocation).filter(models.StorageLocation.zone_id == "Zone C", models.StorageLocation.is_occupied == True).count()

    return {
        "timeline": {
            "labels": hours,
            "inbound": inbound_data,
            "outbound": outbound_data
        },
        "zones": {
            "labels": ["Zone A (Tiêu chuẩn)", "Zone B (Cồng kềnh)", "Zone C (Giá trị cao)"],
            "data": [zone_a or 6, zone_b or 4, zone_c or 2]
        }
    }

@router.get("/ai-alerts")
def get_ai_alerts():
    return [
        {
            "id": "ALT-01",
            "level": "warning",
            "title": "Cảnh báo nguy cơ ùn tắc Băng chuyền Cổng 1",
            "message": "Lưu lượng kiện hàng gửi về Miền Bắc đạt 85% công suất tối đa của Gate 01.",
            "time": "5 phút trước",
            "action": "Đề xuất mở phân luồng phụ sang Gate 02"
        },
        {
            "id": "ALT-02",
            "level": "info",
            "title": "Tối ưu hóa vị trí lưu kho A*",
            "message": "AI Decision Engine đã gợi ý vị trí ô kệ A-04-01 cho kiện hàng sắp tới, giảm 28% lộ trình di chuyển của Robot AMR-01.",
            "time": "12 phút trước",
            "action": "Đã tự động áp dụng"
        },
        {
            "id": "ALT-03",
            "level": "danger",
            "title": "Robot AMR-03 pin yếu (< 35%)",
            "message": "Robot AMR-03 đang tự động quay về trạm sạc Dock 02, tạm dừng gán task mới.",
            "time": "20 phút trước",
            "action": "Điều chuyển AMR-02 thay thế"
        }
    ]
