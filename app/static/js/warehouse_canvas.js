/**
 * SPX Smart Logistics - Warehouse Live 2D Interactive Map
 * Renders Warehouse layout, conveyor belt, IoT gates, and moving AMR Robots
 */

class WarehouseMap {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        
        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Định nghĩa các vùng trong kho
        this.zones = [
            { id: 'Zone A', name: 'Khu A: Tiêu chuẩn', x: 260, y: 50, w: 200, h: 120, color: 'rgba(59, 130, 246, 0.15)', border: '#3b82f6' },
            { id: 'Zone B', name: 'Khu B: Cồng kềnh', x: 490, y: 50, w: 180, h: 120, color: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b' },
            { id: 'Zone C', name: 'Khu C: Giá trị cao', x: 700, y: 50, w: 140, h: 120, color: 'rgba(168, 85, 247, 0.15)', border: '#a855f7' }
        ];

        // 3 Cổng phân loại IoT
        this.gates = [
            { id: 'GATE-01', name: 'Cổng 1 (Bắc)', x: 170, y: 80, active: true },
            { id: 'GATE-02', name: 'Cổng 2 (Trung)', x: 170, y: 150, active: false },
            { id: 'GATE-03', name: 'Cổng 3 (Nam)', x: 170, y: 220, active: true }
        ];

        // Đội xe Robot AMR mô phỏng
        this.robots = [
            { id: 'AMR-01', name: 'Alpha', x: 280, y: 220, targetX: 380, targetY: 100, speed: 1.2, carrying: true, color: '#00f2fe' },
            { id: 'AMR-02', name: 'Beta', x: 550, y: 140, targetX: 200, targetY: 260, speed: 0.9, carrying: false, color: '#10b981' }
        ];

        this.conveyorOffset = 0;
        this.animate();
    }

    resize() {
        if (!this.canvas) return;
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width;
        this.canvas.height = 380;
    }

    drawConveyor() {
        const ctx = this.ctx;
        // Đường băng chuyền chính
        ctx.fillStyle = '#1e293b';
        ctx.fillRect(40, 60, 40, 240);
        ctx.strokeStyle = '#475569';
        ctx.lineWidth = 2;
        ctx.strokeRect(40, 60, 40, 240);

        // Hiệu ứng con lăn băng chuyền chuyển động
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2;
        this.conveyorOffset = (this.conveyorOffset + 0.8) % 15;
        for (let y = 65 + this.conveyorOffset; y < 295; y += 15) {
            ctx.beginPath();
            ctx.moveTo(42, y);
            ctx.lineTo(78, y);
            ctx.stroke();
        }

        // Nhãn Cảng nhập
        ctx.fillStyle = '#94a3b8';
        ctx.font = '11px Inter, sans-serif';
        ctx.fillText('INBOUND', 33, 45);

        // Các nhánh rẽ phân loại sang 3 Cổng IoT
        this.gates.forEach(g => {
            ctx.fillStyle = '#334155';
            ctx.fillRect(80, g.y - 10, 80, 20);
            
            // Cổng phân loại IoT
            ctx.fillStyle = g.active ? 'rgba(0, 242, 254, 0.25)' : 'rgba(100, 116, 139, 0.2)';
            ctx.fillRect(160, g.y - 18, 45, 36);
            ctx.strokeStyle = g.active ? '#00f2fe' : '#64748b';
            ctx.strokeRect(160, g.y - 18, 45, 36);

            // Đèn LED tín hiệu
            ctx.fillStyle = g.active ? '#10b981' : '#ef4444';
            ctx.beginPath();
            ctx.arc(167, g.y, 4, 0, Math.PI * 2);
            ctx.fill();

            // Nhãn cổng
            ctx.fillStyle = '#e2e8f0';
            ctx.font = '10px Inter, sans-serif';
            ctx.fillText(g.id, 175, g.y + 4);
        });
    }

