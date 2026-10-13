

# ========== 1. 测试查询所有图书 ==========

def test_get_all_books(api_url):
    """TC-01：查询所有图书，应该返回列表"""
    response=api_url.get_all_book()
    data=api_url.assert_success(response)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_get_all_books_data_format(api_url, clean_books):
    """TC-07：验证返回的数据格式包含所有字段"""
    response=api_url.get_all_book()
    data = response.json()
    # 取第一条数据验证字段
    book = data["data"][0]
    expected_fields = ["id", "title", "author", "stock", "created_time","price"]
    for field in expected_fields:
        assert field in book, f"缺少字段: {field}"#断言这个字段在book中，若不在则返回“缺少字段: {field}”

    # 验证数据类型
    assert isinstance(book["id"], int)
    assert isinstance(book["title"], str)
    assert isinstance(book["author"], str)
    assert isinstance(book["price"], float)

# ========== 2. 测试查询单本图书 ==========

def test_get_one_book_exists(api_url, clean_books):
    """TC-02：查询存在的图书，返回详情"""
    response=api_url.get_book(1)
    data=api_url.assert_success(response)
    assert data["data"]["id"] == 1
    assert data["data"]["title"] == "测试书1"

def test_get_one_book_not_exists(api_url):
    """TC-03：查询不存在的图书，返回 404"""
    response=api_url.get_book(999)
    data=api_url.assert_error(response,404)
    assert data["message"] == "图书不存在"

def test_get_one_book_0_id(api_url):
    """TC-04：查询id为0，返回404"""
    response=api_url.get_book(0)
    api_url.assert_error(response,404)

def test_get_one_book_negative_id(api_url):
    """TC-05：查询负数 ID，返回 404"""
    response=api_url.get_book(-1)
    assert response.status_code==404#这里不用封装是因为这里的错误是html错误，被flask框架拦截了，无法使用json()S

# ========== 3. 测试创建图书 ==========

def test_create_book_success(api_url, clean_books):
    """TC-08：正常创建图书"""
    payload = {
        "title": "Pytest 测试书",
        "author": "Pytest 作者",
        "price": 88.00,
        "stock": 50
    }
    response = api_url.create_book(payload)
    data=api_url.assert_success_post(response)
    assert data["data"]["title"] == "Pytest 测试书"
    assert data["data"]["author"] == "Pytest 作者"

def test_create_book_only_title_author(api_url,clean_books):
    """TC-09:测只填必填字段，code为200"""
    payload={"title":"测试书名","author":"测试作者"}
    response = api_url.create_book(payload)
    data = api_url.assert_success_post(response)
    assert  data["data"]["price"]==0.00
    assert  data["data"]["stock"]==0

def test_create_book_missing_body(api_url):
    """TC-10：不传 Body，返回 400"""
    response = api_url.create_book(None)
    data = api_url.assert_error(response, 400)
    assert "请求体必须是有效的JSON" in data["error"]

def test_create_book_missing_title(api_url, clean_books):
    """TC-11：缺少 title，返回 400"""
    payload = {"author": "测试作者", "price": 30.00}
    response = api_url.create_book(payload)
    data=api_url.assert_error(response,400)
    assert "书名" in data["message"]

def test_create_book_missing_author(api_url,clean_books):
    """TC-12：缺少 author，返回 400"""
    payload={"title":"测试作者","price":99.00}
    response = api_url.create_book(payload)
    data=api_url.assert_error(response,400)
    assert "作者" in data["message"]

def test_create_book_extra(api_url,clean_books):
    """TC-13:传额外字段，返回201"""
    payload={"title":"测试书名","author":"测试作者","stock":99,"price":99.99,"size":87}
    response = api_url.create_book(payload)
    data=api_url.assert_success_post(response)
    assert "size" not in data["data"]

# ========== 4. 测试更新图书 ==========

def test_update_book_success(api_url, clean_books):
    """TC-14：正常更新图书"""
    payload = {"title": "更新后的书名", "price": 99.00}
    response = api_url.update_book(1,payload)
    data=api_url.assert_success(response)
    assert data["data"]["title"] == "更新后的书名"
    assert data["data"]["price"] == 99.00


def test_update_book_not_exists(api_url):
    """TC-18：更新不存在的图书，返回 404"""
    payload = {"title": "不存在"}
    response = api_url.update_book(999,payload)
    api_url.assert_error(response,404)

def test_update_book_empty_body(api_url, clean_books):
    """TC-17：传空 Body，返回 400"""
    response = api_url.update_book(1,{})
    api_url.assert_error(response,400)

# ========== 5. 测试删除图书 ==========

def test_delete_book_success(api_url, clean_books):
    """TC-19：正常删除图书"""

    response =api_url.delete_book(1)

    data=api_url.assert_success(response)
    assert data["message"] == "删除成功"

    # 验证真的删了
    get_response =api_url.get_book(1)
    assert get_response.status_code == 404


def test_delete_book_not_exists(api_url):
    """TC-20：删除不存在的图书，返回 404"""
    response =api_url.delete_book(999)
    api_url.assert_error(response,404)


'''
response.status_code和data["data"]的区别
response.status_code:Web服务器/Flask框架,请求本身是否成功
data["code"]:你自己的代码（Flask接口)，业务逻辑是否成功
客户法请求，Web服务器接受请求，进行检查：这个url存在吗？
不存在直接返回HTTP404，不会执行你的代码，所以就没必要再断言data的code了。存在才会执行你的函数，
'''