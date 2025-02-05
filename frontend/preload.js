const { contextBridge } = require('electron')

contextBridge.exposeInMainWorld('api', {
    // 获取所有任务
    getTasks: () => {
        return fetch('http://localhost:5000/api/tasks')
            .then(response => response.json())
    },

    // 获取单个任务
    getTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}`)
            .then(response => response.json())
    },

    // 创建任务
    createTask: (task) => {
        return fetch('http://localhost:5000/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        }).then(response => response.json())
    },

    // 更新任务
    updateTask: (taskId, task) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        }).then(response => response.json())
    },

    // 删除任务
    deleteTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}`, {
            method: 'DELETE'
        }).then(response => response.json())
    },

    updateTaskStatus: (taskId, isActive) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ isActive })
        }).then(response => response.json())
    },

    // 执行任务
    runTask: (taskId) => {
        taskId = Number(taskId)
        return fetch(`http://localhost:5000/api/tasks/${taskId}/run`, {
            method: 'POST'
        }).then(response => response.json())
    }
})