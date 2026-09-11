import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    """Bảng 38: Users (Người dùng) - Phân quyền RBAC"""
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(30), nullable=False)  # Admin / Manager / Staff
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")
    created_orders = relationship("DispatchOrder", back_populates="creator")
    received_shipments = relationship("Shipment", back_populates="receiver")

class StorageLocation(Base):
    """Bảng 40: StorageLocations (Vị trí ô kệ)"""
    __tablename__ = "storage_locations"

    location_id = Column(String(50), primary_key=True, index=True) # Ví dụ: A-01-01
    zone_id = Column(String(20), nullable=False)                    # Zone A, Zone B, Zone C
    aisle = Column(String(20), nullable=False)                      # Dãy kệ 01, 02
    shelf_level = Column(Integer, default=1)                        # Tầng 1, 2, 3
    max_capacity_kg = Column(Float, default=500.0)
    current_load_kg = Column(Float, default=0.0)
    is_occupied = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    packages = relationship("Package", back_populates="location")

class SortingGate(Base):
    """Bảng 41: SortingGates (Cổng phân loại IoT)"""
    __tablename__ = "sorting_gates"

    gate_id = Column(String(50), primary_key=True, index=True)     # GATE-01, GATE-02, GATE-03
    target_zone = Column(String(50), nullable=False)               # Miền Bắc, Miền Trung, Miền Nam
    is_active = Column(Boolean, default=True)
    diverter_open = Column(Boolean, default=False)                 # Cần gạt mở/đóng
    processed_count = Column(Integer, default=0)
    last_ping = Column(DateTime, default=datetime.datetime.utcnow)

    packages = relationship("Package", back_populates="gate")

class Shipment(Base):
    """Bảng 43: Shipments (Lô hàng tiếp nhận - FR-02)"""
    __tablename__ = "shipments"

    shipment_id = Column(String(50), primary_key=True, index=True)
    supplier_name = Column(String(100), nullable=False)
    vehicle_number = Column(String(30), nullable=False)
    expected_time = Column(DateTime)
    received_time = Column(DateTime, default=datetime.datetime.utcnow)
    total_packages = Column(Integer, default=0)
    status = Column(String(30), default="Processing")  # Incoming / Processing / Completed
    received_by = Column(String(50), ForeignKey("users.user_id"))

    receiver = relationship("User", back_populates="received_shipments")
    packages = relationship("Package", back_populates="shipment")

class DispatchOrder(Base):
    """Bảng 42: DispatchOrders (Lệnh xuất kho & điều phối)"""
    __tablename__ = "dispatch_orders"

    order_id = Column(String(50), primary_key=True, index=True)
    created_by = Column(String(50), ForeignKey("users.user_id"))
    order_type = Column(String(30), default="Xuất kho")
    destination_hub = Column(String(100), nullable=False)
    total_packages = Column(Integer, default=0)
    status = Column(String(30), default="Pending")     # Pending / In_Progress / Completed / Cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    creator = relationship("User", back_populates="created_orders")
    packages = relationship("Package", back_populates="dispatch_order")

class Package(Base):
    """Bảng 39: Packages (Kiện hàng)"""
    __tablename__ = "packages"

    package_id = Column(String(50), primary_key=True, index=True)
    tracking_number = Column(String(100), unique=True, index=True)
    weight_kg = Column(Float, nullable=False)
    volume_m3 = Column(Float, nullable=False)
    status = Column(String(50), default="Received")    # Received / Sorted / Stored / Dispatched
    category = Column(String(50), default="Tiêu chuẩn")

    shipment_id = Column(String(50), ForeignKey("shipments.shipment_id"), nullable=True)
    location_id = Column(String(50), ForeignKey("storage_locations.location_id"), nullable=True)
    gate_id = Column(String(50), ForeignKey("sorting_gates.gate_id"), nullable=True)
    dispatch_order_id = Column(String(50), ForeignKey("dispatch_orders.order_id"), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    shipment = relationship("Shipment", back_populates="packages")
    location = relationship("StorageLocation", back_populates="packages")
    gate = relationship("SortingGate", back_populates="packages")
    dispatch_order = relationship("DispatchOrder", back_populates="packages")
    history = relationship("InventoryHistory", back_populates="package", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="package")

class InventoryHistory(Base):
    """Bảng 44: InventoryHistory (Lịch sử truy vết & biến động hàng hóa - FR-06)"""
    __tablename__ = "inventory_history"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(String(50), ForeignKey("packages.package_id"), nullable=False)
    from_location = Column(String(50), nullable=True)
    to_location = Column(String(50), nullable=True)
    action_type = Column(String(50), nullable=False)   # CheckIn, Sorting, PutAway, Relocate, Pick, Dispatch
    performed_by = Column(String(50), nullable=False)  # Tên user hoặc mã Robot
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(String(255), nullable=True)

    package = relationship("Package", back_populates="history")

class Robot(Base):
    """Bảng 45: Robots (Danh mục Robot tự hành AMR/AGV - FR-AI-07)"""
    __tablename__ = "robots"

    robot_id = Column(String(50), primary_key=True, index=True)
    robot_name = Column(String(50), nullable=False)
    battery_level = Column(Float, default=100.0)
    current_x = Column(Float, default=10.0)
    current_y = Column(Float, default=10.0)
    max_payload_kg = Column(Float, default=100.0)
    status = Column(String(30), default="Idle")        # Idle, Moving, Carrying, Charging, Maintenance
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    tasks = relationship("Task", back_populates="robot")

class Task(Base):
    """Bảng 46: Tasks (Nhiệm vụ điều phối di chuyển & bốc xếp)"""
    __tablename__ = "tasks"

    task_id = Column(String(50), primary_key=True, index=True)
    robot_id = Column(String(50), ForeignKey("robots.robot_id"), nullable=True)
    package_id = Column(String(50), ForeignKey("packages.package_id"), nullable=True)
    source_location = Column(String(50), nullable=False)
    target_location = Column(String(50), nullable=False)
    priority = Column(Integer, default=3)              # 1: Khẩn, 2: Cao, 3: Tiêu chuẩn
    status = Column(String(30), default="Queued")      # Queued, Assigned, In_Progress, Finished, Cancelled
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    robot = relationship("Robot", back_populates="tasks")
    package = relationship("Package", back_populates="tasks")

class AuditLog(Base):
    """Bảng 47: AuditLog (Nhật ký an ninh & kiểm toán hệ thống - NFR-SEC-05)"""
    __tablename__ = "audit_log"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), ForeignKey("users.user_id"), nullable=True)
    endpoint = Column(String(100), nullable=False)
    http_method = Column(String(10), default="GET")
    ip_address = Column(String(45), default="127.0.0.1")
    action_desc = Column(String(255), nullable=False)
    status_code = Column(Integer, default=200)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="audit_logs")
