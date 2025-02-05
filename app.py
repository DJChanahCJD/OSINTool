from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)  # 启用跨域支持

# 确保data目录存在
if not os.path.exists('data'):
    os.makedirs('data')

# 数据库初始化
def init_db():
    conn = sqlite3.connect('data/tasks.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,  -- SQLite 会自动使用 ROWID
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            schedule_type TEXT NOT NULL,
            days INTEGER,
            exec_time TEXT,
            schedule TEXT,
            data_format TEXT NOT NULL,
            ignore_comment INTEGER DEFAULT 0,
            parse_values TEXT,
            fixed_values TEXT,
            is_active INTEGER DEFAULT 0,
            create_time TEXT DEFAULT CURRENT_TIMESTAMP,
            last_run_time TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 获取数据库连接
def get_db():
    conn = sqlite3.connect('data/tasks.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks ORDER BY create_time DESC')
    tasks = cursor.fetchall()
    conn.close()

    return jsonify([{
        'id': task['id'],
        'title': task['title'],
        'url': task['url'],
        'scheduleType': task['schedule_type'],
        'days': task['days'],
        'execTime': task['exec_time'],
        'schedule': task['schedule'],
        'dataFormat': task['data_format'],
        'ignoreComment': bool(task['ignore_comment']),
        'parseValues': json.loads(task['parse_values'] or '[]'),
        'fixedValues': json.loads(task['fixed_values'] or '[]'),
        'isActive': bool(task['is_active']),
        'createTime': task['create_time'],
        'lastRunTime': task['last_run_time']
    } for task in tasks])

@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    conn.close()

    if task is None:
        return jsonify({'error': 'Task not found'}), 404

    return jsonify({
        'id': task['id'],
        'title': task['title'],
        'url': task['url'],
        'scheduleType': task['schedule_type'],
        'days': task['days'],
        'execTime': task['exec_time'],
        'schedule': task['schedule'],
        'dataFormat': task['data_format'],
        'ignoreComment': bool(task['ignore_comment']),
        'parseValues': json.loads(task['parse_values'] or '[]'),
        'fixedValues': json.loads(task['fixed_values'] or '[]'),
        'isActive': bool(task['is_active']),
        'createTime': task['create_time'],
        'lastRunTime': task['last_run_time']
    })

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    # 使用时间戳作为ID
    current_timestamp = int(datetime.now().timestamp() * 1000)  # 毫秒级时间戳

    cursor.execute('''
        INSERT INTO tasks (
            id, title, url, schedule_type, days, exec_time,
            schedule, data_format, ignore_comment, parse_values,
            fixed_values, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_timestamp,  # 使用时间戳作为ID
        data['title'],
        data['url'],
        data['scheduleType'],
        data.get('days'),
        data.get('execTime'),
        data.get('schedule'),
        data['dataFormat'],
        int(data.get('ignoreComment', False)),
        json.dumps(data.get('parseValues', [])),
        json.dumps(data.get('fixedValues', [])),
        int(data.get('isActive', False))
    ))

    task_id = current_timestamp  # 使用生成的时间戳
    conn.commit()
    conn.close()

    return jsonify({'id': task_id}), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE tasks SET
            title = ?, url = ?, schedule_type = ?, days = ?,
            exec_time = ?, schedule = ?, data_format = ?,
            ignore_comment = ?, parse_values = ?, fixed_values = ?,
            is_active = ?
        WHERE id = ?
    ''', (
        data['title'],
        data['url'],
        data['scheduleType'],
        data.get('days'),
        data.get('execTime'),
        data.get('schedule'),
        data['dataFormat'],
        int(data.get('ignoreComment', False)),
        json.dumps(data.get('parseValues', [])),
        json.dumps(data.get('fixedValues', [])),
        int(data.get('isActive', False)),
        task_id
    ))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    is_active = data.get('isActive', False)

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET is_active = ? WHERE id = ?',
        (int(is_active), task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/api/tasks/<int:task_id>/run', methods=['POST'])
def run_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tasks SET last_run_time = CURRENT_TIMESTAMP WHERE id = ?',
        (task_id,)
    )
    conn.commit()
    conn.close()

    # TODO: 实际的任务执行逻辑
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
