import random
import time
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from tinydb import TinyDB, Query
import json
from datetime import datetime
import os
import shortuuid
from utils.parser_factory import ParserFactory
from utils.parsers.html_parser import HTMLParser
from utils.regex_matcher import parse_keywords, parse_first_keyword, match_one, match_all
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import aiohttp
import zipfile
import io

app = Flask(__name__)
CORS(app)
# 初始化TinyDB
db = TinyDB('db.json')
tasks_table = db.table('tasks')
results_table = db.table('results')
# 初始化调度器
scheduler = BackgroundScheduler()


@app.route('/api/tasks/stats', methods=['GET'])
def get_task_stats():
    all_tasks = tasks_table.all()
    active_tasks = [task for task in all_tasks if task.get('isActive', False)]
    inactive_tasks = [task for task in all_tasks if not task.get('isActive', False)]
    total_tasks = len(all_tasks)
    total_active_tasks = len(active_tasks)
    total_inactive_tasks = len(inactive_tasks)
    # 假设我们有一个results_table存储任务结果
    success_results = results_table.search(Query().success == True)
    failed_results = results_table.search(Query().success == False)
    total_success = len(success_results)
    total_failed = len(failed_results)
    return jsonify({
        'total_tasks': total_tasks,
        'total_active_tasks': total_active_tasks,
        'total_inactive_tasks': total_inactive_tasks,
        'total_success': total_success,
        'total_failed': total_failed
    })


@app.route('/getTasks', methods=['GET'])
def get_tasks_pages():
    # 获取前端传递的页码和每页数量，默认每页显示5条
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 5))
    # 获取搜索查询参数
    search_query = request.args.get('search_query', '').strip().lower()
    # 从数据库查询所有任务
    all_tasks = tasks_table.all()
    # 如果有搜索查询，进行过滤
    if search_query:
        filtered_tasks = []
        for task in all_tasks:
            title = task.get('title', '').lower()
            url = task.get('url', '').lower()
            if search_query in title or search_query in url:
                filtered_tasks.append(task)
    else:
        filtered_tasks = all_tasks
    # 计算总页数
    total_count = len(filtered_tasks)
    total_pages = (total_count + per_page - 1) // per_page
    # 计算偏移量
    offset = (page - 1) * per_page
    # 对过滤后的数据进行分页
    paginated_tasks = filtered_tasks[offset: offset + per_page]
    return jsonify({
        'tasks': paginated_tasks,
        'total_pages': total_pages,
        'total_count': total_count
    })


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = tasks_table.all()
    return jsonify(tasks)


@app.route('/api/tasks/paginated', methods=['GET'])
def get_tasks_paginated():
    # 获取分页、搜索、排序和筛选参数
    print("get_tasks_paginated")
    # 解析参数
    print(request.args)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('perPage', 10))
    search = request.args.get('searchQuery', '').lower()
    print("get_tasks_paginated 1")
    sort = json.loads(request.args.get('sort', '[]'))  # 是一个对象sort= [{ sortField: 'title', sortOrder: 'asc' }]
    print("get_tasks_paginated 1111")
    filters = json.loads(request.args.get('filters', '{}'))  # 是一个对象filters = { scheduleType: ['fixed'] }
    print("get_tasks_paginated2")
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
            scheduler.remove_job(task_id)  # 先删除原有任务
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
        ids = request.json
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
    # 获取当前任务的状态
    task = tasks_table.get(Task.id == task_id)
    current_is_active = task.get('isActive', False) if task else False
    # 检查当前状态和传入的状态是否一致
    if current_is_active != isActive:
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
    running_tasks = [{'id': job.id, 'next_run_time': job.next_run_time} for job in jobs]
    return jsonify({'success': True, 'running_tasks': running_tasks})


