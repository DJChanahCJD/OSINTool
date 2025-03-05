from contextlib import asynccontextmanager
import random
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from tinydb import TinyDB, Query as TinyDBQuery
import json
from datetime import datetime
import os
import shortuuid
from models.common import TaskIds
from utils.parser_factory import ParserFactory
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from models import PaginatedResponse, Task
from middleware import setup_cors_middleware, RequestLoggingMiddleware
from middleware.logging import setup_logger
import pathlib
from uvicorn import Config, Server

root_dir = pathlib.Path(__file__) # 获取项目根目录
DB_PATH = os.getenv('DB_PATH', 'db.json')

# 先初始化logger
logger = setup_logger()

# 创建启动事件管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时运行
    print("正在初始化调度器")

    # 初始化调度器
    init_scheduler()
    scheduler.start()

    yield   # FastAPI 应用运行期间

    # 关闭时运行
    print("正在关闭调度器")
    scheduler.shutdown()

# 创建 FastAPI 应用实例
app = FastAPI(
    title="任务管理系统",
    description="任务调度和管理API",
    version="1.0.0",
    lifespan=lifespan,
    redoc_url=None
)

# app创建后才能添加中间件
app.add_middleware(RequestLoggingMiddleware, logger=logger)
setup_cors_middleware(app)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板
templates = Jinja2Templates(directory="templates")

# 添加页面路由
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/edit")
async def edit(request: Request):
    return templates.TemplateResponse("edit.html", {"request": request})

# 初始化 TinyDB
db = TinyDB(DB_PATH)
tasks_table = db.table('tasks')

# 初始化调度器
scheduler = AsyncIOScheduler()

@app.get('/api/tasks', response_model=List[Task], tags=['获取所有任务'])
def get_tasks():
    try:
        tasks = tasks_table.all()
        return tasks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务时出错：{e}")

@app.get('/api/tasks/basic', response_model=List[Task], tags=['获取所有任务的基本信息'])
def get_basic_tasks():
    try:
        tasks = tasks_table.all()
        # 只返回必要的字段（用于edit.html）
        necessary_fields = ['id', 'title', 'isActive']
        result = []
        for task in tasks:
            filtered_task = {field: task.get(field) for field in necessary_fields}
            result.append(filtered_task)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务时出错：{e}")

