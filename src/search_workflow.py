import google.generativeai as genai
import pymysql 
import os


# 設定 Gemini API 金鑰
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


# 從資料庫取出所有 workflow 描述
def get_all_workflows():
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

    cursor = conn.cursor()
    cursor.execute("SELECT title, link, description FROM n8n")
    result = cursor.fetchall()
    conn.close()
    return result


# 工作流程包裝成 prompt 格式
def build_prompt(workflows, user_query):
    prompt = f"""
你是一個 n8n 自動化流程顧問。以下是目前資料庫中的工作流程，請根據使用者輸入的需求：
「{user_query}」
回覆最相關的 workflow，包含：
1. 標題
2. 連結
3. 匹配程度（高、中、低）
4. 為什麼會選這個 workflow？

---
"""

    for i, (title, link, desc) in enumerate(workflows, 1):
        prompt += f"### Workflow {i}\n**Title**: {title}\n**Link**: {link}\n**Description**: {desc}\n\n"

    prompt += "---\n請從中分析並推薦最合適的 workflow。"

    return prompt


# 發送給 Gemini API
def query_gemini(user_query):
    workflows = get_all_workflows()
    prompt = build_prompt(workflows, user_query)

    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    user_input = input("請輸入你的需求（如：郵件自動分類）：")
    result = query_gemini(user_input)
    print("\nGemini 回覆結果：\n")
    print(result)
