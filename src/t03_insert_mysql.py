from dotenv import load_dotenv

import pandas as pd
import pymysql
import time
import os

load_dotenv()

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
file_folder = os.path.join(base_dir, "data")
file_path = os.path.join(file_folder, "n8n_workflows_final.csv")

df = pd.read_csv(file_path, encoding="utf-8")
# print(df.columns.tolist())

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET")

conn = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    passwd=MYSQL_PASSWORD,
    db=MYSQL_DATABASE,
    charset=MYSQL_CHARSET
    )

print('Successfully connected!')

try:
    cursor = conn.cursor()
    sql_insert = """
    INSERT INTO n8n (title, link, description)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE description = VALUES(description);
    """

    df = df.where(pd.notnull(df), None)
    data = df[["title", "link", "description"]].values.tolist()
    print(f"資料筆數：{len(data)}")

    if data:
        cursor.executemany(sql_insert, data)
        conn.commit()
        print("資料已成功寫入資料庫。")
    else:
        print("無新增資料，已全部存在於資料庫中。")

except Exception as e:
    print(f"錯誤資訊: {e}")
    conn.rollback()

finally:
    cursor.close()
    conn.close()