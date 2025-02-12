## 项目概述
本项目包含一个Flask后端和一个Electron客户端，用于解析和管理OSINT任务。

### 安装依赖

#### 后端依赖
在项目根目录下运行以下命令安装后端依赖：
```bash
pip install flask flask-cors tinydb shortuuid requests beautifulsoup4 lxml pandas
```

#### 前端依赖
在`frontend`目录下运行以下命令安装前端依赖：
```bash
npm install
```

### 启动步骤
在`根目录`启动Flask后端：

```bash
python app.py
```
在`frontend`目录启动Electron客户端：


```bash
npm start
```