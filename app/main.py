from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import os

from app.database import init_db
from app.routers import dashboard, packages, robots, users, audit

app = FastAPI(
    title="SPX Smart Logistics - AI & IoT Warehouse Control Center",
    version="1.0.0",
    description="Hệ thống Quản lý kho thông minh tích hợp AI & Thiết bị IoT Smart Sorting"
)

# Khởi tạo thư mục static & templates nếu chưa có
os.makedirs("app/static/css", exist_ok=True)
os.makedirs("app/static/js", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Đăng ký các API Routers
app.include_router(dashboard.router)
app.include_router(packages.router)
app.include_router(robots.router)
app.include_router(users.router)
app.include_router(audit.router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/")
def root():
    return RedirectResponse(url="/admin")

@app.get("/admin")
def admin_dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "admin_name": "Nguyễn Văn Toàn",
            "admin_role": "Chủ nhiệm đề tài / Admin",
            "app_title": "SPX Smart Logistics"
        }
    )
