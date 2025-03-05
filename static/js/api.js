// 创建新文件 backend/static/js.js
const baseURL = '/api';

const api = {
    // 获取所有任务
    getTasks: () => {
        return fetch(`${baseURL}/tasks`)
            .then(response => response.json())
    },

    getTasksBasic: () => {
        return fetch(`${baseURL}/tasks/basic`)
          .then(response => response.json())
    },

    // 获取分页任务
    getTasksPaginated: (params) => {
        // 将对象参数转为查询字符串
        const queryParams = new URLSearchParams(params).toString();
        return fetch(`${baseURL}/tasks/paginated?${queryParams}`)
            .then(response => response.json())
    },

    // 获取单个任务
    getTask: (taskId) => {
        return fetch(`${baseURL}/tasks/${taskId}`)
            .then(response => response.json())
    },

    // 创建任务
    createTask: (task) => {
        return fetch(`${baseURL}/tasks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        }).then(response => response.json())
    },

    // 更新任务
    updateTask: (taskId, task) => {
        return fetch(`${baseURL}/tasks/${taskId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(task)
        }).then(response => response.json())
    },

    // 删除任务
    deleteTask: (taskId) => {
        return fetch(`${baseURL}/tasks/${taskId}`, {
            method: 'DELETE'
        }).then(response => response.json())
    },

    updateTaskStatus: (taskId, isActive) => {
        return fetch(`${baseURL}/tasks/${taskId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ isActive })
        }).then(response => response.json())
    },

    parseTask: (taskId) => {
        return fetch(`${baseURL}/tasks/${taskId}/parse`, {
            method: 'POST'
        }).then(response => response.json())
    },

    // 执行任务
    runTask: (taskId) => {
        return fetch(`${baseURL}/tasks/${taskId}/run`, {
            method: 'POST'
        }).then(response => response.json())
    },

    // 批量删除任务
    deleteTasks: (taskIds) => {
        return fetch(`${baseURL}/tasks/batch_delete`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ taskIds })
        }).then(response => response.json())
    },
    // 批量运行
    runTasks: (taskIds) => {
        return fetch(`${baseURL}/tasks/batch_start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ taskIds })
        }).then(response => response.json())
    },
    // 批量停止
    stopTasks: (taskIds) => {
        return fetch(`${baseURL}/tasks/batch_stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ taskIds })
        }).then(response => response.json())
    },
    // 导入
    importTasks: (jsonData) => {
        return fetch(`${baseURL}/tasks/import`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jsonData)
        }).then(response => response.json());
    },
    // 修改导出任务方法
    exportTasks: async (taskIds) => {
        try {
            const response = await fetch(`${baseURL}/tasks/export?${new URLSearchParams({task_ids: taskIds})}`);
            if (!response.ok) throw new Error('导出失败');

            // 触发文件下载
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = response.headers.get('content-disposition').split('filename=')[1];
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            return true;
        } catch (error) {
            console.error('导出失败:', error);
            return false;
        }
    },
    // 修改脚本上传方法
    uploadScript: async (id, file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${baseURL}/tasks/${id}/upload-script`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) throw new Error('上传失败');
            return true;
        } catch (error) {
            console.error('上传失败:', error);
            return false;
        }
    },
    // 检查脚本是否存在
    checkScriptExists: (taskId) => {
        const scriptDir = path.join(rootPath, 'script');
        const scriptPath = path.join(scriptDir, `${taskId}.py`);
        return fs.existsSync(scriptPath);
    },
    openScriptFile: (id) => {
        const scriptDir = path.join(rootPath, 'script');
        const scriptPath = path.join(scriptDir, `${id}.py`);
        shell.openPath(scriptPath).then((error) => {
            if (error) {
                console.error('Failed to open script file:', error);
            }
        });
    },
    openLocalFile: (filePath) => {
        shell.openPath(filePath).then((error) => {
            if (error) {
                console.error('Failed to open file:', error);
            }
        });
    },
    sendToRenderer: (channel, data) => ipcRenderer.send(channel, data),
    receiveFromMain: (channel, func) => ipcRenderer.on(channel, (event, ...args) => func(...args)),
    // 获取任务结果列表
    getTaskResults: async (taskId) => {
        try {
            const response = await fetch(`${baseURL}/tasks/${taskId}/results`);
            if (!response.ok) throw new Error('获取结果失败');
            return await response.json();
        } catch (error) {
            console.error('获取结果失败:', error);
            throw error;
        }
    },
    // 下载结果文件
    downloadResultFile: async (taskId, filename) => {
        try {
            const response = await fetch(`${baseURL}/tasks/${taskId}/results/${filename}`);
            if (!response.ok) throw new Error('下载失败');

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            return true;
        } catch (error) {
            console.error('下载失败:', error);
            return false;
        }
    }
}

// 暴露给全局
window.api = api;