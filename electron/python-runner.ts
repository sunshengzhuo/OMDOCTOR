/**
 * FastAPI 后端子进程管理
 *
 * 职责：
 * 1. 查找/启动 Python 后端进程
 * 2. 健康检查轮询
 * 3. 优雅关闭
 */
import { spawn, ChildProcess } from 'child_process'
import * as http from 'http'
import * as path from 'path'

let backendProcess: ChildProcess | null = null

/**
 * 获取 Python 可执行文件路径
 * 开发模式: 系统 Python
 * 生产模式: PyInstaller 打包的 exe
 */
function getPythonCommand(): { cmd: string; args: string[] } {
  const isPackaged = __dirname.includes('app.asar')

  if (isPackaged) {
    // 生产模式：运行打包后的 exe
    const exePath = path.join(process.resourcesPath, 'backend', 'tcm-backend.exe')
    return { cmd: exePath, args: [] }
  } else {
    // 开发模式：使用系统 Python 运行 uvicorn
    const backendDir = path.resolve(__dirname, '..', 'backend')
    return {
      cmd: 'python',
      args: ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(8765)],
    }
  }
}

/**
 * 健康检查：轮询 /health 接口
 */
function waitForBackend(port: number, maxRetries = 20, interval = 500): Promise<void> {
  return new Promise((resolve, reject) => {
    let retries = 0

    const check = () => {
      const req = http.get(`http://127.0.0.1:${port}/health`, (res) => {
        if (res.statusCode === 200) {
          console.log('[PythonRunner] Backend is ready!')
          resolve()
        } else {
          retry()
        }
      })

      req.on('error', () => retry())
      req.setTimeout(2000, () => {
        req.destroy()
        retry()
      })
    }

    const retry = () => {
      retries++
      if (retries >= maxRetries) {
        reject(new Error(`Backend failed to start after ${maxRetries} retries`))
      } else {
        setTimeout(check, interval)
      }
    }

    check()
  })
}

/**
 * 启动 FastAPI 后端
 */
export async function startPythonBackend(port: number): Promise<void> {
  const { cmd, args } = getPythonCommand()
  const isPackaged = __dirname.includes('app.asar')

  console.log(`[PythonRunner] Starting: ${cmd} ${args.join(' ')}`)

  const spawnOptions: any = {
    env: { ...process.env },
    stdio: ['pipe', 'pipe', 'pipe'],
  }

  // 开发模式下设置 cwd 为 backend 目录；打包模式由 run.py 自行处理 CWD
  if (!isPackaged) {
    spawnOptions.cwd = path.resolve(__dirname, '..', 'backend')
    console.log(`[PythonRunner] Working dir: ${spawnOptions.cwd}`)
  }

  backendProcess = spawn(cmd, args, spawnOptions)

  backendProcess.stdout?.on('data', (data: Buffer) => {
    console.log(`[Backend] ${data.toString().trim()}`)
  })

  backendProcess.stderr?.on('data', (data: Buffer) => {
    console.error(`[Backend:ERR] ${data.toString().trim()}`)
  })

  backendProcess.on('error', (err) => {
    console.error('[PythonRunner] Failed to start backend:', err)
  })

  backendProcess.on('exit', (code) => {
    console.log(`[PythonRunner] Backend exited with code ${code}`)
    backendProcess = null
  })

  // 等待后端就绪
  try {
    await waitForBackend(port)
  } catch (err) {
    console.error('[PythonRunner] Backend startup timeout')
    throw err
  }
}

/**
 * 停止 FastAPI 后端
 */
export async function stopPythonBackend(): Promise<void> {
  if (backendProcess) {
    console.log('[PythonRunner] Stopping backend...')
    backendProcess.kill('SIGTERM')

    // 等待进程退出
    await new Promise<void>((resolve) => {
      if (!backendProcess) {
        resolve()
        return
      }
      const timeout = setTimeout(() => {
        backendProcess?.kill('SIGKILL')
        resolve()
      }, 5000)

      backendProcess.on('exit', () => {
        clearTimeout(timeout)
        resolve()
      })
    })

    backendProcess = null
  }
}
