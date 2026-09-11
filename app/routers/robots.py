from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import datetime

router = APIRouter(prefix="/api/robots", tags=["Robots"])

@router.get("")
def list_robots(db: Session = Depends(get_db)):
    robots = db.query(models.Robot).all()
    results = []
    for r in robots:
        # Lấy task hiện tại nếu có
        current_task = db.query(models.Task).filter(
            models.Task.robot_id == r.robot_id,
            models.Task.status.in_(["Assigned", "In_Progress"])
        ).first()

        results.append({
            "robot_id": r.robot_id,
            "robot_name": r.robot_name,
            "battery_level": r.battery_level,
            "current_x": r.current_x,
            "current_y": r.current_y,
            "max_payload_kg": r.max_payload_kg,
            "status": r.status,
            "current_task": {
                "task_id": current_task.task_id,
                "package_id": current_task.package_id,
                "source": current_task.source_location,
                "target": current_task.target_location,
                "priority": current_task.priority
            } if current_task else None
        })
    return results

@router.post("/{robot_id}/command")
def send_robot_command(robot_id: str, action: str, db: Session = Depends(get_db)):
    robot = db.query(models.Robot).filter(models.Robot.robot_id == robot_id).first()
    if not robot:
        raise HTTPException(status_code=404, detail="Không tìm thấy robot")

    if action == "charge":
        robot.status = "Charging"
    elif action == "resume":
        robot.status = "Idle"
    elif action == "emergency_stop":
        robot.status = "Maintenance"
    
    db.commit()
    return {"message": f"Đã gửi lệnh {action} tới {robot.robot_name}", "status": robot.status}
