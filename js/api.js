const baseURL = `http://8.134.56.232:8081/api`;

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
        return fetch(`${baseURL}/tasks/${taskId}/status?isActive=${isActive}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
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
            body: JSON.stringify( { taskIds: taskIds } )
        }).then(response => response.json())
    },
    // 批量运行
    runTasks: (taskIds) => {
        return fetch(`${baseURL}/tasks/batch_start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify( { taskIds: taskIds } )
        }).then(response => response.json())
    },
    // 批量停止
    stopTasks: (taskIds) => {
        return fetch(`${baseURL}/tasks/batch_stop`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify( { taskIds: taskIds } )
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
            const response = await fetch(`${baseURL}/tasks/batch_export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify( { taskIds: taskIds } )
            });
            if (!response.ok) throw new Error('导出失败');

            return response.json();
        } catch (error) {
            console.error('导出失败:', error);
            return false;
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