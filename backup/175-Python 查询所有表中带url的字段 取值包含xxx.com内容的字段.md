### 查找字段生成csv

```python
"""
查询所有表中字段名包含指定关键字，且取值包含指定内容的字段。

用法示例：
    python search_url_fields.py --column-pattern url --value-pattern xxx.com
    python search_url_fields.py -c url -v xxx.com --limit 5
"""

import argparse
import sys

import pymysql

# MySQL 连接配置（可改为从环境变量读取）
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "123456"
DB_NAME = "INFORMATION_SCHEMA"


def parse_args():
    parser = argparse.ArgumentParser(
        description="查询所有表中字段名匹配指定模式、且取值包含指定内容的字段"
    )
    parser.add_argument(
        "-c", "--column-pattern",
        required=True,
        help="字段名匹配模式，如 url（对应 LIKE '%%url%%'）",
    )
    parser.add_argument(
        "-v", "--value-pattern",
        required=True,
        help="字段取值匹配内容，如 xxx.com（对应 LIKE '%%xxx.com%%'）",
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=1,
        help="每个字段最多检查的行数（默认 1）",
    )
    parser.add_argument(
        "--host", default=DB_HOST, help=f"数据库主机（默认 {DB_HOST}）"
    )
    parser.add_argument(
        "--user", default=DB_USER, help=f"数据库用户名（默认 {DB_USER}）"
    )
    parser.add_argument(
        "--password", default=DB_PASSWORD, help="数据库密码"
    )
    parser.add_argument(
        "--database", default=DB_NAME, help=f"数据库名（默认 {DB_NAME}）"
    )
    return parser.parse_args()


def get_tables_with_matching_fields(cursor, column_pattern):
    """
    查询所有包含匹配字段名的表和字段。
    使用参数化查询避免 SQL 注入。
    """
    query = """
        SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE COLUMN_NAME LIKE %s
          AND TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
    """
    cursor.execute(query, (f"%{column_pattern}%",))
    return cursor.fetchall()


def search_value_in_table(cursor, table_schema, table_name, column_name, value_pattern, limit):
    """
    查询表中指定字段的取值是否包含目标内容。
    返回 True 表示命中。
    """
    # 表名和字段名用反引号包裹，防止关键字冲突
    query = (
        f"SELECT 1 FROM `{table_schema}`.`{table_name}` "
        f"WHERE `{column_name}` LIKE %s "
        f"LIMIT %s"
    )
    try:
        cursor.execute(query, (f"%{value_pattern}%", limit))
        return cursor.fetchone() is not None
    except pymysql.err.ProgrammingError as e:
        # 某些字段可能不是字符串类型，LIKE 会报错，跳过即可
        print(f"  [跳过] {table_schema}.{table_name}.{column_name} 类型不支持 LIKE 查询：{e}", file=sys.stderr)
        return False


def main():
    args = parse_args()

    connection = None
    cursor = None
    try:
        connection = pymysql.connect(
            host=args.host,
            user=args.user,
            password=args.password,
            database=args.database,
            charset="utf8mb4",  # 处理中文编码
        )
        cursor = connection.cursor()

        tables_and_columns = get_tables_with_matching_fields(cursor, args.column_pattern)
        print(f"共找到 {len(tables_and_columns)} 个字段名包含 '{args.column_pattern}' 的字段\n")

        hit_count = 0
        for table_schema, table_name, column_name in tables_and_columns:
            if search_value_in_table(
                cursor, table_schema, table_name, column_name,
                args.value_pattern, args.limit,
            ):
                print(f"{table_schema},{table_name},{column_name}")
                hit_count += 1

        print(f"\n命中 {hit_count} 个字段包含 '{args.value_pattern}'")

    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


if __name__ == "__main__":
    main()

```

### 批量替换

```sh
#!/usr/bin/bash
# 设置当前脚本使用的编码
export LANG=zh_CN.UTF-8
export LC_ALL=zh_CN.UTF-8

# 数据库连接配置
DB_HOST="127.0.0.1"
DB_PORT="3306"
DB_USER="root"
DB_PASSWORD="123456"
# 输入文件路径
INPUT_FILE="/root/test.csv"

# 检查输入文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
    echo "文件 $INPUT_FILE 不存在。"
    exit 1
fi
# 逐行读取文件内容
while IFS=$',' read -r DB_NAME TABLE_NAME COLUMN_NAME; do
    # 构建SQL更新语句
    SQL="USE $DB_NAME; UPDATE $DB_NAME.$TABLE_NAME SET $COLUMN_NAME = REPLACE($COLUMN_NAME, 'aaa', 'bbb') WHERE $COLUMN_NAME LIKE '%aaa%';"
    # 使用mysql客户端执行SQL语句
    mysql -u"$DB_USER" -p"$DB_PASSWORD" -h"$DB_HOST" -P"$DB_PORT" -e "$SQL"
    if [ $? -eq 0 ]; then
        echo "在 $DB_NAME.$TABLE_NAME 的 $COLUMN_NAME 列中替换成功"
    else
        echo "在 $DB_NAME.$TABLE_NAME 的 $COLUMN_NAME 列中替换失败"
    fi
done < "$INPUT_FILE"

echo "替换完成"
```