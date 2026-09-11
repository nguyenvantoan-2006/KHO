# SPX SMART LOGISTICS - AI & IoT WAREHOUSE MANAGEMENT SYSTEM

Hệ thống Quản lý Kho Logistics Thông Minh tích hợp Trí Tuệ Nhân Tạo (AI Decision Engine) và Thiết Bị Phân Loại Tự Động (IoT Smart Sorting).

## 👥 Thành Viên Thực Hiện Đề Tài
- **Nguyễn Văn Toàn**: Chủ nhiệm đề tài / Quản lý dự án / Lập trình Backend, AI & Giao diện Admin.
- **Trần Thị Loan**: Quản lý chất lượng (QA) / Phân tích yêu cầu (BA) / Thiết kế trải nghiệm người dùng (UI/UX).

---

## 🌟 Tính Năng Nổi Bật

### 1. Giao Diện Quản Trị Viên (Admin Dashboard)
- Thiết kế phong cách **Modern Dark Mode** kết hợp hiệu ứng kính mờ **Glassmorphism** cao cấp.
- **5 Thẻ KPI Thời Gian Thực**: Theo dõi tổng kiện hàng, tiếp nhận trong ngày, tỷ lệ lấp đầy ô kệ, số lượng xe tự hành Robot AMR và trạng thái AI Engine.
- **Sơ Đồ Kho 2D Tương Tác (Live Simulation Canvas)**:
  - Băng chuyền con lăn chuyển động liên tục.
  - 3 Cổng phân loại IoT (Miền Bắc, Miền Trung, Miền Nam) có đèn LED trạng thái.
  - Các Zone lưu trữ ô kệ (Zone A: Tiêu chuẩn, Zone B: Cồng kềnh, Zone C: Giá trị cao) và Cửa xuất hàng.
  - Đội xe Robot AMR (`Alpha`, `Beta`) tự động di chuyển gắp và phân bổ kiện hàng vào ô kệ.
- **Biểu Đồ Trực Quan (Chart.js)**: Lưu lượng hàng hóa theo từng khung giờ và phân bổ tồn kho theo Zone.
- **Cảnh Báo AI Thông Minh**: Phát hiện nguy cơ ùn tắc tại các cổng phân loại, đề xuất vị trí lưu kho tối ưu A*.
- **Quản Lý Kiện Hàng & Timeline Truy Vết**: Tra cứu nhanh Barcode, lọc theo trạng thái, xem lộ trình từng bước từ nhập kho đến xuất xưởng.
- **Phân Quyền RBAC**: Quản lý tài khoản Admin, Manager, Staff.
- **Nhật Ký Kiểm Toán (Audit Log)**: Ghi nhận lịch sử thao tác phục vụ an ninh hệ thống.

---

## 🛠️ Công Nghệ Sử Dụng

- **Ngôn ngữ lập trình**: Python 3.10+
- **Backend Framework**: FastAPI, Uvicorn
- **Cơ sở dữ liệu**: SQLite / PostgreSQL, SQLAlchemy ORM
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism), JavaScript (ES6+), Chart.js
- **Mô hình phát triển**: Agile Scrum (6 Sprint)

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy

1. **Cài đặt thư viện phụ thuộc:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Khởi chạy hệ thống 1-click:**
   ```bash
   python run_admin.py
   ```

3. **Truy cập hệ thống:**
   - **Giao diện Admin Dashboard:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
   - **Tài liệu API Swagger tự động:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📄 Tài Liệu Đồ Án Chi Tiết

File báo cáo thuyết minh đồ án hoàn chỉnh:
- `TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG_HOAN_CHINH.docx`
