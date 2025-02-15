const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');

const { setupTitlebar, attachTitlebarToWindow } = require("custom-electron-titlebar/main");

// setup the titlebar main process
setupTitlebar();

function createWindow() {
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
    });

    attachTitlebarToWindow(mainWindow);

    mainWindow.loadFile('index.html');

    // 开发时打开开发者工具
    // mainWindow.webContents.openDevTools()
}

app.whenReady().then(() => {
    createWindow();

    // 获取当前菜单，如果没有设置菜单，会返回 null
    let menu = Menu.getApplicationMenu();
    if (!menu) {
        // 如果没有菜单，创建一个空的菜单模板
        menu = Menu.buildFromTemplate([]);
    }

    // 在原菜单基础上添加新的菜单项
    const newMenuItem = {
        label: '自定义菜单',
        submenu: [
            {
                label: '子菜单项 1',
                click: () => {
                    console.log('点击了子菜单项 1');
                }
            },
            {
                label: '子菜单项 2',
                click: () => {
                    console.log('点击了子菜单项 2');
                }
            }
        ]
    };

    // 将新的菜单项添加到菜单中
    menu.append(new MenuItem(newMenuItem));

    // 重新设置应用程序菜单
    Menu.setApplicationMenu(menu);

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});

// 引入 MenuItem 类
const { MenuItem } = require('electron');