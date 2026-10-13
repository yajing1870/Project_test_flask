import time
import requests
import logging
logger=logging.getLogger(__name__)
class ApiClient:
    #自动调用url，timeout，复用连接
    def __init__(self,base_url,token=None,timeout=10,max_retries=3):
        self.base_url=base_url
        self.timeout=timeout
        self.session=requests.Session()
        #最大重试次数
        self.max_retries=max_retries
        #如果有传token则更新请求头
        if token:
            self.session.headers.update({"Authorization":f"Bearer{token}"})
    #统一请求入口
    def _request(self,method,path,**kwargs):
        url=f"{self.base_url}{path}"
        kwargs.setdefault("timeout",self.timeout)

        logger.info(f"请求：{method}{url}")
        logger.info(f"参数：{kwargs.get('json') or kwargs.get('params')}")

        #重试机制
        for attempt in range(1,self.max_retries+1):
            try:
                response=self.session.request(method,url,**kwargs)
                #响应后日志
                logger.info(f"响应：{response.status_code}")
                logger.info(f"响应体:{response.text[:200]}")
                #若状态码为5XX，重新出发
                if 500<=response.status_code<600:
                    logger.warning(f"[重试]第{attempt}次，状态码{response.status_code}")
                    if attempt<self.max_retries:
                        time.sleep(1)#等待一秒后出发
                        continue
                return response
            except requests.exceptions.RequestException as e:
                logger.error(f"[异常]第{attempt}次请求失败：{e}")
                if attempt<self.max_retries:
                    time.sleep(1)
                    continue
                raise
    #封装CRUD
    #获取全部书籍
    def get_all_book(self):
        return self._request("GET","/books")
    #获取单本书
    def get_book(self,book_id):
        return self._request("GET",f"/books/{book_id}")
    #创建书籍
    def create_book(self,data):
        return self._request("POST","/books",json=data)
    #更新书籍
    def update_book(self,book_id,data):
        return self._request("PUT",f"/books/{book_id}",json=data)
    #删除书籍
    def delete_book(self,book_id):
        return self._request("DELETE",f"/books/{book_id}")
    #关闭连接
    def close(self):
        self.session.close()

    #封装断言
    def assert_success(self,response,expected_status=200):
        assert response.status_code==expected_status,f"状态码错误：期望{expected_status},实际{response.status_code}"
        data=response.json()
        assert data["code"]==0,f"业务失败：{data.get('message')}"

        return data
    def assert_error(self,response,excepted_status):
        assert response.status_code==excepted_status
        return response.json()#断言失败的用例只需要断言http状态码，不需要断言业务状态码
    def assert_success_post(self,response,expected_status=201):
        assert response.status_code==expected_status,f"状态码错误：期望{expected_status},实际{response.status_code}"
        data=response.json()
        assert data["code"]==0,f"业务失败：{data.get('message')}"
        assert data["message"] == "创建成功"
        return data
    #这里断言我分三个，第一个断言的是结果成功的且状态码为200的。
    #第二个断言的时错误的，也就是在第一步断言HTTP状态码时就不通过，，不需要在断言业务状态码。
    #第三个断言的时post的，因为post的创建成功的状态码为201，所以单独写一个