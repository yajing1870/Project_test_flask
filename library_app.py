from flask  import Flask,request,jsonify
import pymysql,os
from dotenv import load_dotenv
app=Flask(__name__)
#数据库配置
load_dotenv()#加载文件的意思
db_config={
    'host':os.getenv('DB_HOST','127.0.0.1'),
    'port':int(os.getenv('DB_PORT',3306)),
    'user':os.getenv('DB_USER','root'),
    'password':os.getenv('DB_PASSWORD',''),
    'charset':'utf8mb4',
    'db':os.getenv('DB_NAME','book_db')
}
#连接数据库
def get_db_connection():
    return pymysql.connect(**db_config)
#获取数据
#获取一条数据
def fetch_one(sql,params=None):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute(sql,params or ())
    result=cursor.fetchone()
    cursor.close()
    conn.close()
    return result
#获取多条数据
def fetch_all(sql,params=None):
    conn=get_db_connection()
    cursor=conn.cursor()
    cursor.execute(sql,params or ())
    result=cursor.fetchall()
    cursor.close()
    conn.close()
    return result
#进行增删改时，返回删除了更改了几行或增加的id
def execute_sql(sql,params=None):
    conn=get_db_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(sql,params or ())
        conn.commit()
        if sql.strip().upper().startswith('INSERT'):
            return cursor.lastrowid
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
#对请求体格式进行“安检”
def get_request_data():
    data=request.get_json(silent=True)
    if data is None:
        return None,jsonify({'error':"请求体必须是有效的JSON"}),400
    return data,None,None
#将pymysql中默认的元组转换成字典
def book_to_dict(book_tuple):
    return {
        "id":book_tuple[0],
        "title": book_tuple[1],
        "author": book_tuple[2],
        "stock": book_tuple[3],
        "created_time": str(book_tuple[4])if book_tuple[4] else None,
        "price": float(book_tuple[5])
    }
#CRUD
#查询所有图书
#先写sql需要查询什么，再调用查询函数获取到数据，将获取到的数据转换成字典，最后统一格式返回客户端
@app.route("/books",methods=['GET'])
def get_all_books():
    sql="select id,title,author,stock,created_time,price from books order by id"
    #这里最好不要用*
    #因为若后续需要改变数据，那你先前调用的元组就不对立
    results=fetch_all(sql)
    books=[book_to_dict(row) for row in results]#注意这里是字典列表，只是将里边的元素从元组改成了字典
    return jsonify({
        "code":0,
        "message":"success",
        "data":books
    })
#查询单本书籍
#先写sql语句，调用查询函数获取数据，要判断存不存再对单本书格式转换，再统一格式返回客户端
@app.route("/books/<int:book_id>",methods=['GET'])
def get_one_books(book_id):
    sql="select id,title,author,stock,created_time,price from books where id=%s"
    results=fetch_one(sql,(book_id,))
    if results:
        return jsonify({
            "code":0,
            "message":"success",
            "data":book_to_dict(results)
        })
    else:
        return jsonify({
            "code":404,
            "message":"图书不存在"
        }),404  # code的状态码是给程序员测试人员看的。外面的状态码是给浏览器服务器看的，例如网页找不到时显示的404
#创建图书
#创建图书需要输入请求体所以要先对请求体进行安检，然后再从安检通过的data里获取数据，再对一些特殊情况进行判断，拿到数据后写sql，更新数据库返回新建图书
@app.route("/books",methods=['POST'])
def create_book():
    data,err_res,status=get_request_data()
    if data is None:
        return err_res,status
    title=data.get("title")
    author=data.get("author")
    stock=data.get("stock",0)
    price=data.get("price",0.00)

    if not title or not author:
        return jsonify({
            "code":400,
            "message":"书名和作者不能为空"
        }),400

    sql="insert into books(title,author,stock,price) values (%s,%s,%s,%s)"
    try:
        new_id=execute_sql(sql,(title,author,stock,price))
        result=fetch_one("select id,title,author,stock,created_time,price from books where id=%s",(new_id,))
        #（new_id，)是传实际参数的意思，有占位符%s就一定要有参数
        return jsonify({
            "code":0,
            "message":"创建成功",
            "data":book_to_dict(result)
        }),201
    except Exception as e:
        return jsonify({
            "code":500,
            "message":f"创建失败:{str(e)}"
        }),500
#更新图书
#先安检请求体，检查更新图书是否存在，获取数据，判断特殊情况，更新字段，更新数据库，返回客户端
@app.route("/books/<int:book_id>",methods=['PUT'])
def update_book(book_id):
    data,err_res,status=get_request_data()
    if data is None:
        return err_res,status
    check_sql="select id from books where id =%s"
    if not fetch_one(check_sql,(book_id,)):
        return jsonify({
            "code":404,
            "message":"该图书不存在"
        }),404

    update_books=[]
    params=[]
    if 'title' in data:
        update_books.append("title=%s")
        params.append(data['title'])
    if 'author' in data:
        update_books.append("author=%s")
        params.append(data['author'])
    if 'stock' in data:
        update_books.append("stock=%s")
        params.append(data['stock'])
    if 'price' in data:
        update_books.append("price=%s")
        params.append(data['price'])
    if not update_books:
        return jsonify({
            "code":400,
            "message":"没有需要更新的字段"
        }),400

    params.append(book_id)
    sql=f"update books set {','.join(update_books)} where id =%s"
    try:
        execute_sql(sql,tuple(params))
        result=fetch_one("select id,title,author,stock,created_time,price from books where id=%s",(book_id,))
        return jsonify({
            "code":0,
            "message":"更新成功",
            "data":book_to_dict(result)
        })
    except Exception as e:
        return jsonify({
            "code":500,
            "message":f"更新失败：{str(e)}"
        }),500
#删除图书
#检查图书是否存在，sql，删除，返回客户端
@app.route("/books/<int:book_id>",methods=['delete'])
def delete_book(book_id):
    check_sql="select id from books where id=%s"
    if not fetch_one(check_sql,(book_id,)):
        return jsonify({
            "code":404,
            "message":"图书不存在"
        }),404
    sql="delete from books where id=%s"
    try:
        execute_sql(sql,(book_id,))
        return jsonify({
            "code":0,
            "message":"删除成功"
        })
    except Exception as e:
        return jsonify({
            "code":500,
            "message":f"删除失败：{str(e)}"
        }),500
if __name__ == '__main__':
    app.run(debug=True,port=5000)