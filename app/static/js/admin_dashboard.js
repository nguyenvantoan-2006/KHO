/**
 * SPX Smart Logistics - Admin Dashboard Core Script
 */

document.addEventListener('DOMContentLoaded', () => {
    // Khởi tạo Canvas Map
    const warehouseMap = new WarehouseMap('warehouseCanvas');

    // Biến lưu trữ charts
    let timelineChart = null;
    let zonesChart = null;

    // 1. Quản lý Tab Navigation
    const navItems = document.querySelectorAll('.nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const targetTab = item.getAttribute('data-tab');
            if (!targetTab) return;

            navItems.forEach(i => i.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            item.classList.add('active');
            const targetPane = document.getElementById(targetTab);
            if (targetPane) targetPane.classList.add('active');

            // Cập nhật tiêu đề trang
            const titleEl = document.getElementById('currentTabTitle');
            if (titleEl) titleEl.innerText = item.innerText.trim();

            // Kích hoạt nạp dữ liệu cho tab tương ứng
            if (targetTab === 'tab-packages') loadPackages();
            if (targetTab === 'tab-robots') loadRobots();
            if (targetTab === 'tab-users') loadUsers();
            if (targetTab === 'tab-audit') loadAuditLogs();
        });
    });

    // 2. Nạp dữ liệu KPI Stats
    async function loadStats() {
        try {
            const res = await fetch('/api/dashboard/stats');
            const data = await res.json();

            document.getElementById('kpiTotalPackages').innerText = data.total_packages;
            document.getElementById('kpiReceivedToday').innerText = data.received_today;
            document.getElementById('kpiDispatchedToday').innerText = data.dispatched_today;
            document.getElementById('kpiOccupancyRate').innerText = `${data.occupancy_rate}%`;
            document.getElementById('kpiActiveRobots').innerText = `${data.active_robots}/${data.total_robots}`;
            document.getElementById('kpiAIStatus').innerText = data.ai_status;
        } catch (e) {
            console.error('Lỗi khi nạp KPI Stats:', e);
        }
    }

    // 3. Khởi tạo Biểu đồ Chart.js
    async function loadCharts() {
        try {
            const res = await fetch('/api/dashboard/charts');
            const data = await res.json();

            // Timeline Chart (Lưu lượng nhập / xuất)
            const ctxTimeline = document.getElementById('timelineChart')?.getContext('2d');
            if (ctxTimeline) {
                if (timelineChart) timelineChart.destroy();
                timelineChart = new Chart(ctxTimeline, {
                    type: 'line',
                    data: {
                        labels: data.timeline.labels,
                        datasets: [
                            {
                                label: 'Kiện hàng Nhập (Inbound)',
                                data: data.timeline.inbound,
                                borderColor: '#00f2fe',
                                backgroundColor: 'rgba(0, 242, 254, 0.1)',
                                tension: 0.4,
                                fill: true,
                                pointBackgroundColor: '#00f2fe',
                                pointRadius: 4
                            },
                            {
                                label: 'Kiện hàng Xuất (Outbound)',
                                data: data.timeline.outbound,
                                borderColor: '#a855f7',
                                backgroundColor: 'rgba(168, 85, 247, 0.1)',
                                tension: 0.4,
                                fill: true,
                                pointBackgroundColor: '#a855f7',
                                pointRadius: 4
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { labels: { color: '#94a3b8', font: { family: 'Inter' } } }
                        },
                        scales: {
                            x: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } },
                            y: { grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#64748b' } }
                        }
                    }
                });
            }

            // Zones Chart (Phân bổ theo Zone)
            const ctxZones = document.getElementById('zonesChart')?.getContext('2d');
            if (ctxZones) {
                if (zonesChart) zonesChart.destroy();
                zonesChart = new Chart(ctxZones, {
                    type: 'doughnut',
                    data: {
                        labels: data.zones.labels,
                        datasets: [{
                            data: data.zones.data,
                            backgroundColor: ['#3b82f6', '#f59e0b', '#a855f7'],
                            borderColor: '#111827',
                            borderWidth: 3
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { position: 'bottom', labels: { color: '#94a3b8', font: { family: 'Inter', size: 11 } } }
                        },
                        cutout: '70%'
                    }
                });
            }
        } catch (e) {
            console.error('Lỗi khi nạp biểu đồ:', e);
        }
    }

    // 4. Nạp Cảnh báo AI
    async function loadAIAlerts() {
        try {
            const res = await fetch('/api/dashboard/ai-alerts');
            const alerts = await res.json();
            const container = document.getElementById('aiAlertsList');
            if (!container) return;

            container.innerHTML = alerts.map(a => `
                <div class="alert-item ${a.level}">
                    <div class="alert-header">
                        <span class="alert-title"><i class="fas fa-microchip"></i> ${a.title}</span>
                        <span class="alert-time">${a.time}</span>
                    </div>
                    <div class="alert-msg">${a.message}</div>
                    <div class="alert-action"><i class="fas fa-magic"></i> ${a.action}</div>
                </div>
            `).join('');
        } catch (e) {
            console.error('Lỗi khi nạp cảnh báo AI:', e);
        }
    }

    // 5. Nạp Danh Sách Kiện Hàng
    let currentStatusFilter = 'All';
    async function loadPackages(search = '') {
        const tbody = document.getElementById('packagesTableBody');
        if (!tbody) return;
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px;">Đang tải dữ liệu...</td></tr>`;

        try {
            let url = `/api/packages?status=${currentStatusFilter}`;
            if (search) url += `&search=${encodeURIComponent(search)}`;
            const res = await fetch(url);
            const data = await res.json();

            if (data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:20px; color:#64748b;">Không tìm thấy kiện hàng nào</td></tr>`;
                return;
            }

            tbody.innerHTML = data.map(p => `
                <tr>
                    <td><strong>${p.package_id}</strong></td>
                    <td><code>${p.tracking_number}</code></td>
                    <td>${p.weight_kg} kg</td>
                    <td><span class="badge ${p.status}"><i class="fas fa-circle" style="font-size:6px;"></i> ${p.status}</span></td>
                    <td><span style="color:#38bdf8;">${p.category}</span></td>
                    <td>${p.location_id}</td>
                    <td>${p.gate_id}</td>
                    <td>
                        <button class="btn-action btn-sm" onclick="viewTimeline('${p.package_id}')">
                            <i class="fas fa-history"></i> Truy vết
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Lỗi khi nạp danh sách kiện hàng:', e);
        }
    }

    // Bộ lọc Status Pills cho Kiện hàng
    document.querySelectorAll('.pill-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pill-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentStatusFilter = btn.getAttribute('data-status');
            const searchVal = document.getElementById('packageSearchInput')?.value || '';
            loadPackages(searchVal);
        });
    });

    // Tìm kiếm tức thì
    const searchInput = document.getElementById('packageSearchInput');
    if (searchInput) {
        let debounceTimeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(() => {
                loadPackages(e.target.value);
            }, 300);
        });
    }

    // 6. Modal Chi tiết Truy Vết Kiện Hàng (Timeline)
    window.viewTimeline = async function(packageId) {
        const modal = document.getElementById('timelineModal');
        const content = document.getElementById('timelineContent');
        const title = document.getElementById('timelinePackageTitle');
        if (!modal || !content) return;

        title.innerText = `Lộ trình di chuyển - ${packageId}`;
        content.innerHTML = `<p style="padding:20px; text-align:center;">Đang tải hành trình...</p>`;
        modal.style.display = 'flex';

        try {
            const res = await fetch(`/api/packages/${packageId}`);
            const data = await res.json();

            content.innerHTML = `
                <div style="display:flex; justify-content:space-between; margin-bottom:15px; font-size:12px; color:#94a3b8;">
                    <span>Mã vận đơn: <strong>${data.tracking_number}</strong></span>
                    <span>Trọng lượng: <strong>${data.weight_kg} kg</strong></span>
                    <span>Trạng thái: <strong>${data.status}</strong></span>
                </div>
                <div class="timeline">
                    ${data.timeline.map(t => `
                        <div class="timeline-item">
                            <div class="timeline-dot"></div>
                            <div class="timeline-content">
                                <h4>${t.action_type} - ${t.performed_by}</h4>
                                <p>Từ <em>${t.from_location}</em> ➔ Đến <em>${t.to_location}</em></p>
                                <span style="display:block; font-size:11px; color:#00f2fe; margin-top:2px;">${t.notes || ''}</span>
                                <span><i class="far fa-clock"></i> ${t.timestamp}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        } catch (e) {
            content.innerHTML = `<p style="color:#ef4444;">Lỗi khi nạp dữ liệu lộ trình!</p>`;
        }
    };

    window.closeModal = function() {
        const modal = document.getElementById('timelineModal');
        if (modal) modal.style.display = 'none';
    };

    // 7. Nạp danh sách Robot
    async function loadRobots() {
        const tbody = document.getElementById('robotsTableBody');
        if (!tbody) return;
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;">Đang tải...</td></tr>`;

        try {
            const res = await fetch('/api/robots');
            const data = await res.json();
            tbody.innerHTML = data.map(r => `
                <tr>
                    <td><strong>${r.robot_id}</strong></td>
                    <td>${r.robot_name}</td>
                    <td>
                        <div style="display:flex; align-items:center; gap:8px;">
                            <div style="flex:1; background:rgba(255,255,255,0.1); height:6px; border-radius:3px; overflow:hidden;">
                                <div style="width:${r.battery_level}%; background:${r.battery_level > 50 ? '#10b981' : '#f59e0b'}; height:100%;"></div>
                            </div>
                            <span style="font-size:11px;">${r.battery_level}%</span>
                        </div>
                    </td>
                    <td>X: ${r.current_x}, Y: ${r.current_y}</td>
                    <td><span class="badge ${r.status}">${r.status}</span></td>
                    <td>${r.current_task ? `${r.current_task.task_id} (Đến: ${r.current_task.target})` : 'Không có'}</td>
                    <td>
                        <button class="btn-action btn-sm" onclick="sendRobotCommand('${r.robot_id}', 'charge')">
                            <i class="fas fa-charging-station"></i> Sạc
                        </button>
                    </td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Lỗi khi nạp danh sách robot:', e);
        }
    }

    window.sendRobotCommand = async function(robotId, action) {
        try {
            const res = await fetch(`/api/robots/${robotId}/command?action=${action}`, { method: 'POST' });
            const data = await res.json();
            alert(data.message);
            loadRobots();
        } catch (e) {
            alert('Lỗi gửi lệnh robot');
        }
    };

    // 8. Nạp danh sách Users
    async function loadUsers() {
        const tbody = document.getElementById('usersTableBody');
        if (!tbody) return;
        try {
            const res = await fetch('/api/users');
            const data = await res.json();
            tbody.innerHTML = data.map(u => `
                <tr>
                    <td><strong>${u.user_id}</strong></td>
                    <td>${u.username}</td>
                    <td>${u.full_name}</td>
                    <td><span class="badge" style="background:rgba(0,242,254,0.15); color:#00f2fe;">${u.role}</span></td>
                    <td><span class="badge" style="background:rgba(16,185,129,0.15); color:#10b981;">Đang hoạt động</span></td>
                    <td>${u.created_at}</td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Lỗi tải danh sách người dùng:', e);
        }
    }

    // 9. Nạp Audit Logs
    async function loadAuditLogs() {
        const tbody = document.getElementById('auditTableBody');
        if (!tbody) return;
        try {
            const res = await fetch('/api/audit');
            const data = await res.json();
            tbody.innerHTML = data.map(a => `
                <tr>
                    <td>#${a.log_id}</td>
                    <td>${a.user_name}</td>
                    <td><code>${a.http_method} ${a.endpoint}</code></td>
                    <td>${a.ip_address}</td>
                    <td>${a.action_desc}</td>
                    <td><span class="badge" style="background:rgba(16,185,129,0.15); color:#10b981;">${a.status_code} OK</span></td>
                    <td>${a.created_at}</td>
                </tr>
            `).join('');
        } catch (e) {
            console.error('Lỗi tải audit logs:', e);
        }
    }

    // Chạy nạp dữ liệu ban đầu
    loadStats();
    loadCharts();
    loadAIAlerts();
    loadPackages();

    // Polling tự động làm mới số liệu mỗi 6 giây
    setInterval(() => {
        loadStats();
    }, 6000);
});
