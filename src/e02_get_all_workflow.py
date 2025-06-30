from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time, random, os, glob

file_folder = "../data/"
df = pd.read_csv(f"{file_folder}n8n_workflows_all.csv", encoding="utf-8")
links = df["link"].tolist()
titles = df["title"].tolist()


def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def save_batch(part_num, all_links):
    df = pd.DataFrame(all_links)
    file_name = f"{file_folder}n8n_workflows_part_{part_num}.csv"
    df.to_csv(file_name, index=False, encoding="utf-8")
    print(f"儲存 {file_name}，共 {len(df)} 筆")


def get_saved_count():
    files = glob.glob("n8n_workflows_part_*.csv")
    count = 0
    for f in files:
        try:
            df = pd.read_csv(f)
            count += len(df)
        except:
            continue
    return count


def merge_csv_files():
    files = glob.glob(f"{file_folder}n8n_workflows_part_*.csv")
    all_dfs = [pd.read_csv(f) for f in files]
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df.drop_duplicates(subset=["title"])
    final_df.to_csv("n8n_workflows_final.csv", index=False, encoding="utf-8")
    print("合併完成")

    for f in files:
        os.remove(f)
        print(f"已刪除：{f}")


start_idx = get_saved_count()
print(f"從第 {start_idx + 1} 筆繼續擷取...")

driver = create_driver()

body_list = []
fail_list = []
part_num = (start_idx // 100) + 1
max_retries = 2

for idx, (title, url) in enumerate(zip(titles, links)):
    title = titles[idx]
    url = links[idx]
    success = False

    for attempt in range(max_retries + 1):

        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#__nuxt > section > div > div.relative.z-10 > section:nth-child(2) > div > div > div.lg\:w-8\/12 > div > div"))
            )
            
            body = driver.find_element(By.CSS_SELECTOR, "#__nuxt > section > div > div.relative.z-10 > section:nth-child(2) > div > div > div.lg\:w-8\/12 > div > div").text
            # print(body)
            body_list.append(
                {
                    "title": title,
                    "link": url,
                    "description": body
                }
            )   

            print(f"已擷取第 {start_idx + idx + 1} 筆")

            time.sleep(random.uniform(1, 3))
            success = True
            break

        except Exception as e:
            print(f"第 {idx+1} 筆失敗：{url}\n錯誤：{e}")
            time.sleep(random.uniform(1, 2))

    if not success:
        fail_list.append({
            "title": title,
            "link": url,
            "description": None
        })

    if (idx + 1) % 100 == 0:
        save_batch(part_num, body_list)
        body_list.clear()
        part_num += 1

if body_list:
    save_batch(part_num, body_list)

driver.quit()

fail_df = pd.DataFrame(fail_list)
fail_df.to_csv(f"{file_folder}n8n_workflows_fail.csv", index=False, encoding="utf-8")

merge_csv_files()
print("完成儲存")