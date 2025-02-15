import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from tinydb import TinyDB, Query
import json
from datetime import datetime
import os
import shortuuid
from utils.parser_factory import ParserFactory
from utils.parsers.html_parser import HTMLParser
from utils.regex_matcher import match_one, match_all
from apscheduler.schedulers.background import BackgroundScheduler

# https://regex101.com/

app = Flask(__name__)
CORS(app)

# 初始化 TinyDB
db = TinyDB('db.json')
tasks_table = db.table('tasks')

# 初始化调度器
scheduler = BackgroundScheduler()

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = tasks_table.all()
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json
    task_id = str(shortuuid.uuid())
    data['id'] = task_id
    tasks_table.insert(data)
    if data.get('isActive', True):
        schedule_task(data)
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
    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)   # 先删除原有任务
    if data.get('isActive', False) == True:
        schedule_task(data)
    return jsonify({'success': True})

@app.route('/api/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    Task = Query()
    tasks_table.remove(Task.id == task_id)
    if scheduler.get_job(task_id):
        scheduler.remove_job(task_id)
    return jsonify({'success': True})

@app.route('/api/tasks/<string:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    isActive = data.get('isActive', False)
    Task = Query()
    tasks_table.update({'isActive': isActive}, Task.id == task_id)
    if isActive:
        task = tasks_table.get(Task.id == task_id)
        schedule_task(task)
    else:
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)

    # 打印当前所有运行的任务
    print("当前运行的任务:")
    for job in scheduler.get_jobs():
        print(f"任务ID: {job.id}")
        # 打印任务详情
        print(job)
    return jsonify({'success': True})

@app.route('/api/tasks/running', methods=['GET'])
def get_running_tasks():
    jobs = scheduler.get_jobs()
    running_tasks = [{'id': job.id, 'next_run_time': job.next_run_time } for job in jobs]
    return jsonify({'success': True, 'running_tasks': running_tasks})


@app.route('/api/tasks/<string:task_id>/parse', methods=['POST'])
def parse_task(task_id):
    Task = Query()
    task = tasks_table.get(Task.id == task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    parser = ParserFactory.get_parser(task['dataFormat'])
    table = parser.parse(
        task['url'],
        int(task.get('tableType', 0))
    )
    return jsonify({'success': True, 'table': table})

@app.route('/api/tasks/<string:task_id>/run', methods=['POST'])
def run_task(task_id):
    try:
        Task = Query()
        task = tasks_table.get(Task.id == task_id)
        if not task:
            return jsonify({'success': False, 'error': '任务不存在'}), 404

        os.makedirs('data', exist_ok=True)

        print(f'===========正在运行任务: {task_id}============')

        result = []
        parse_rules = task['parseValues']
        other_rules = task['otherValues']
        dataFormat = task['dataFormat']
        print(f'parse_rules: {parse_rules}')
        print(f'other_rules: {other_rules}')

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        columns = {rule['key']: rule['index'] for rule in parse_rules}
        patterns = {rule['key']: rule['pattern'] for rule in parse_rules}
        if (dataFormat == 'html'):
            xpaths = task['xpaths']
            parser = HTMLParser(task['url'], xpaths['table'], xpaths['row'], xpaths['next_page'], patterns)
            content = parser.get_content()    # 其他值的正则解析用
            res = parser.parse()
            # 添加其他值
            result = addOtherValues(res, other_rules, content, current_time)
        else:
            parser = ParserFactory.get_parser(dataFormat)

            res = parser.parse(
                task['url'],
                task['parseType'],
                columns,
                patterns,
            )

            # 添加其他值
            result = addOtherValues(res, other_rules, content, current_time)

        print(f'========命名文件======')
        output_dir = os.path.join('data', str(task_id))

        os.makedirs(output_dir, exist_ok=True)
        formatted_time = current_time.replace(' ', '_').replace(':', '.')

        filename = f'{formatted_time}.json'
        filepath = os.path.join(output_dir, filename)

        print(f'========保存文件======')
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as file_error:
            return jsonify({'success': False, 'error': f'保存文件时出错: {str(file_error)}'}), 500

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


def run_scheduled_task(task_id):
    with app.app_context():
        run_task(task_id)

def schedule_task(task):
    task_id = task['id']
    schedule_type = task['scheduleType']
    if schedule_type == 'fixed':
        days = task['days']
        exec_time = task['execTime']
        hour, minute = map(int, exec_time.split(':'))
        scheduler.add_job(run_scheduled_task, 'cron', day=f'*/{days}', hour=hour, minute=minute, id=task_id, kwargs={'task_id': task_id})
    elif schedule_type == 'interval':
        interval = task['interval']
        scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})
    elif schedule_type == 'random':
        interval = random.randint(0, 4096)  # 0 - 4096 分钟之间
        if interval == 0:
            # 使用 date 触发器立即调度任务
            scheduler.add_job(run_scheduled_task, 'date', run_date=datetime.now(), id=task_id, kwargs={'task_id': task_id})
            interval = random.randint(1, 4096)
        scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})

    print(f"已添加定时任务: {task_id}")
    print(f"任务详情: {task}")

def addOtherValues(data, other_rules, html_content, current_time):
    result = []
    memo = {}
    for item in data:
        for rule in other_rules:
            if rule['valueType'] == 'fixed':
                item[rule['source']] = rule['target']
            elif rule['valueType'] == 'regex':  # 只允许解析单个
                if rule['source'] not in memo:
                    memo[rule['source']] = match_one(html_content, rule['target'])
                value = memo[rule['source']]
                item[rule['source']] = value
            elif rule['valueType'] == 'other':
                if rule['target'] == 'attack_time':
                    item[rule['source']] = current_time
        result.append(item)
    return result

def init_scheduler():
    print("初始化调度器")
    scheduler.start()
    tasks = tasks_table.all()
    for task in tasks:
        if task.get('isActive', True):
            schedule_task(task)

if __name__ == '__main__':
    init_scheduler()
    # app.run(debug=True, port=5000) # 调试模式下会重复运行定时任务
    app.run(debug=False, port=5000)