@app.get('/api/tasks/paginated', response_model=PaginatedResponse)
async def get_tasks_paginated(
    page: Optional[int] = Query(default=1, description="页码"),
    perPage: Optional[int] = Query(default=10, description="每页数量"),
    searchQuery: Optional[str] = Query(default="", description="搜索关键词"),
    sort: Optional[str] = Query(default="[]", description="排序条件"),
    filters: Optional[str] = Query(default="{}", description="筛选条件")
):
    try:
        # 解析 JSON 字符串
        sort_conditions = json.loads(sort)
        filter_conditions = json.loads(filters)

        # 获取所有任务
        tasks = tasks_table.all()

        # 搜索过滤
        if searchQuery:
            tasks = [t for t in tasks if searchQuery.lower() in t.get('title', '').lower()
                    or searchQuery.lower() in t.get('url', '').lower()]

        # 筛选过滤
        if filter_conditions:
            for field, values in filter_conditions.items():
                if values:
                    tasks = [t for t in tasks if t.get(field) in values]

        # 排序处理
        if sort_conditions:
            for cond in reversed(sort_conditions):
                field = cond.get("sortField")
                order = cond.get("sortOrder", "asc")
                tasks.sort(
                    key=lambda t: "" if t.get(field) is None else t.get(field),
                    reverse=(order == "desc")
                )

        # 分页处理
        total = len(tasks)
        start = (page - 1) * perPage
        end = start + perPage
        paginated_tasks = tasks[start:end]

        return {
            "page": page,
            "perPage": perPage,
            "total": total,
            "data": paginated_tasks
        }
    except Exception as e:
        logger.error(f"获取分页任务时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/api/tasks', response_model=Task)
async def create_task(task: Task):
    try:
        task_id = str(shortuuid.uuid())
        task.id = task_id
        tasks_table.insert(task.model_dump())
        if task.isActive:
            schedule_task(task.model_dump())
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务时出错: {e}")

@app.get('/api/tasks/{task_id}', response_model=Task)
def get_task(task_id: str):
    task = tasks_table.get(TinyDBQuery().id == task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务未找到")
    return task

@app.put('/api/tasks/{task_id}', response_model=Task)
async def update_task(task_id: str, task: Task):
    try:
        Task = TinyDBQuery()
        tasks_table.update(task.model_dump(), Task.id == task_id)
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)   # 先删除原有任务
        if task.isActive:
            schedule_task(task.model_dump())
        return task
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新任务时出错: {e}")

@app.delete('/api/tasks/{task_id}')
def delete_task(task_id: str):
    try:
        Task = TinyDBQuery()
        tasks_table.remove(Task.id == task_id)
        if scheduler.get_job(task_id):
            scheduler.remove_job(task_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除任务时出错: {e}")


# 批量删除
@app.delete('/api/tasks/batch_delete')
def delete_tasks(taskIds: TaskIds):
    try:
        ids = taskIds.taskIds
        tasks_table.remove(TinyDBQuery().id.one_of(ids))
        for task_id in ids:
            if scheduler.get_job(task_id):
                scheduler.remove_job(task_id)
        return {"success": True, "msg": f"批量删除任务成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除任务失败: {e}")


@app.put('/api/tasks/{task_id}/status')
async def update_task_status(task_id: str, isActive: bool):
    try:
        await update_task_status_func(task_id, isActive)
        print(f"更新任务状态成功, ID: {task_id}, 运行中: {isActive}")
        return {"success": True, "msg": f"运行中: {isActive}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新任务状态失败: {e}")

async def update_task_status_func(task_id, isActive):
    Task = TinyDBQuery()
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

@app.post('/api/tasks/{task_id}/parse')
async def parse_task(task_id: str):    # 预览
    Task = TinyDBQuery()
    task = tasks_table.get(Task.id == task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    max_count = min(task['maxCount'], 20)  # 最大返回20条数据
    try:
        table = await execute_task_parsing(task, max_count)
        return {
            'success': True,
            'table': table
        }
    except Exception as e:
        logger.error(f"预览任务解析失败: {e}")
        raise HTTPException(status_code=500, detail=f"预览任务解析失败: {e}")

@app.post('/api/tasks/{task_id}/run')
async def run_task(task_id: str):
    Task = TinyDBQuery()
    task = tasks_table.get(Task.id == task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    print(f'===========正在运行任务: {task_id}============')

    if task['crawlMode'] == 'pro':  # 专家模式
        return {"success": False, "message": "网页版暂无专家模式"}

    # 普通模式(task['crawlMode'] == 'general')

    max_count = task['maxCount']  # 获取最大数据量
    try:
        result = await execute_task_parsing(task, max_count)

        # 更新任务的 lastRunTime
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        Task = TinyDBQuery()
        tasks_table.update({'lastRunTime': current_time}, Task.id == task_id)

        return {
            'success': True,
            'task': {
                'id': task['id'],
                'lastRunTime': current_time,
            },
            'data': result  # 直接返回解析结果
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务运行失败: {e}")

#批量启动
@app.post('/api/tasks/batch_start')
async def batch_start_tasks(taskIds: TaskIds):
    try:
        task_ids = taskIds.taskIds
        for task_id in task_ids:
            await update_task_status_func(task_id, True)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量启动任务失败: {e}")

#批量停止
@app.post('/api/tasks/batch_stop')
async def batch_stop_tasks(taskIds: TaskIds):
    try:
        task_ids = taskIds.taskIds
        for task_id in task_ids:
            await update_task_status_func(task_id, False)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量停止任务失败: {e}")

# 批量导出
@app.post('/api/tasks/batch_export')
def batch_export_tasks(taskIds: TaskIds):
    try:
        task_ids = taskIds.taskIds
        if not task_ids:
            raise HTTPException(status_code=400, detail="未提供任务ID")

        Task = TinyDBQuery()
        tasks = tasks_table.search(Task.id.one_of(task_ids))
        return {"success": True, "data": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量导出任务失败: {e}")

# 通过json导入
@app.post('/api/tasks/import')
def import_tasks(data: List[Task]):
    try:
        # 定义一个样本任务，可根据实际情况调整
        sample_task = {"cookies": "", "crawlMode": "general", "dataFormat": "html", "days": 1, "execTime": "00:00",
                       "id": "", "interval": 1, "isActive": False, "lastRunTime": "", "maxCount": 1,
                       "next_run_time": None, "title": "", "url": "", "scheduleType": "random",
                       "table_pattern": "", "schedule": "", "tableType": "0",
                       "xpaths": {"next_page": "", "row": "", "table": ""},
                       "parseValues": [], "otherValues": [], "parseType": 1,
                       "before_action_group": [], "children": []}

        for task in data:
            task_id = task.get('id')
            if task_id:
                existing_task = tasks_table.get(TinyDBQuery().id == task_id)
                if existing_task:
                    print(f"任务 {task_id} 已存在，跳过导入")
                    continue
            # 遍历样本任务的字段，将缺失的字段设为空
            for field, default_value in sample_task.items():
                if field not in task:
                    task[field] = default_value

            tasks_table.insert(task)

        return {"success": True, "message": "任务导入成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入任务失败: {e}")

async def execute_task_parsing(task, max_count):
    # 根据数据格式初始化解析器
    parser = ParserFactory.get_parser(task)
    result = await parser.parse(max_count, context=None)
    return result

async def run_scheduled_task(task_id):
    with app.app_context():
        await run_task(task_id)
        job = scheduler.get_job(task_id)
        if job:
            next_run_time = job.trigger.get_next_fire_time(None, datetime.now().astimezone())   # 获取下一次运行时间(以当前系统时区为准)
            next_run_time_str = next_run_time.strftime('%Y-%m-%d %H:%M:%S') if next_run_time else None
            Task = TinyDBQuery()
            tasks_table.update({'next_run_time': next_run_time_str}, Task.id == task_id)

            print(f"任务 {task_id} 已运行, 下次运行时间: {next_run_time_str}")
        else:
            print(f"未找到任务 {task_id} 的调度信息")

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
        next_run_time = job.trigger.get_next_fire_time(None, datetime.now().astimezone())   # 获取下一次运行时间(以当前系统时区为准)
        next_run_time_str = next_run_time.strftime('%Y-%m-%d %H:%M:%S') if next_run_time else None
        Task = TinyDBQuery()
        tasks_table.update({'next_run_time': next_run_time_str}, Task.id == task_id)

    print(f"已添加定时任务: {task_id}")
    print(f"任务详情: {task}")

def init_scheduler():
    tasks = tasks_table.all()
    for task in tasks:
        if task.get('isActive', True):
            schedule_task(task)

if __name__ == '__main__':
    # 配置服务器
    config = Config(
        app=app,
        host="0.0.0.0",
        port=8081,
        reload=False,
        workers=1
    )
    # 使用 uvicorn 的 Server
    server = Server(config=config)
    server.run()
