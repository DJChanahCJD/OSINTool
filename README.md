## 项目概述

OSINTool-Web-Linux 是一个自动化爬虫网页，适用于Linux服务器

> 如果你希望在Windows系统使用本项目，可将app.py的主函数改为
>
> ```python
> if __name__ == '__main__':
>     # 创建自定义的 ProactorServer
>     class ProactorServer(Server):
>         def run(self, sockets=None):
>             # 使用 ProactorEventLoop
>             loop = ProactorEventLoop()
>             asyncio.set_event_loop(loop)
>             asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
>             # 运行服务器
>             asyncio.run(self.serve(sockets=sockets))
> 
>     # 配置服务器
>     config = Config(
>         app=app,
>         host="127.0.0.1",
>         port=8080,
>         reload=False,
>         workers=1
>     )
>     # 使用自定义的 ProactorServer
>     server = ProactorServer(config=config)
>     server.run()
> ```



## 快速开始

### 安装依赖

在项目根目录下运行以下命令安装依赖：

```bash
pip3 install -r requirements.txt
```

### 启动项目

在`根目录`启动：

```bash
python app.py
```

## 技术栈

- 本地服务器：FastAPI(venv Python 3.11)
- 数据爬取：Playwirght, Requests
- 定时任务：APSchedule
- 数据库：TinyDB
- 页面构建：Vue2 + ElementUI

## 项目结构

```
OSINTOOL
├── app.py                   # FastAPI 后端（含 API）
├── db.json                  # TinyDB 数据库
├── osintool.service         # systemd 服务文件
├── requirements.txt         # Python 依赖文件
├── middleware               # 中间件
│   ├── __init__.py
│   ├── cors.py
│   └── logging.py
├── models                   # 数据模型
├── static                   # 静态文件
│   ├── js
│   │   └── api.js
│   └── styles
│       ├── edit.css
│       └── index.css
├── templates                # HTML 模板
│   ├── edit.html
│   └── index.html
└── utils                    # 工具模块
    ├── parsers              # 解析器
    │   ├── base.py
    │   ├── csv_parser.py
    │   ├── html_parser.py
    │   └── txt_parser.py
    ├── common.py            # 通用函数
    └── parser_factory.py    # 解析器工厂
```

## 部署相关

若您期望应用在 Linux 服务器启动时自动运行，可创建一个 systemd 服务。

### 步骤如下：

1. 创建服务文件 `/etc/systemd/system/osintool.service`，内容如下：

```ini
[Unit]
Description=OSINTool
After=network.target

[Service]
User=root
WorkingDirectory=/root/osintool
ExecStart=/root/osintool/venv/bin/python /root/osintool/app.py  # 请将此处修改为 python 和 app.py 的实际位置
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

2. 启用服务：

```bash
sudo systemctl enable myapp.service
```

3. 启动服务：

```bash
sudo systemctl start myapp.service
```

4. 重启服务：

```bash
sudo systemctl restart myapp.service
```

5. 查看服务状态：

```bash
sudo systemctl status myapp.service
```

## 解析器流程图

### TXTParser

![image-20250303203737825](https://djchan-xyz.pages.dev/file/AgACAgUAAyEGAASJIjr1AAICiGfFoxi3bIdwvIiU94eog5ZbiCJeAAL1wzEb3fAwVtcmLMAcq5nmAQADAgADeQADNgQ.png)

### CSVParser

![image-20250303203803022](https://djchan-xyz.pages.dev/file/AgACAgUAAyEGAASJIjr1AAICiWfFoxqbPOEoQK6CWQAB1IGh73xkhAAC9sMxG93wMFaYhIPtx2weqQEAAwIAA3kAAzYE.png)

### HTMLParser

![image-20250303203818303](https://djchan-xyz.pages.dev/file/AgACAgUAAyEGAASJIjr1AAICimfFoxzLLYq7shI0c8LBIn8n1p5WAAL3wzEb3fAwVmpaMTByYxv2AQADAgADeQADNgQ.png)

## 预览图

### 任务列表页（index.html）

![image-20250301183926480](https://djchan-xyz.pages.dev/file/AgACAgUAAyEGAASJIjr1AAICh2fC4-HOyqgoF9BA7GQzpsEpu2L0AAI3wTEb6_wYVsDmm7bD_FC7AQADAgADdwADNgQ.png)

### 任务编辑页（edit.html）

![image-20250301183707849](https://djchan-xyz.pages.dev/file/AgACAgUAAyEGAASJIjr1AAIChmfC41tJdUTdt5uvGi1PxAxR2Ce1AAI1wTEb6_wYVtBNUuqQoP4PAQADAgADdwADNgQ.png)


## Todo

- 支持CSV输出
- 处理OCR/滑动验证码等人机验证
- CI/CD
- 支持网页端部署



## SWOT分析

- **Strengths（优势）**：支持多类型数据解析，自定义程度高 （登录、翻页等），任务调度灵活。
- **Weaknesses（劣势）**：学习成本高，需网页分析与正则基础；可视化差，没有直观界面；暂时无法应对人机验证等反爬技术。
- **Opportunities（机会）**：未来可融合AI实现智能爬取，集成如Excel等工具方便数据分析。
- **Threats（威胁）**：市场已有八爪鱼、EasySpider 等成熟可视化爬取工具；网页反爬技术迭代快 ，需持续更新爬取技术。



## 参考项目

- [八爪鱼采集器](https://www.bazhuayu.com/)
- [EasySpider](https://www.easyspider.net/)