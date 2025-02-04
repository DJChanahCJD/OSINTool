from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    # 这里可以返回任务列表，例如从数据库中获取
    tasks = [
        {'id': 1, 'title': 'Task 1', 'description': 'This is task 1'},
        {'id': 2, 'title': 'Task 2', 'description': 'This is task 2'}
    ]
    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
def create_task():
    # 这里可以处理创建任务的逻辑，例如将任务保存到数据库
    task = request.json
    # 假设任务创建成功，返回任务ID
    task_id = 1
    return jsonify({'id': task_id}), 201

if __name__ == '__main__':
    app.run(debug=True)
