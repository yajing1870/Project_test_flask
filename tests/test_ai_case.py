
#前面已经封装了requests、curd操作，也进行了session和function的操作url已提取
#现在直接开始测试
def test_add_book(api_url,clean_books):
    payload={
        "title": "Pytest 测试书",
        "author": "Pytest 作者",
        "price": 88.00,
        "stock": 50}
    res=api_url.create_book(payload)
    data=api_url.assert_success_post(res)
    assert data["data"]["title"] == "Pytest 测试书"
    assert data["data"]["author"] == "Pytest 作者"