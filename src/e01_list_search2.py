from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time, random, os, glob

# print("cwd:", os.getcwd())

# 建立 driver
def create_driver(headless=True):
    options = Options()
    options.binary_location = "/usr/bin/chromium-browser"
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    service = Service()
    return webdriver.Chrome(service=service, options=options)

# 擷取總數
def get_counts(driver):
    text = driver.find_element(By.XPATH, "//*[@id='__nuxt']/section[2]/div/div[4]/p").text
    parts = text.split()
    return int(parts[1]), int(parts[4])

file_folder = "../data/"

# 存檔
def save_batch(part_num, all_links):
    df = pd.DataFrame(all_links)
    filename = f"{file_folder}n8n_workflows_part_{part_num}.csv"
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"儲存 {filename}，共 {len(df)} 筆")

# 合併 CSV 檔
def merge_csv_files():
    files = glob.glob(f"{file_folder}n8n_workflows_part_*.csv")
    all_dfs = [pd.read_csv(f) for f in files]
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df = final_df.drop_duplicates(subset=["title"])
    final_df.to_csv(f"{file_folder}n8n_workflows_all.csv", index=False, encoding="utf-8")
    print("合併完成")

    for f in files:
        os.remove(f)
        print(f"已刪除：{f}")

# 主流程
driver = create_driver()
driver.get("https://n8n.io/workflows/categories/ai/")

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div.search-results-list"))
)

_, max_count = get_counts(driver)
print(f"總共 {max_count} 筆資料")

all_links = []
part_num = 1

scroll_step = 550
scroll_pause = 0.4
max_scroll_attempts = 15

while True:
    items = driver.find_elements(By.CSS_SELECTOR, "div.search-results-list > div > a")
    print(f"目前共 {len(items)} 筆")

    for i in range(len(all_links), len(items)):
        try:
            title = items[i].find_element(By.CSS_SELECTOR, "h3").text
            href = items[i].get_attribute("href")
            all_links.append({"title": title, "link": href})
        except:
            continue

    # 每 100 筆存檔
    if len(all_links) >= part_num * 100:
        save_batch(part_num, all_links)
        part_num += 1

    try:
        # 找到 Load More 
        load_more = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "div.search-results-actions.mt-8.flex.flex-row.items-center.justify-between.gap-4 > button"))
        )

        # 滾動直到按鈕可點擊
        for _ in range(max_scroll_attempts):
            try:
                WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR,
                        "div.search-results-actions.mt-8.flex.flex-row.items-center.justify-between.gap-4 > button"))
                )
                break
            except:
                driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_step)
                time.sleep(scroll_pause)
        else:
            break

        # 滾進來後再用 scrollIntoView 以防萬一
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", load_more)
        time.sleep(0.5)

        load_more.click()
        time.sleep(random.uniform(1.5, 2.5))

    except Exception as e:
        print(e)
        break

# 存最後一次（剩餘不足 100 筆）
if len(all_links) > (part_num - 1) * 100:
    save_batch(part_num, all_links)

driver.quit()
merge_csv_files()

