```python
"""
查询所有表中带url的字段 取值包含xxx.com内容的字段
"""
import pymysql

# MySQL连接配置
DB_HOST = '127.0.0.1'           # 数据库主机
DB_USER = 'root'                # 数据库用户名
DB_PASSWORD = '123456'          # 数据库密码
DB_NAME = 'INFORMATION_SCHEMA'  # 数据库名称

# 连接到MySQL数据库
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# 创建游标对象
cursor = connection.cursor()

def get_tables_with_url_fields():
    # 查询所有包含'url'字段的表和字段
    query = """
    SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE COLUMN_NAME LIKE "%url%";
    """
    cursor.execute(query)
    return cursor.fetchall()

def search_url_in_table(table_schema, table_name, column_name):
    # 查询表中字段包含'xxx.com'的记录
    query = f"SELECT * FROM {table_schema}.`{table_name}` WHERE {column_name} LIKE '%xxx.com%' limit 1"
    cursor.execute(query)
    results = cursor.fetchall()

    if results:
        print(f"{table_schema},{table_name},{column_name}");

def main():
    try:
        # 获取所有包含'url'字段的表和字段
        tables_and_columns = get_tables_with_url_fields()

        # 逐个表和字段查询
        for table_schema, table_name, column_name in tables_and_columns:
            search_url_in_table(table_schema, table_name, column_name)

    except Exception as e:
        print(f"发生错误: {e}")

    finally:
        # 关闭游标和连接
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()

```