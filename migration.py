from tinydb import TinyDB

# 打开数据库文件
db = TinyDB('db.json')

# 获取所有任务
tasks = db.table('tasks')

# 遍历每个任务
for task in tasks:
    # 检查是否存在 crawlMode 字段
    if 'crawlMode' not in task:
        # 若不存在，则设置为 "general"
        task['crawlMode'] = 'general'
        # 更新数据库中的任务
        tasks.update(task, doc_ids=[task.doc_id])

print("数据迁移完成。")
