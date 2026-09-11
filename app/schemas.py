from pydantic import BaseModel
from typing import List, Optional
import datetime

class UserOut(BaseModel):
    user_id: str
    username: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        orm_mode = True

class PackageOut(BaseModel):
    package_id: str
    tracking_number: str
    weight_kg: float
    volume_m3: float
    status: str
    category: str
    location_id: Optional[str] = None
    gate_id: Optional[str] = None
    dispatch_order_id: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        orm_mode = True

class RobotOut(BaseModel):
    robot_id: str
    robot_name: str
    battery_level: float
    current_x: float
    current_y: float
    max_payload_kg: float
    status: str

    class Config:
        orm_mode = True

class AuditLogOut(BaseModel):
    log_id: int
    user_id: Optional[str]
    endpoint: str
    http_method: str
    ip_address: str
    action_desc: str
    status_code: int
    created_at: datetime.datetime

    class Config:
        orm_mode = True