@app.route('/api/tasks/<string:task_id>/parse', methods=['POST'])
def parse_task(task_id):  # 预览
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
    try:
        Task = Query()
        task = tasks_table.get(Task.id == task_id)
        if not task:
            return jsonify({'success': False, 'error': '任务不存在'}), 404
        os.makedirs('data', exist_ok=True)
        print(f'===========正在运行任务: {task_id}============')
        result = []
        parse_rules = task['parseValues']
        fixed_rules = task['fixedValues']
        dataFormat = task['dataFormat']
        print(f'parse_rules: {parse_rules}')
        print(f'fixed_rules: {fixed_rules}')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if (dataFormat == 'html'):
            xpaths = task['xpaths']
            patterns = {rule['key']: rule['keyword'] for rule in parse_rules}
            parser = HTMLParser(task['url'], xpaths['table'], xpaths['row'], xpaths['next_page'], patterns)
            res = parser.parse()
            print(f'res前5行: {res[:5]}')
            # 添加特殊值
            for item in res:
                for rule in fixed_rules:
                    item[rule['source']] = rule['target']
                result.append(item)
            print(f'if结束')
        else:
            parser = ParserFactory.get_parser(dataFormat)
            table = parser.parse(
                task['url'],
                int(task.get('tableType', 0))
            )
            content = parser.content
            print(f'table前5行:')
            for row in table[:5]:
                print(row)
            print(f'=======================')
            memo = {}
            startRow = task.get('startRow', 0)
            for row in table[startRow:]:
                temp = {}
                for rule in parse_rules:
                    value = None
                    if rule['parseType'] == 'column':
                        value = row[rule['index']]
                    elif rule['parseType'] == 'regex':
                        if rule['keyword'] not in memo:
                            memo[rule['keyword']] = parse_first_keyword(content, rule['keyword']) if int(
                                rule['regexMode']) == 0 else parse_keywords(content, rule['keyword'])
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
        # 更新lastRunTime字段
        tasks_table.update({'lastRunTime': current_time}, Task.id == task_id)
        # 保存结果到数据库
        results_table.insert({
            'task_id': task_id,
            'run_time': current_time,
            'result': result
        })
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


def execute_task_parsing(task, max_count):
    parse_rules = task['parseValues']
    other_rules = task['otherValues']
    columns = {rule['key']: rule['index'] for rule in parse_rules}
    patterns = {rule['key']: rule['pattern'] for rule in parse_rules}
    # 根据数据格式选择解析器
    if task['dataFormat'] == 'html':
        xpaths = task['xpaths']
        parser = HTMLParser(task['url'], xpaths['table'], xpaths['row'], xpaths['next_page'], patterns, max_count)
        table = parser.parse(task['cookies'])
    else:
        parser = ParserFactory.get_parser(task['dataFormat'])
        table = parser.parse(task['url'], task['parseType'], columns, patterns, task['table_pattern'], max_count)
    # 添加其他值
    result = addOtherValues(table, other_rules, parser.get_content())
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
        job = scheduler.add_job(run_scheduled_task, 'cron', day=f'*/{days}', hour=hour, minute=minute, id=task_id,
                                kwargs={'task_id': task_id})
    elif schedule_type == 'interval':
        interval = task['interval']
        job = scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})
    elif schedule_type == 'random':
        interval = random.randint(1, 4096)  # 1 - 4096分钟之间的随机值
        job = scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})
    # 更新任务的next_run_time
    if job:
        next_run_time = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
        Task = Query()
        tasks_table.update({'next_run_time': next_run_time}, Task.id == task_id)
    print(f"已添加定时任务: {task_id}")
    print(f"任务详情: {task}")


def addOtherValues(data, other_rules, html_content):
    """
    为数据添加额外的值，根据不同规则（固定值、正则匹配、特殊值）处理
    :param data: 原始数据列表
    :param other_rules: 额外规则列表，包含规则类型和目标值
    :param html_content: HTML 内容，用于正则匹配
    :return: 添加额外值后的数据列表
    """
    specialValues = getSpecialValues()
    result = []
    memo = {}

    for item in data:
        for rule in other_rules:
            source = rule['source']
            value_type = rule['valueType']

            if value_type == 'fixed':
                # 固定值直接赋值
                item[source] = rule['target']
            elif value_type == 'regex':
                # 正则匹配值，使用缓存避免重复匹配
                if source not in memo:
                    memo[source] = match_one(html_content, rule['target'])
                item[source] = memo[source]
            elif value_type == 'xpath':
                # 假设存在一个 xpath 匹配函数，这里简单模拟
                try:
                    # 这里需要实现具体的 xpath 匹配逻辑
                    # 例如使用 lxml 库来解析 html_content 并根据 rule['target'] 进行匹配
                    from lxml import html
                    tree = html.fromstring(html_content)
                    xpath_result = tree.xpath(rule['target'])
                    if xpath_result:
                        item[source] = xpath_result[0].text if hasattr(xpath_result[0], 'text') else xpath_result[0]
                    else:
                        item[source] = None
                except Exception as e:
                    print(f"XPath 匹配出错: {e}")
                    item[source] = None
            elif value_type =='special':
                # 特殊值从预定义的特殊值字典中获取
                value = specialValues.get(rule['target'])
                if value is not None:
                    item[source] = value
                else:
                    print(f"Key {rule['target']} not found in specialValues.")

        result.append(item)

    return result
