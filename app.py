from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3
import datetime

app = Flask(__name__)
CORS(app)  # 允许你的前端页面调用

# ---------- 初始化数据库 ----------
def init_db():
    conn = sqlite3.connect('lab.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            date TEXT,
            message TEXT,
            status TEXT DEFAULT '待处理',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- 1. 提交预约（前端调用的接口） ----------
@app.route('/api/booking', methods=['POST'])
def submit_booking():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    date = data.get('date')
    message = data.get('message')

    if not name:
        return jsonify({'error': '姓名不能为空'}), 400

    conn = sqlite3.connect('lab.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO bookings (name, phone, date, message) VALUES (?, ?, ?, ?)',
        (name, phone, date, message)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': '预约成功！'}), 200

# ---------- 2. 获取所有预约（后台管理用） ----------
@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    conn = sqlite3.connect('lab.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bookings ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    
    # 把数据转成字典列表
    bookings = []
    for row in rows:
        bookings.append({
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'date': row[3],
            'message': row[4],
            'status': row[5],
            'created_at': row[6]
        })
    return jsonify(bookings)

# ---------- 3. 后台管理页面（直接浏览器打开看效果） ----------
@app.route('/admin')
def admin_panel():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>预约管理后台</title>
        <style>
            body { font-family: sans-serif; padding: 20px; background: #f4f7fa; }
            h1 { color: #0a3d62; }
            table { width: 100%; border-collapse: collapse; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            th { background: #0a3d62; color: white; padding: 12px; text-align: left; }
            td { padding: 10px; border-bottom: 1px solid #ddd; }
            .status { display: inline-block; padding: 2px 12px; border-radius: 12px; font-size: 0.8rem; }
            .pending { background: #f0a04b; color: #fff; }
            .done { background: #2ecc71; color: #fff; }
            button { background: #0a3d62; color: white; border: none; padding: 6px 16px; border-radius: 4px; cursor: pointer; }
            button:hover { background: #1a5a7a; }
            .refresh { margin-bottom: 16px; }
        </style>
    </head>
    <body>
        <h1>📋 实验室预约管理</h1>
        <button class="refresh" onclick="loadData()">🔄 刷新列表</button>
        <div id="table-wrap"></div>

        <script>
            async function loadData() {
                const res = await fetch('/api/bookings');
                const data = await res.json();
                if (!data.length) {
                    document.getElementById('table-wrap').innerHTML = '<p>暂无预约记录</p>';
                    return;
                }
                let html = '<table><tr><th>ID</th><th>姓名</th><th>电话</th><th>预约日期</th><th>备注</th><th>状态</th></tr>';
                data.forEach(b => {
                    const statusClass = b.status === '已处理' ? 'done' : 'pending';
                    html += `<tr>
                        <td>${b.id}</td>
                        <td>${b.name}</td>
                        <td>${b.phone || '-'}</td>
                        <td>${b.date || '-'}</td>
                        <td>${b.message || '-'}</td>
                        <td><span class="status ${statusClass}">${b.status}</span></td>
                    </tr>`;
                });
                html += '</table>';
                document.getElementById('table-wrap').innerHTML = html;
            }
            loadData();
        </script>
    </body>
    </html>
    '''
    return render_template_string(html)

# ---------- 启动 ----------
if __name__ == '__main__':
    app.run(debug=True, port=5000)