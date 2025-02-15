import random
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from tinydb import TinyDB, Query
import json
from datetime import datetime
import os
import shortuuid
from utils.parser_factory import ParserFactory
from utils.parsers.html_parser import HTMLParser
from utils.regex_matcher import parse_keywords, parse_first_keyword
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
import aiohttp
import zipfile
import io

app = Flask(__name__)
CORS(app)

# 初始化 TinyDB
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

    # 这里可以进一步扩展统计信息，例如成功和失败的任务数量
    # 假设我们有一个 results_table 存储任务结果
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
    # 获取前端传递的页码和每页数量，默认每页显示 5 条
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
        scheduler.remove_job(task_id)  # 先删除原有任务
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
    running_tasks = [{'id': job.id, 'next_run_time': job.next_run_time} for job in jobs]
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
            print(f'if 结束')
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

        # 更新 lastRunTime 字段
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
        scheduler.add_job(run_scheduled_task, 'cron', day=f'*/{days}', hour=hour, minute=minute, id=task_id,
                          kwargs={'task_id': task_id})
    elif schedule_type == 'interval':
        interval = task['interval']
        scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})
    elif schedule_type == 'random':
        interval = random.randint(0, 4096)  # 0 - 4096 分钟之间
        if interval == 0:
            # 使用 date 触发器立即调度任务
            scheduler.add_job(run_scheduled_task, 'date', run_date=datetime.now(), id=task_id,
                              kwargs={'task_id': task_id})
            interval = random.randint(1, 4096)
        scheduler.add_job(run_scheduled_task, 'interval', minutes=interval, id=task_id, kwargs={'task_id': task_id})

    print(f"已添加定时任务: {task_id}")
    print(f"任务详情: {task}")


def init_scheduler():
    print("初始化调度器")
    scheduler.start()
    tasks = tasks_table.all()
    for task in tasks:
        if task.get('isActive', True):
            schedule_task(task)


@app.route('/api/tasks/batch', methods=['POST'])
def batch_create_tasks():
    data = request.json
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid data format. Expected a list of tasks.'}), 400
    created_task_ids = []
    for task in data:
        task_id = str(shortuuid.uuid())
        task['id'] = task_id
        tasks_table.insert(task)
        if task.get('isActive', True):
            schedule_task(task)
        created_task_ids.append(task_id)
    return jsonify({'created_task_ids': created_task_ids}), 201


# 异步运行单个任务
async def async_run_task(session, task_id):
    url = f'http://localhost:5000/api/tasks/{task_id}/run'
    async with session.post(url) as response:
        return await response.json()


# 批量运行任务
@app.route('/api/tasks/batch/run', methods=['POST'])
async def batch_run_tasks():
    task_ids = request.json
    if not isinstance(task_ids, list):
        return jsonify({'error': 'Invalid data format. Expected a list of task IDs.'}), 400

    async with aiohttp.ClientSession() as session:
        tasks = [async_run_task(session, task_id) for task_id in task_ids]
        results = await asyncio.gather(*tasks)

    return jsonify({'results': results})


# 批量下载 JSON 文件
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
                            # 处理 JSON 解析错误
                            print(f"Error decoding JSON file for task {task_id} at {filepath}")

    # 将所有任务数据转换为 JSON 字符串
    json_data = json.dumps(all_task_data, ensure_ascii=False, indent=4)

    # 返回 JSON 响应
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


if __name__ == '__main__':
    init_scheduler()
    # app.run(debug=True, port=5000) # 调试模式下会重复运行定时任务
    app.run(debug=False, port=5000)