import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./warehouse.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from app import models
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    # Kiểm tra xem đã có dữ liệu mẫu chưa
    if db.query(models.User).first():
        db.close()
        return

    print("[DB] Khoi tao du lieu mau cho He thong Kho thong minh...")

    # 1. Khởi tạo Users (Admin Nguyễn Văn Toàn, Quản lý Trần Thị Loan, Nhân viên)
    admin_user = models.User(
        user_id="USR-001",
        username="admin",
        hashed_password="hashed_admin_pass_123",
        full_name="Nguyễn Văn Toàn",
        role="Admin"
    )
    manager_user = models.User(
        user_id="USR-002",
        username="loan_manager",
        hashed_password="hashed_loan_pass_123",
        full_name="Trần Thị Loan",
        role="Manager"
    )
    staff_user = models.User(
        user_id="USR-003",
        username="kho_staff1",
        hashed_password="hashed_staff_pass_123",
        full_name="Lê Hoàng Nam",
        role="Staff"
    )
    db.add_all([admin_user, manager_user, staff_user])

    # 2. Khởi tạo Sorting Gates (3 Cổng phân loại IoT)
    gates = [
        models.SortingGate(gate_id="GATE-01", target_zone="Miền Bắc (Hà Nội, Hải Phòng)", is_active=True, diverter_open=True, processed_count=420),
        models.SortingGate(gate_id="GATE-02", target_zone="Miền Trung (Đà Nẵng, Huế)", is_active=True, diverter_open=False, processed_count=285),
        models.SortingGate(gate_id="GATE-03", target_zone="Miền Nam (TP.HCM, Cần Thơ)", is_active=True, diverter_open=True, processed_count=615)
    ]
    db.add_all(gates)

    # 3. Khởi tạo Storage Locations (Zone A: Tiêu chuẩn, Zone B: Cồng kềnh, Zone C: Giá trị cao)
    locations = []
    zones = [("Zone A", 10), ("Zone B", 6), ("Zone C", 4)]
    for zone_name, count in zones:
        for i in range(1, count + 1):
            loc_id = f"{zone_name.split()[-1]}-{i:02d}-01"
            is_occ = (i % 2 == 1 or i == 2)
            locations.append(
                models.StorageLocation(
                    location_id=loc_id,
                    zone_id=zone_name,
                    aisle=f"Dãy {zone_name.split()[-1]}1",
                    shelf_level=1,
                    max_capacity_kg=300.0 if zone_name == "Zone A" else 800.0,
                    current_load_kg=120.5 if is_occ else 0.0,
                    is_occupied=is_occ
                )
            )
    db.add_all(locations)

    # 4. Khởi tạo Robots AMR
    robots = [
        models.Robot(robot_id="AMR-01", robot_name="Robot Tự Hành Alpha", battery_level=92.0, current_x=45.0, current_y=120.0, max_payload_kg=150.0, status="Moving"),
        models.Robot(robot_id="AMR-02", robot_name="Robot Tự Hành Beta", battery_level=78.5, current_x=120.0, current_y=80.0, max_payload_kg=200.0, status="Carrying"),
        models.Robot(robot_id="AMR-03", robot_name="Robot Tự Hành Gamma", battery_level=35.0, current_x=220.0, current_y=40.0, max_payload_kg=150.0, status="Charging")
    ]
    db.add_all(robots)

    # 5. Khởi tạo Shipment & DispatchOrder
    shipment1 = models.Shipment(
        shipment_id="SHIP-202609-01",
        supplier_name="Shopee Express Logistics Hub",
        vehicle_number="29C-889.92",
        expected_time=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
        received_time=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
        total_packages=24,
        status="Completed",
        received_by="USR-003"
    )
    db.add(shipment1)

    dispatch1 = models.DispatchOrder(
        order_id="DSP-202609-01",
        created_by="USR-001",
        order_type="Xuất liên tỉnh",
        destination_hub="Hub Trung Chuyển Miền Nam - Tân Bình",
        total_packages=12,
        status="In_Progress",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=2)
    )
    db.add(dispatch1)
    db.commit()

    # 6. Khởi tạo Packages (Kiện hàng đa dạng)
    packages_data = [
        ("PKG-1001", "SPX8829104VN", 2.5, 0.015, "Stored", "Tiêu chuẩn", "A-01-01", "GATE-01", None),
        ("PKG-1002", "SPX8829105VN", 15.0, 0.080, "Stored", "Cồng kềnh", "B-01-01", "GATE-02", None),
        ("PKG-1003", "SPX8829106VN", 0.8, 0.005, "Dispatched", "Giá trị cao", "C-01-01", "GATE-03", "DSP-202609-01"),
        ("PKG-1004", "SPX8829107VN", 3.2, 0.020, "Sorted", "Tiêu chuẩn", None, "GATE-01", None),
        ("PKG-1005", "SPX8829108VN", 4.1, 0.025, "Received", "Tiêu chuẩn", None, None, None),
        ("PKG-1006", "SPX8829109VN", 1.2, 0.008, "Stored", "Tiêu chuẩn", "A-02-01", "GATE-01", None),
        ("PKG-1007", "SPX8829110VN", 25.0, 0.150, "Stored", "Cồng kềnh", "B-02-01", "GATE-02", None),
        ("PKG-1008", "SPX8829111VN", 0.5, 0.003, "Sorted", "Giá trị cao", None, "GATE-03", None),
        ("PKG-1009", "SPX8829112VN", 5.6, 0.035, "Received", "Tiêu chuẩn", None, None, None),
        ("PKG-1010", "SPX8829113VN", 8.4, 0.045, "Stored", "Tiêu chuẩn", "A-03-01", "GATE-01", None),
        ("PKG-1011", "SPX8829114VN", 1.9, 0.012, "Dispatched", "Tiêu chuẩn", None, "GATE-01", "DSP-202609-01"),
        ("PKG-1012", "SPX8829115VN", 12.0, 0.070, "Stored", "Cồng kềnh", "B-03-01", "GATE-02", None)
    ]

    for p_id, trk, w, v, st, cat, loc, gate, dsp in packages_data:
        pkg = models.Package(
            package_id=p_id,
            tracking_number=trk,
            weight_kg=w,
            volume_m3=v,
            status=st,
            category=cat,
            shipment_id="SHIP-202609-01",
            location_id=loc,
            gate_id=gate,
            dispatch_order_id=dsp,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=45)
        )
        db.add(pkg)
        db.commit()

        # Thêm lịch sử truy vết
        hist1 = models.InventoryHistory(
            package_id=p_id,
            from_location="Cảng nhập số 1",
            to_location="Băng chuyền IoT",
            action_type="CheckIn",
            performed_by="Lê Hoàng Nam (Staff)",
            notes="Kiểm đếm quét mã QR thành công"
        )
        db.add(hist1)

        if st in ["Sorted", "Stored", "Dispatched"]:
            hist2 = models.InventoryHistory(
                package_id=p_id,
                from_location="Băng chuyền IoT",
                to_location=gate if gate else "GATE-01",
                action_type="Sorting",
                performed_by="IoT Smart Sorting Gate",
                notes="AI Computer Vision phân loại tự động"
            )
            db.add(hist2)

        if st in ["Stored", "Dispatched"]:
            hist3 = models.InventoryHistory(
                package_id=p_id,
                from_location=gate if gate else "GATE-01",
                to_location=loc if loc else "A-01-01",
                action_type="PutAway",
                performed_by="AMR-01 (Robot tự hành)",
                notes="Tối ưu đường đi A* lưu kho thành công"
            )
            db.add(hist3)

        if st == "Dispatched":
            hist4 = models.InventoryHistory(
                package_id=p_id,
                from_location=loc,
                to_location="Cửa xuất xe tải T01",
                action_type="Dispatch",
                performed_by="AMR-02 (Robot tự hành)",
                notes=f"Đóng gói theo lệnh {dsp}"
            )
            db.add(hist4)

    # 7. Khởi tạo Tasks
    tasks_data = [
        ("TSK-01", "AMR-01", "PKG-1004", "GATE-01", "A-05-01", 2, "In_Progress"),
        ("TSK-02", "AMR-02", "PKG-1008", "GATE-03", "C-02-01", 1, "Assigned"),
        ("TSK-03", None, "PKG-1005", "Cảng nhập", "GATE-01", 3, "Queued")
    ]
    for tid, rid, pid, src, tgt, prio, st in tasks_data:
        task = models.Task(
            task_id=tid,
            robot_id=rid,
            package_id=pid,
            source_location=src,
            target_location=tgt,
            priority=prio,
            status=st
        )
        db.add(task)

    # 8. Khởi tạo Audit Logs
    audit_samples = [
        ("USR-001", "/api/v1/auth/login", "POST", "192.168.1.15", "Đăng nhập hệ thống thành công (Role: Admin)", 200),
        ("USR-001", "/api/v1/dispatch/create", "POST", "192.168.1.15", "Phê duyệt lệnh xuất kho DSP-202609-01", 200),
        ("USR-002", "/api/v1/ai/optimize-path", "GET", "192.168.1.28", "Chạy thuật toán tối ưu A* cho AMR-01", 200),
        ("USR-003", "/api/v1/packages/scan", "POST", "192.168.1.42", "Quét mã vạch tiếp nhận lô hàng SHIP-202609-01", 200)
    ]
    for uid, ep, meth, ip, desc, sc in audit_samples:
        log = models.AuditLog(
            user_id=uid,
            endpoint=ep,
            http_method=meth,
            ip_address=ip,
            action_desc=desc,
            status_code=sc,
            created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15)
        )
        db.add(log)

    db.commit()
    db.close()
    print("[DB] Khoi tao hoan tat 10 bang du lieu mau thanh cong!")
