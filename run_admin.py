import sys, os, time, webbrowser
import uvicorn

def main():
    print("=" * 65)
    print(">> SPX SMART LOGISTICS - KHOI CHAY GIAO DIEN QUAN TRI VIEN (ADMIN)")
    print("=" * 65)
    print(">> Chu nhiem de tai: Nguyen Van Toan (Admin / Backend / AI Lead)")
    print(">> Thanh vien du an: Tran Thi Loan (Manager / QA / BA)")
    print(">> Dia chi truy cap Web Admin:")
    print("   -> http://127.0.0.1:8000/admin")
    print("   -> API Swagger Docs: http://127.0.0.1:8000/docs")
    print("=" * 65)
    print(">> May chu dang khoi dong tren cong 8000...")

    # Khởi chạy FastAPI Server với uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
