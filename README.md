\# Flask CRUD 测试项目



\## 项目简介

这是一个基于 Flask 框架的 CRUD（增删改查）接口测试项目，使用 Pytest + Allure 生成自动化测试报告。
增添了ai生成测试用例，用Github Actions进行自动测试


\## 技术栈

\- Python 3.8

\- Flask

\- Pytest

\- Allure

\- Yaml

\- OpenAI

\## 项目结构

Project\_test\_flask/

├──.github/

│ ├──workflows/

│ └── test.yaml #Github Actions自动流程

├── tests/ # 测试用例目录

│ ├──__init__.py

│ ├── conftest.py # pytest fixtures 配置

│ ├──api_client.py #封装CRUD、断言、日志、重试、requests

│ ├──test_ai_case.py #对ai生成用例进行测试

│ └── test_books.py # 图书相关测试用例


├── library_app.py # Flask 应用主文件

├── main.py # 项目入口

├── pytest.ini # pytest 配置文件

├──data/ # 存储数据

│ ├── test_data.yaml #测试数据

│ └── ai_case.yaml #ai生成的测试用例 

├── chat_ai.py # ai大模型

└── .env # 环境变量配置



\### 1. 创建虚拟环境



python -m venv .venv

source .venv/Scripts/activate  # Windows



\## 安装依赖

```python

pip install Flask

pip install pymysql

pip install dotenv

pip install requests

pip install openai

```



\## 运行测试

```bash

pytest tests/ -v

```



\## 生成Allure报告

```bash

allure generate -o report -c temps

allure open report

```



\## 测试结果

http://localhost:63342/Project\_test\_flask/report/index.html?\_ijt=odn4kg6opjbvk8e5s2ep8ua665\&\_ij\_reload=RELOAD\_ON\_SAVE



\## 作者

庄雅菁



\## 日期



2026年10月







