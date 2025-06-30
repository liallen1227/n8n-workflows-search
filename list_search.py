from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time, random, os, glob

# 建立 driver
def create_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# 擷取總數
def get_counts(driver):
    text = driver.find_element(By.XPATH, "//*[@id='__nuxt']/section[2]/div/div[4]/p").text
    parts = text.split()
    return int(parts[1]), int(parts[4])

# 存檔
def save_batch(part_num, all_links):
    df = pd.DataFrame(all_links)
    filename = f"n8n_workflows_part_{part_num}.csv"
    df.to_csv(filename, index=False, encoding="utf-8")
    print(f"儲存 {filename}，共 {len(df)} 筆")

# 合併 CSV
def merge_csv_files():
    files = glob.glob("n8n_workflows_part_*.csv")
    all_dfs = [pd.read_csv(f) for f in files]
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_csv("n8n_workflows_all.csv", index=False, encoding="utf-8")
    print("合併完成")

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

    scroll_step = 530
    scroll_pause = 0.5

    # 點擊 Load More
    try:
        for _ in range(3):
            current_scroll = driver.execute_script("return window.pageYOffset;")
            driver.execute_script(f"window.scrollTo(0, {current_scroll + scroll_step});")
            time.sleep(scroll_pause)

        load_more = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "div.search-results-actions.mt-8.flex.flex-row.items-center.justify-between.gap-4 > button"
            ))
        )
        load_more.click()
        time.sleep(random.uniform(1.5, 2.5))
    except:
        print("找不到可點擊的 Load More 按鈕，結束")
        break

# 存最後一次（剩餘不足 100 筆）
if len(all_links) > (part_num - 1) * 100:
    save_batch(part_num, all_links)

driver.quit()
merge_csv_files()

