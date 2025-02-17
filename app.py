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


@app.route('/api/tasks/paginated', methods=['GET'])
def get_tasks_paginated():
    # 获取分页、搜索、排序和筛选参数

    print ("get_tasks_paginated")
    # 解析参数
    print(request.args)

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('perPage', 10))
    search = request.args.get('searchQuery', '').lower()
    print ("get_tasks_paginated 1")

    sort = json.loads(request.args.get('sort', '[]'))   # 是一个对象sort= [{ sortField: 'title', sortOrder: 'asc' }]
    print ("get_tasks_paginated 1111")

    filters = json.loads(request.args.get('filters', '{}'))    # 是一个对象filters = { scheduleType: ['fixed'] }
    print ("get_tasks_paginated2")

    # 调试输出
    print(f"Page: {page}, Per Page: {per_page}, Search: {search}, Sort: {sort}, Filters: {filters}")

    # 获取所有任务
    tasks = tasks_table.all()

    # 搜索过滤
    if search:
        tasks = [t for t in tasks if search in t.get('title', '').lower() or search in t.get('url', '').lower()]

    # 筛选过滤, filters = { scheduleType: ['fixed'], ... }
    if filters:
        for field, values in filters.items():
            if values:
                tasks = [t for t in tasks if t.get(field) in values]

    # 排序处理
    if sort:
        for cond in reversed(sort):
            field, order = cond.get("sortField"), cond.get("sortOrder", "asc")
            placeholder = ''
            tasks.sort(key=lambda t: placeholder if t.get(field) is None else t.get(field), reverse=(order == "desc"))


    # 分页处理
    start, end, total = (page - 1) * per_page, (page - 1) * per_page + per_page, len(tasks)
    paginated_tasks = tasks[start:end]

    return jsonify({
        'page': page,
        'perPage': per_page,
        'total': total,
        'data': paginated_tasks
    })




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
    try:
        data = request.json
        Task = Query()
        tasks_table.update(data, Task.id == task_id)
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)   # 先删除原有任务
        if data.get('isActive', False) == True:
            schedule_task(data)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<string:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        Task = Query()
        tasks_table.remove(Task.id == task_id)
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# 批量删除
@app.route('/api/tasks/batch_delete', methods=['DELETE'])
def delete_tasks():
    try:
        data = request.json
        ids = data.get('taskIds', [])
        tasks_table.remove(Query().id.one_of(ids))
        for task_id in ids:
            if scheduler.get_job(task_id):
                scheduler.remove_job(task_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tasks/<string:task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    data = request.json
    isActive = data.get('isActive', False)
    update_task_status_func(task_id, isActive)

    # 打印当前所有运行的任务
    print("当前运行的任务:")
    for job in scheduler.get_jobs():
        print(f"任务ID: {job.id}")
        # 打印任务详情
        print(job)
    return jsonify({'success': True})

def update_task_status_func(task_id, isActive):
    Task = Query()
    tasks_table.update({'isActive': isActive}, Task.id == task_id)
    if isActive:
        task = tasks_table.get(Task.id == task_id)
        schedule_task(task)
    else:
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)

@app.route('/api/tasks/running', methods=['GET'])
def get_running_tasks():
    jobs = scheduler.get_jobs()
    running_tasks = [{'id': job.id, 'next_run_time': job.next_run_time } for job in jobs]
    return jsonify({'success': True, 'running_tasks': running_tasks})

@app.route('/api/tasks/<string:task_id>/parse', methods=['POST'])
def parse_task(task_id):    # 预览
    Task = Query()
    task = tasks_table.get(Task.id == task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

    max_count = min(task['maxCount'], 20)  # 最大返回20条数据
    try:
        table = execute_task_parsing(task, max_count)
        return jsonify({'success': True, 'table': table})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<string:task_id>/run', methods=['POST'])
def run_task(task_id):
    Task = Query()
    task = tasks_table.get(Task.id == task_id)
    if not task:
        return jsonify({'success': False, 'error': '任务不存在'}), 404

    print(f'===========正在运行任务: {task_id}============')

    os.makedirs('data', exist_ok=True)

    max_count = task['maxCount']  # 获取最大数据量
    try:
        result = execute_task_parsing(task, max_count)

        # 保存结果
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_time = current_time.replace(' ', '_').replace(':', '.')
        filename = f'{formatted_time}.json'
        output_dir = os.path.join('data', str(task_id))
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # 更新任务的 lastRunTime
        Task = Query()
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

#批量启动
@app.route('/api/tasks/batch_start', methods=['POST'])
def batch_start_tasks():
    try:
        data = request.json
        task_ids = data.get('taskIds', [])
        for task_id in task_ids:
            update_task_status_func(task_id, True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

#批量停止
@app.route('/api/tasks/batch_stop', methods=['POST'])
def batch_stop_tasks():
    try:
        data = request.json
        task_ids = data.get('taskIds', [])
        for task_id in task_ids:
            update_task_status_func(task_id, False)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def execute_task_parsing(task, max_count):
    # 根据任务设置提取解析规则
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    parse_rules = task['parseValues']
    other_rules = task['otherValues']
    columns = {rule['key']: rule['index'] for rule in parse_rules}
    patterns = {rule['key']: rule['pattern'] for rule in parse_rules}

    # 根据数据格式选择解析器
    if task['dataFormat'] == 'html':
        xpaths = task['xpaths']
        parser = HTMLParser(task['url'], xpaths['table'], xpaths['row'], xpaths['next_page'], patterns, max_count)
        table = parser.parse()
    else:
        parser = ParserFactory.get_parser(task['dataFormat'])
        table = parser.parse(task['url'], task['parseType'], columns, patterns, task['table_pattern'], max_count)

    # 添加其他值
    result = addOtherValues(table, other_rules, parser.get_content(), current_time)
    return result

def run_scheduled_task(task_id):
    with app.app_context():
        run_task(task_id)


def schedule_task(task):
    task_id = task['id']
    schedule_type = task['scheduleType']
    job = None
    if schedule_type == 'fixed':
        days = task['days']
        exec_time = task['execTime']
        hour, minute = map(int, exec_time.split(':'))
        job = scheduler.add_job(run_scheduled_task, 'cron', day=f'*/{days}', hour=hour, minute=minute, id=task_id, kwargs={'task_id': task_id})
    elif schedule_type == 'interval':
        interval = task['interval']
        job = scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})
    elif schedule_type == 'random':
        interval = random.randint(1, 4096)  # 1 - 4096 分钟之间的随机值
        job = scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})

    # 更新任务的 next_run_time
    if job:
        next_run_time = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
        Task = Query()
        tasks_table.update({'next_run_time': next_run_time}, Task.id == task_id)

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
            elif rule['valueType'] == 'special':
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
