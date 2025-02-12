from flask import Flask, jsonify, request
from flask_cors import CORS
from tinydb import TinyDB, Query
import json
from datetime import datetime
import os
import shortuuid
from utils.parser_factory import ParserFactory
from utils.keyword_parser import parse_keywords

app = Flask(__name__)
CORS(app)

# 初始化 TinyDB
db = TinyDB('db.json')
tasks_table = db.table('tasks')

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = tasks_table.all()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    # 使用uuid作为任务ID
    # shortuuid会将uuid转码为22位字符串，如：ZG6R53mFCkvNtzhRboWxwx
    task_id = str(shortuuid.uuid())
    data['id'] = task_id
    tasks_table.insert(data)
    return jsonify({'id': task_id}), 201

@app.route('/api/tasks/<string:task_id>', methods=['GET'])
def get_task(task_id):
    Task = Query()
    task = tasks_table.get(Task.id == task_id)
    if task is None:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task)

@app.route('/api/tasks/<string:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    Task = Query()
    tasks_table.update(data, Task.id == task_id)
    return jsonify({'success': True})

@app.route('/api/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    Task = Query()
    tasks_table.remove(Task.id == task_id)
    return jsonify({'success': True})

@app.route('/api/tasks/<string:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    isActive = data.get('isActive', False)
    Task = Query()
    tasks_table.update({'isActive': isActive}, Task.id == task_id)
    return jsonify({'success': True})

# 在用户输入完整网址或更新数据格式后，解析表格，后面可以用全局变量存储table, comment，避免重复解析
@app.route('/api/tasks/<string:task_id>/parse', methods=['POST'])
def parse_task(task_id):
    try:
        Task = Query()
        task = tasks_table.get(Task.id == task_id)
        if not task:
            return jsonify({'success': False, 'error': '任务不存在'}), 404

        parser = ParserFactory.get_parser(task['dataFormat'])
        table, comment = parser.parse(
            task['url'],
            bool(task['ignoreComment']),
            int(task.get('tableType', 0))
        )
        return jsonify({
            'success': True,
            'table': table,
            'comment': comment
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<string:task_id>/run', methods=['POST'])
def run_task(task_id):
    try:
        Task = Query()
        task = tasks_table.get(Task.id == task_id)
        if not task:
            return jsonify({'success': False, 'error': '任务不存在'}), 404

        os.makedirs('data', exist_ok=True)

        # todo: 用全局变量存储table, comment，避免重复解析
        parser = ParserFactory.get_parser(task['dataFormat'])
        table, comment = parser.parse(
            task['url'],
            bool(task['ignoreComment']),
            int(task.get('tableType', 0))
        )

        result = []
        parse_rules = task['parseValues']
        fixed_rules = task['fixedValues']
        print(f'=======================')
        print(f'正在运行任务: {task_id}')
        print(f'table前5行:')
        for row in table[:5]:
            print(row)
        print(f'comment: {comment}')
        print(f'parse_rules: {parse_rules}')
        print(f'fixed_rules: {fixed_rules}')
        print(f'=======================')

        memo = {}
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        startRow = task.get('startRow', 0)
        for row in table[startRow:]:
            temp = {}
            for rule in parse_rules:
                value = None
                if rule['parseType'] == 'column':
                    value = row[rule['index']]
                elif rule['parseType'] == 'comment':
                    # todo: 注释正则匹配
                    if rule['keyword'] not in memo:
                        memo[rule['keyword']] = parse_keywords(comment, rule['keyword'])
                    value = memo[rule['keyword']]
                elif rule['parseType'] == 'other':
                    if rule['keyword'] == 'currentTime':
                        value = current_time
                else:
                    continue
                temp[rule['key']] = value
            for rule in fixed_rules:
                temp[rule['source']] = rule['target']
            result.append(temp)

        output_dir = os.path.join('data', str(task_id))
        os.makedirs(output_dir, exist_ok=True)
        formatted_time = current_time.replace(' ', '_').replace(':', '.')
        filename = f'{formatted_time}.json'
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 更新 lastRunTime 字段
        tasks_table.update({'lastRunTime': current_time}, Task.id == task_id)

        return jsonify({
            'success': True,
            'task': {
                'id': task['id'],
                'lastRunTime': current_time,
                'resultFile': filename
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)