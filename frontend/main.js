const { app, BrowserWindow } = require('electron')
const path = require('path')

const { setupTitlebar, attachTitlebarToWindow } = require("custom-electron-titlebar/main");

// setup the titlebar main process
setupTitlebar();

function createWindow () {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    titleBarStyle: 'hidden',  // 隐藏默认标题栏
    titleBarOverlay: true,  // 使用自定义标题栏
    // frame: false,  // 禁用默认边框
    webPreferences: {
      sandbox: false,             // 禁用沙箱
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,     // 禁用 nodeIntegration
      contextIsolation: true,     // 启用上下文隔离
      enableRemoteModule: false   // 禁用远程模块，通过ipc通信
    }
  })

  attachTitlebarToWindow(mainWindow);
  
  mainWindow.loadFile('index.html')

  // 开发时打开开发者工具
  // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit()
})
