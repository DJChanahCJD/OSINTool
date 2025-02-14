const { contextBridge, shell } = require('electron')
const { Titlebar, TitlebarColor } = require("custom-electron-titlebar");
const path = require('path');

const customColor = TitlebarColor.fromHex('#66B1FF');
window.addEventListener('DOMContentLoaded', () => {
    // Title bar implementation
    new Titlebar({
        backgroundColor: customColor,
        icon: '../logo.png',
        // shadow: false
    });
});

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

    parseTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/parse`, {
            method: 'POST'
        }).then(response => response.json())
    },

    // 执行任务
    runTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/run`, {
            method: 'POST'
        }).then(response => response.json())
    },
    // 打开根目录data/taskId
    openTaskResultFolder: (taskId) => {
        const rootPath = path.resolve(__dirname, '..');  // 根目录
        const taskPath = path.join(rootPath, 'data', taskId);  // 对应id的任务解析结果目录
        shell.openPath(taskPath).then((error) => {
            if (error) {
                console.error('Failed to open folder:', error);
            }
        });
    }
})