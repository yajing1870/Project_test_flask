import pytest
import requests
import os
import pymysql
from dotenv import load_dotenv
# 基础 URL，方便切换环境
BASE_URL = "http://127.0.0.1:5000"


@pytest.fixture(scope="session")
def api_url():
    """返回 API 基础地址"""
    return BASE_URL


@pytest.fixture(scope="function")
def clean_books():
    """
    每个测试函数执行前，清空数据并插入干净的测试数据
    scope="function" 表示每个测试函数都会执行一次
    """

    # 数据库配置
    load_dotenv()  # 加载文件的意思
    db_config = {
        'host': os.getenv('DB_HOST', '127.0.0.1'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
        'db': os.getenv('DB_NAME', 'book_db')
    }

    # 连接数据库
    conn=pymysql.connect(**db_config)
    cursor = conn.cursor()

    # 清空表
    cursor.execute("DELETE FROM books")
    # 重置自增 ID
    cursor.execute("ALTER TABLE books AUTO_INCREMENT = 1")
    # 插入两条测试数据
    cursor.execute(
        "INSERT INTO books (title, author,stock,price) VALUES (%s, %s, %s, %s)",
        ('测试书1', '测试作者1',10,30.00)
    )
    cursor.execute(
        "INSERT INTO books (title, author,stock,price) VALUES (%s, %s, %s, %s)",
        ('测试书2', '测试作者2',20,45.00)
    )

    conn.commit()
    cursor.close()
    conn.close()

#出过的问题：测试把原来数据全删了。
# 有三种办法：
# 1.设置测试数据库，book_db_test,在.env里配置测试数据库DB_NAME=book_db_test
#2.使用回滚，每个测试后自动恢复，不提交，把conn.commit改成yield    conn.rollback()
#3.提前备份

'''
开始测试
    ↓
创建 api_url（session 级别，只创建一次）
    ↓
测试函数1（如 test_get_all_books）
    ↓
执行 clean_books（function 级别）
    ├── DELETE FROM books
    ├── ALTER TABLE books AUTO_INCREMENT = 1
    ├── INSERT 测试书1
    ├── INSERT 测试书2
    └── COMMIT
    ↓
执行测试函数1的代码
    ↓
测试函数2（如 test_get_one_book）
    ↓
再次执行 clean_books（全新干净的数据）
    ├── DELETE FROM books
    ├── ALTER TABLE books AUTO_INCREMENT = 1
    ├── INSERT 测试书1
    ├── INSERT 测试书2
    └── COMMIT
    ↓
执行测试函数2的代码
    ↓
... 每个测试函数都重复这个流程 ...
'''