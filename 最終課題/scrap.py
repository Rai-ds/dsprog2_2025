import requests
import pandas as pd
import io
import time
from db import JobDatabase  

class JilptScraper:
    TARGET_URL = "https://www.jil.go.jp/kokunai/statistics/shuyo/0208.html"
    
    def __init__(self):
        self.headers = {'User-Agent': 'University Research Project (Student)'}

    def scrape(self):
        print(f"データ取得を開始します: {self.TARGET_URL}")
        
        try:
            time.sleep(2) 
            
            response = requests.get(self.TARGET_URL, headers=self.headers)
            response.raise_for_status() 
            response.encoding = response.apparent_encoding #

            print("HTMLを解析中...")
            html_content = io.StringIO(response.text)
            
            dfs = pd.read_html(html_content, header=[0, 1])
            
            target_df = None
            for i, df in enumerate(dfs):
                if "有効求人倍率" in str(df.columns):
                    print(f"   >>> テーブル {i} が対象データと一致しました。処理を開始します。 <<<")
                    target_df = df
                    break
            
            if target_df is None:
                print("エラー: 対象のデータテーブルが見つかりませんでした。")
                return None

            return self._clean_data(target_df)

        except Exception as e:
            print(f"スクレイピング中にエラーが発生しました: {e}")
            return None

    def _clean_data(self, df):
        print("3. データのクリーニング中...")
        
        new_columns = []
        for col in df.columns:
            parts = [str(c).strip() for c in col if "Unnamed" not in str(c)]
            clean_col = "_".join(parts)
            

            if not clean_col:
                if len(new_columns) == 0: clean_col = "年"
                elif len(new_columns) == 1: clean_col = "月"
            
            new_columns.append(clean_col)
        df.columns = new_columns 

        cleaned_rows = []
        current_year = None 
        
        for idx, row in df.iterrows():
            try:
                col0 = str(row['年']).strip()
                col1 = str(row['月']).strip()
                
                year_part = ""
                month_part = ""
                
                if "年" in col0:
                    current_year = col0.replace('年', '')
                    year_part = current_year
                    if "月" in col1:
                        month_part = col1.replace('月', '')
                    else:
                        month_part = "平均"
                
                elif (col0 == 'nan' or col0 == '') and "月" in col1:
                    year_part = current_year
                    month_part = col1.replace('月', '')
                
                if not year_part: continue

                row_data = {'年': year_part, '月': month_part}
                
                for col_name in df.columns[2:]:
                    val = str(row[col_name]).replace(',', '').replace(' ', '')
                    
                    if val.replace('.', '', 1).isdigit():
                        row_data[col_name] = float(val)
                    else:
                        row_data[col_name] = None 
                
                cleaned_rows.append(row_data)
                
            except Exception:
                continue

        print(f"   クリーニング完了: {len(cleaned_rows)} 件のデータを抽出しました。")
        return pd.DataFrame(cleaned_rows)

if __name__ == "__main__":
    scraper = JilptScraper()
    df = scraper.scrape()
    
    if df is not None:
        db = JobDatabase()
        db.save_data(df)