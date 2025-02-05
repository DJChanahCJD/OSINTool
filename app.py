from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
from utils.parser_factory import ParserFactory
from utils.keyword_parser import parse_keywords

# todo: 实现定时任务（开机自启+taskschedule？）
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
            interval INTEGER,
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
        'interval': task['interval'],
        'dataFormat': task['data_format'],
        'ignoreComment': bool(task['ignore_comment']),
        'parseValues': json.loads(task['parse_values'] or '[]'),
        'fixedValues': json.loads(task['fixed_values'] or '[]'),
        'isActive': bool(task['is_active']),
        'createTime': task['create_time'],
        'lastRunTime': task['last_run_time']
    } for task in tasks])

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
            schedule, interval, data_format, ignore_comment, parse_values,
            fixed_values, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        current_timestamp,  # 使用时间戳作为ID
        data['title'],
        data['url'],
        data['scheduleType'],
        data.get('days'),
        data.get('execTime'),
        data.get('schedule'),
        data.get('interval'),
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
        'interval': task['interval'],
        'dataFormat': task['data_format'],
        'ignoreComment': bool(task['ignore_comment']),
        'parseValues': json.loads(task['parse_values'] or '[]'),
        'fixedValues': json.loads(task['fixed_values'] or '[]'),
        'isActive': bool(task['is_active']),
        'createTime': task['create_time'],
        'lastRunTime': task['last_run_time']
    })

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE tasks SET
            title = ?, url = ?, schedule_type = ?, days = ?,
            exec_time = ?, schedule = ?, data_format = ?, interval = ?,
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
        data.get('interval'),
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
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 获取任务信息
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()

        if not task:
            return jsonify({'success': False, 'error': '任务不存在'}), 404

        # 创建结果目录
        results_dir = os.path.join('data', 'results')
        os.makedirs(results_dir, exist_ok=True)

        # 解析内容
        parser = ParserFactory.get_parser(task['data_format'])
        table, comment = parser.parse(
            task['url'],
            bool(task['ignore_comment'])
        )

        result = []
        parse_rules = json.loads(task['parse_values'])
        fixed_rules = json.loads(task['fixed_values'])
        print(f'=======================')
        print(f'comment: {comment}')
        print(f'parse_rules: {parse_rules}')
        print(f'fixed_rules: {fixed_rules}')
        print(f'=======================')

        memo = {}
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for row in table:
            temp = {}
            for rule in parse_rules:
                value = None
                if rule['parseType'] == 'column':
                    value = row[rule['index']]
                elif rule['parseType'] == 'comment':
                    # todo完善: 解析注释中的关键词
                    if rule['keyword'] not in memo:
                        memo[rule['keyword']] = parse_keywords(comment, rule['keyword'])
                    value = memo[rule['keyword']]
                    # print(f'keyword: {value}')
                elif rule['parseType'] == 'other':
                    if rule['keyword'] == 'currentTime':
                        value = current_time
                    # print(f'other: {value}')
                else:
                    continue
                temp[rule['key']] = value
            for rule in fixed_rules:
                temp[rule['source']] = rule['target']
            result.append(temp)

        # 保存结果
        output_dir = os.path.join('data', 'results', str(task_id))
        os.makedirs(output_dir, exist_ok=True)
        formatted_time = current_time.replace(' ', '_').replace(':', '.')
        filename = f'{formatted_time}.json'
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'task': {
                'id': task['id'],
                'lastRunTime': task['last_run_time'],
                'resultFile': filename
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
