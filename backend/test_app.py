import os
import pytest
from fastapi.testclient import TestClient
from tinydb import TinyDB

# 设置测试环境变量和测试数据库路径
os.environ['TESTING'] = '1'
DB_PATH = '../test_db.json'
os.environ['DB_PATH'] = DB_PATH  # 设置测试数据库路径

# 确保在导入 app 之前关闭可能存在的数据库连接
db = None

# 现在导入 app
from app import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_teardown():
    """每次测试前后的设置和清理"""
    # 确保数据库连接被关闭
    global db
    if hasattr(app, 'db') and app.db:
        app.db.close()

    # 清空数据库内容而不是删除文件
    db = TinyDB(DB_PATH)
    db.truncate()  # 这会清空所有表，包括 tasks 表

    yield

    # 测试后清理
    if db:
        db.close()

# 测试数据
test_task = {
    "title": "测试任务",
    "description": "这是一个测试任务",
    "scheduleType": "interval",
    "interval": 10,
    "isActive": True
}

def test_create_task():
    """测试创建任务"""

    response = client.post("/api/tasks", json=test_task)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data

def test_get_tasks_paginated():
    """测试分页获取任务列表"""
    params = {
        "page": 1,
        "perPage": 10,
        "searchQuery": "",
        "sort": '[{"sortField":"title","sortOrder":"asc"}]',
        "filters": '{"scheduleType":["interval"]}'
    }
    response = client.get("/api/tasks/paginated", params=params)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data

def test_get_task():
    """测试获取单个任务"""
    # 先创建一个任务
    task_id = test_create_task()
    response = client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id

def test_update_task():
    """测试更新任务"""
    task_id = test_create_task()
    updated_task = test_task.copy()
    updated_task["title"] = "更新后的测试任务"
    response = client.put(f"/api/tasks/{task_id}", json=updated_task)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "更新后的测试任务"

def test_delete_task():
    """测试删除任务"""
    task_id = test_create_task()
    response = client.delete(f"/api/tasks/{task_id}")
    assert response.status_code == 200

def test_batch_operations():
    """测试批量操作"""
    # 创建多个测试任务
    task_ids = [test_create_task() for _ in range(3)]

    # 测试批量启动
    response = client.post("/api/tasks/batch_start", json={"taskIds": task_ids})
    assert response.status_code == 200

    # 测试批量停止
    response = client.post("/api/tasks/batch_stop", json={"taskIds": task_ids})
    assert response.status_code == 200

    # 测试批量删除
    response = client.delete("/api/tasks/batch_delete", json={"taskIds": task_ids})
    assert response.status_code == 200

def test_task_parse():
    """测试任务解析"""
    task_id = test_create_task()
    response = client.post(f"/api/tasks/{task_id}/parse")
    assert response.status_code == 200

def test_task_run():
    """测试任务运行"""
    task_id = test_create_task()
    response = client.post(f"/api/tasks/{task_id}/run")
    assert response.status_code == 200

if __name__ == "__main__":
    pytest.main(["-v", "test_app.py"])