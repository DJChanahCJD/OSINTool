## 项目概述
OSINTool包含一个Flask后端和一个Electron客户端，用于解析和管理OSINT任务。

### 功能特性
- **支持多种类型**：文本类（TXT等）、表格类（CSV等）、网页类（HTML等）
- **动态页面解析**：使用 **Playwright** 获取动态加载的 HTML 内容，通过**XPath+正则匹配**的方式定位表格内容，支持分页抓取

### 安装依赖

#### 后端依赖
在项目根目录下运行以下命令安装后端依赖：
```bash
pip install flask flask-cors flask[async] tinydb shortuuid requests lxml pandas apscheduler playwright
playwright install
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

### 注意事项
请确保已经安装了 Playwright 所需的浏览器和驱动，可通过 `playwright install` 命令进行安装。

### Todo
- 支持CSV输出
- 处理OCR/滑动验证码等人机验证
- CI/CD
- 支持网页端部署

### 参考项目
- spider-flow
- 蓝天采集器
- EasySpider
