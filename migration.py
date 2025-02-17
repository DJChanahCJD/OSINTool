from tinydb import TinyDB, Query

db = TinyDB('db.json')
tasks_table = db.table('tasks')

def migrate_add_next_run_time():
    Task = Query()
    # 遍历所有任务，如果没有 next_run_time 字段，则添加默认值 None
    for task in tasks_table.all():
        if 'next_run_time' not in task:
            tasks_table.update({'next_run_time': None}, Task.id == task['id'])
    print("迁移完成，所有任务已添加 next_run_time 字段。")

if __name__ == '__main__':
    migrate_add_next_run_time()
