/**
 * Electron 主进程入口
 *
 * 职责：
 * 1. 启动 FastAPI 后端子进程
 * 2. 创建 BrowserWindow 加载前端页面
 * 3. 管理应用生命周期
 */
import { app, BrowserWindow, ipcMain } from 'electron'
import * as path from 'path'
import { startPythonBackend, stopPythonBackend } from './python-runner'

let mainWindow: BrowserWindow | null = null
const isDev = process.argv.includes('--dev')

// 后端端口
const BACKEND_PORT = 8765
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`

async function createWindow() {
  // 启动 FastAPI 后端
  console.log('[Main] Starting FastAPI backend...')
  try {
    await startPythonBackend(BACKEND_PORT)
  } catch (err) {
    console.error('[Main] Backend failed to start, continuing without it:', err)
  }

  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: '中医诊所问诊管理平台',
    icon: path.join(__dirname, '..', 'resources', 'icon.ico'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  })

  // 加载前端页面
  if (isDev) {
    // 开发模式：加载 Vite dev server
    const frontendUrl = 'http://localhost:5173'
    console.log(`[Main] Loading frontend from: ${frontendUrl}`)
    await mainWindow.loadURL(frontendUrl)
    mainWindow.webContents.openDevTools()
  } else {
    // 生产模式：加载构建后的静态文件
    // asar 内结构: /electron/dist/main.js, /frontend/dist/index.html
    // __dirname = /electron/dist/，需要 ../../ 到根再进 frontend/dist/
    const frontendPath = path.join(__dirname, '../../frontend/dist/index.html')
    console.log(`[Main] Loading frontend from: ${frontendPath}`)
    await mainWindow.loadFile(frontendPath)
  }

  mainWindow.on('closed', () => {
    mainWindow = null
  })
}

// 应用启动
app.whenReady().then(createWindow)

// 所有窗口关闭时退出
app.on('window-all-closed', async () => {
  // 停止后端进程
  await stopPythonBackend()
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow()
  }
})

// 应用退出前清理
app.on('before-quit', async () => {
  await stopPythonBackend()
})

// IPC 通信
ipcMain.handle('get-backend-url', () => BACKEND_URL)
ipcMain.handle('get-app-version', () => app.getVersion())
