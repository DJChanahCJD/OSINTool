const { contextBridge } = require('electron')

contextBridge.exposeInMainWorld('api', {
  getTasks: () => {
    return fetch('http://localhost:5000/api/tasks')
      .then(response => response.json())
  },
  createTask: (task) => {
    return fetch('http://localhost:5000/api/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(task)
    })
      .then(response => response.json())
  }
})