    drawZones() {
        const ctx = this.ctx;
        this.zones.forEach(z => {
            // Khung Zone
            ctx.fillStyle = z.color;
            ctx.fillRect(z.x, z.y, z.w, z.h);
            ctx.strokeStyle = z.border;
            ctx.lineWidth = 1.5;
            ctx.setLineDash([4, 4]);
            ctx.strokeRect(z.x, z.y, z.w, z.h);
            ctx.setLineDash([]);

            // Nhãn Zone
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 11px Inter, sans-serif';
            ctx.fillText(z.name, z.x + 10, z.y + 20);

            // Vẽ các ô kệ bên trong
            const cols = z.id === 'Zone A' ? 5 : (z.id === 'Zone B' ? 4 : 3);
            const rows = 2;
            const slotW = (z.w - 30) / cols;
            const slotH = 26;

            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    const sx = z.x + 15 + c * (slotW + 3);
                    const sy = z.y + 35 + r * (slotH + 12);
                    const isOccupied = (c + r) % 2 === 1;

                    ctx.fillStyle = isOccupied ? 'rgba(16, 185, 129, 0.35)' : 'rgba(255, 255, 255, 0.05)';
                    ctx.fillRect(sx, sy, slotW, slotH);
                    ctx.strokeStyle = isOccupied ? '#10b981' : 'rgba(255, 255, 255, 0.15)';
                    ctx.lineWidth = 1;
                    ctx.strokeRect(sx, sy, slotW, slotH);

                    if (isOccupied) {
                        ctx.fillStyle = '#f8fafc';
                        ctx.font = '8px Inter, sans-serif';
                        ctx.fillText('PKG', sx + 4, sy + 16);
                    }
                }
            }
        });

        // Khu Vực Cửa Xuất Hàng (Dispatch Gate)
        ctx.fillStyle = 'rgba(239, 68, 68, 0.12)';
        ctx.fillRect(450, 290, 220, 60);
        ctx.strokeStyle = '#ef4444';
        ctx.setLineDash([4, 4]);
        ctx.strokeRect(450, 290, 220, 60);
        ctx.setLineDash([]);
        ctx.fillStyle = '#fca5a5';
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.fillText('OUTBOUND DISPATCH AREA (CỬA XUẤT HÀNG)', 460, 315);
    }

    drawRobots() {
        const ctx = this.ctx;
        this.robots.forEach(r => {
            // Tính toán di chuyển về mục tiêu
            const dx = r.targetX - r.x;
            const dy = r.targetY - r.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist > 3) {
                r.x += (dx / dist) * r.speed;
                r.y += (dy / dist) * r.speed;
            } else {
                // Đổi mục tiêu tuần hoàn
                if (r.id === 'AMR-01') {
                    r.targetX = r.targetX === 380 ? 200 : 380;
                    r.targetY = r.targetY === 100 ? 280 : 100;
                    r.carrying = !r.carrying;
                } else {
                    r.targetX = r.targetX === 200 ? 600 : 200;
                    r.targetY = r.targetY === 260 ? 120 : 260;
                }
            }

            // Vẽ vòng hào quang xung quanh Robot
            ctx.fillStyle = 'rgba(0, 242, 254, 0.15)';
            ctx.beginPath();
            ctx.arc(r.x, r.y, 18, 0, Math.PI * 2);
            ctx.fill();

            // Thân xe Robot AMR
            ctx.fillStyle = '#0f172a';
            ctx.beginPath();
            ctx.arc(r.x, r.y, 13, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = r.color;
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // Nếu đang mang kiện hàng
            if (r.carrying) {
                ctx.fillStyle = '#f59e0b';
                ctx.fillRect(r.x - 5, r.y - 5, 10, 10);
            }

            // Nhãn tên Robot
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 9px Inter, sans-serif';
            ctx.fillText(r.name, r.x - 12, r.y - 18);
        });
    }

    animate() {
        if (!this.ctx) return;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Lưới tọa độ ngầm (Grid lines)
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.03)';
        this.ctx.lineWidth = 1;
        for (let x = 0; x < this.canvas.width; x += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y < this.canvas.height; y += 40) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }

        this.drawZones();
        this.drawConveyor();
        this.drawRobots();

        requestAnimationFrame(() => this.animate());
    }
}
