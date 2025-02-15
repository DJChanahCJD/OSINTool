const { contextBridge } = require('electron');
const { Titlebar, TitlebarColor } = require("custom-electron-titlebar");

// 设置自定义标题栏颜色
const customColor = TitlebarColor.fromHex('#66B1FF');

// 当 DOM 内容加载完成时，初始化自定义标题栏
window.addEventListener('DOMContentLoaded', () => {
    new Titlebar({
        backgroundColor: customColor,
        icon: '../logo.png',
        // shadow: false
    });
});

// 通过 contextBridge 暴露 API 给主窗口
contextBridge.exposeInMainWorld('api', {
    // 获取所有任务，支持分页和搜索
    getTasks: (params = {}) => {
        const { page = 1, per_page = 5, search_query = '' } = params;
        const queryParams = new URLSearchParams({
            page,
            per_page,
            search_query
        });
        return fetch(`http://localhost:5000/getTasks?${queryParams.toString()}`)
           .then(response => response.json());
    },

    // 获取单个任务
    getTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}`)
           .then(response => response.json());
    },

    // 创建单个任务
    createTask: (task) => {
        return fetch('http://localhost:5000/api/tasks', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        }).then(response => response.json());
    },

    // 更新任务
    updateTask: (taskId, task) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        }).then(response => response.json());
    },

    // 删除任务
    deleteTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}`, {
            method: 'DELETE'
        }).then(response => response.json());
    },

    // 更新任务状态
    updateTaskStatus: (taskId, isActive) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ isActive })
        }).then(response => response.json());
    },

    // 解析任务
    parseTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/parse`, {
            method: 'POST'
        }).then(response => response.json());
    },

    // 执行任务
    runTask: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/run`, {
            method: 'POST'
        }).then(response => response.json());
    },

    // 批量创建任务
    batchCreateTasks: (tasks) => {
        return fetch('http://localhost:5000/api/tasks/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tasks)
        }).then(response => response.json());
    },

    // 批量运行任务
    batchRunTasks: (taskIds) => {
        return fetch('http://localhost:5000/api/tasks/batch/run', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskIds)
        }).then(response => response.json());
    },

    // 批量下载 JSON 文件
    batchDownloadTasks: (taskIds) => {
        return fetch('http://localhost:5000/api/tasks/batch/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(taskIds)
        }).then(response => response.blob());
    },

    // 预览任务爬取结果
    previewTaskResults: (taskId) => {
        return fetch(`http://localhost:5000/api/tasks/${taskId}/preview`)
           .then(response => response.json());
    },

    getTaskStats: () => {
        return fetch('http://localhost:5000/api/tasks/stats')
           .then(response => response.json());
    }
});

