import time
import sqlite3
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURATION ---
# Save DB inside the "最終課題" folder or current directory
DB_NAME = "recruitment_data.db"
MAX_PAGES = 5

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            salary_text TEXT,
            salary_min INTEGER,
            salary_max INTEGER,
            description TEXT,
            url TEXT UNIQUE
        )
    ''')
    conn.commit()
    return conn

def clean_salary(salary_str):
    try:
        nums = re.findall(r'([0-9,]+)', salary_str)
        cleaned_nums = [int(n.replace(',', '')) for n in nums if n.replace(',', '').isdigit()]
        if len(cleaned_nums) >= 2:
            return cleaned_nums[0], cleaned_nums[1]
        elif len(cleaned_nums) == 1:
            return cleaned_nums[0], cleaned_nums[0]
        else:
            return 0, 0
    except:
        return 0, 0

def main():
    conn = init_db()
    cursor = conn.cursor()

    print("ブラウザを起動中...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    
    url = "https://www.hellowork.mhlw.go.jp/kensaku/GECA110010.do?action=initDisp&screenId=GECA110010"
    driver.get(url)

    print("\n" + "="*60)
    print("一時停止中: Chromeウィンドウで検索を行ってください。")
    print("1. キーワード（例: データサイエンティスト）と勤務地（東京）を入力")
    print("2. 青い「検索」ボタンをクリック")
    print("3. 求人一覧が表示されたら、ここに戻って Enter キーを押してください")
    print("="*60 + "\n")
    input("Press Enter to start scraping...")

    page_count = 0
    while page_count < MAX_PAGES:
        print(f"ページ {page_count + 1} を取得中...")
        
        try:
            # General table row selector for Hello Work
            job_rows = driver.find_elements(By.CSS_SELECTOR, "tr")
        except:
            break

        jobs_saved = 0
        for row in job_rows:
            try:
                text = row.text
                if "円" not in text or "求人番号" not in text:
                    continue
                
                lines = text.split('\n')
                title = lines[0]
                salary_text = "0"
                for line in lines:
                    if "円" in line and "〜" in line:
                        salary_text = line
                        break
                
                min_sal, max_sal = clean_salary(salary_text)
                
                cursor.execute('''
                    INSERT INTO jobs (title, salary_text, salary_min, salary_max, description)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, salary_text, min_sal, max_sal, text))
                conn.commit()
                jobs_saved += 1
            except:
                continue

        print(f"  -> {jobs_saved} 件保存しました")

        try:
            next_btn = driver.find_element(By.LINK_TEXT, "次へ進む")
            next_btn.click()
            time.sleep(3)
            page_count += 1
        except:
            print("次のページが見つかりません。終了します。")
            break

    conn.close()
    driver.quit()

if __name__ == "__main__":
    main()