# 生成特殊值字典
def getSpecialValues():
    current_timestamp = int(time.time())
    current_time_str = datetime.fromtimestamp(current_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    specialValues = {
        'attack_time': current_time_str,
        'attack_timestamp': current_timestamp
    }
    return specialValues


def init_scheduler():
    print("初始化调度器...")
    scheduler.start()
    tasks = tasks_table.all()
    for task in tasks:
        if task.get('isActive', True):
            schedule_task(task)


import requests

# 同步运行单个任务
def sync_run_task(task_id, is_active):
    url = f'http://localhost:5000/api/tasks/{task_id}/status'
    data = {"isActive": is_active}
    try:
        response = requests.put(url, json=data)
        content_type = response.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            return response.json()
        elif content_type.startswith('text/'):
            # 处理文本类型的响应，指定编码为 UTF - 8
            return response.text
        else:
            print(f"Unexpected response content type for task {task_id}: {content_type}")
            print(f"Response content: {response.text}")
            return {'success': False, 'error': 'Unexpected response content type'}
    except Exception as e:
        print(f"Error running task {task_id}: {e}")
        return {'success': False, 'error': str(e)}


# 批量运行任务
@app.route('/api/tasks/batch/run', methods=['POST'])
def batch_run_tasks():
    task_ids = request.json
    if not isinstance(task_ids, list):
        return jsonify({'error': 'Invalid data format. Expected a list of task IDs.'}), 400
    results = []
    for task_id in task_ids:
        result = sync_run_task(task_id, True)
        results.append(result)
    return jsonify({'results': results})

@app.route('/api/tasks/batch/stop', methods=['POST'])
def batch_stop_tasks():
    task_ids = request.json
    if not isinstance(task_ids, list):
        return jsonify({'error': 'Invalid data format. Expected a list of task IDs.'}), 400
    results = []
    for task_id in task_ids:
        result = sync_run_task(task_id, False)
        results.append(result)
    return jsonify({'results': results})



# 批量下载JSON文件
@app.route('/api/tasks/batch/download', methods=['POST'])
def batch_download_tasks():
    task_ids = request.json
    if not isinstance(task_ids, list):
        return jsonify({'error': 'Invalid data format. Expected a list of task IDs.'}), 400
    all_task_data = {}
    for task_id in task_ids:
        task = tasks_table.get(Query().id == task_id)
        if task:
            last_run_time = task.get('lastRunTime')
            if last_run_time:
                formatted_time = last_run_time.replace(' ', '_').replace(':', '.')
                output_dir = os.path.join('data', str(task_id))
                filename = f'{formatted_time}.json'
                filepath = os.path.join(output_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        try:
                            task_data = json.load(f)
                            all_task_data[task_id] = task_data
                        except json.JSONDecodeError:
                            # 处理JSON解析错误
                            print(f"Error decoding JSON file for task {task_id} at {filepath}")
    # 将所有任务数据转换为JSON字符串
    json_data = json.dumps(all_task_data, ensure_ascii=False, indent=4)
    # 返回JSON响应
    response = app.response_class(
        response=json_data,
        status=200,
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=batch_download.json'
    return response


# 获取任务的爬取结果预览
@app.route('/api/tasks/<string:task_id>/preview', methods=['GET'])
def preview_task_results(task_id):
    Result = Query()
    # 获取最新的结果
    results = results_table.search(Result.task_id == task_id)
    if not results:
        return jsonify({'success': False, 'error': '暂无爬取结果'}), 404
    latest_result = max(results, key=lambda x: x['run_time'])
    return jsonify({'success': True, 'result': latest_result['result']})


# 通过json导入
@app.route('/api/tasks/import', methods=['POST'])
def import_tasks():
    try:
        # 获取请求中的JSON数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        if not isinstance(data, list):
            return jsonify({"error": "Invalid JSON data format, must be list"}), 400
        # 定义一个样本任务，可根据实际情况调整
        sample_task = {
            "cookies": "",
            "crawlMode": "general",
            "dataFormat": "txt",
            "days": 1,
            "execTime": "00:00",
            "id": "",
            "interval": 1,
            "isActive": False,
            "lastRunTime": "",
            "maxCount": 10,
            "next_run_time": None,
            "otherValues": [],
            "parseType": 0,
            "parseValues": [],
            "schedule": "00 00 */1 * *",
            "scheduleType": "fixed",
            "table_pattern": "",
            "title": "",
            "url": "",
            "xpaths": {
                "next_page": "",
                "row": "",
                "table": ""
            }
        }
        for task in data:
            task_id = task.get('id')
            if task_id:
                existing_task = tasks_table.get(Query().id == task_id)
                if existing_task:
                    print(f"任务 {task_id} 已存在，跳过导入")
                    continue
            # 遍历样本任务的字段，将缺失的字段设为空
            for field, default_value in sample_task.items():
                if field not in task:
                    task[field] = default_value
            tasks_table.insert(task)
        return jsonify({"success": True, "message": "Tasks imported successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    init_scheduler()
    # app.run(debug=True, port=5000) # 调试模式下会重复运行定时任务
    app.run(debug=False, port=5000)