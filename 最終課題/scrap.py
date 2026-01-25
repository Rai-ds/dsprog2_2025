import requests
import pandas as pd
import io
import time
from db import JobDatabase  # 作成したdb.pyをインポート

class JilptScraper:
    """
    JILPT（労働政策研究・研修機構）から求人データをスクレイピングするクラス。
    課題要件：「サーバー負荷に配慮する (time.sleepの使用)」を満たしています。
    """
    
    # スクレイピング対象のURL（主要労働統計指標：職業紹介・求人倍率）
    TARGET_URL = "https://www.jil.go.jp/kokunai/statistics/shuyo/0208.html"
    
    def __init__(self):
        # 自分の身元（大学の課題用であること）をサーバーに伝えます
        self.headers = {'User-Agent': 'University Research Project (Student)'}

    def scrape(self):
        """
        データを取得し、クリーニングを行い、DataFrameとして返します。
        """
        print(f"1. データ取得を開始します: {self.TARGET_URL}")
        
        try:
            # サーバー負荷への配慮（2秒待機）
            time.sleep(2) 
            
            response = requests.get(self.TARGET_URL, headers=self.headers)
            response.raise_for_status() # エラーがあればここで停止
            response.encoding = response.apparent_encoding # 日本語の文字化け防止

            print("2. HTMLを解析中...")
            html_content = io.StringIO(response.text)
            
            # ページ内のすべてのテーブルを読み込みます（ヘッダーが2行あることを指定）
            dfs = pd.read_html(html_content, header=[0, 1])
            
            # 「有効求人倍率」という文字が含まれるテーブルを探します
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
        """
        取得した生のDataFrameを整形します。
        日本語のマルチヘッダーを結合し、結合セルの欠損値を埋めます。
        """
        print("3. データのクリーニング中...")
        
        # 1. ヘッダーの平坦化処理
        # 例: ("有効求人倍率", "パートタイム") → "有効求人倍率_パートタイム"
        new_columns = []
        for col in df.columns:
            # カラム名のパーツをアンダースコアで結合（'Unnamed' は除外）
            parts = [str(c).strip() for c in col if "Unnamed" not in str(c)]
            clean_col = "_".join(parts)
            
            # 年と月のカラム名が空になってしまうため、手動で設定
            if not clean_col:
                if len(new_columns) == 0: clean_col = "年"
                elif len(new_columns) == 1: clean_col = "月"
            
            new_columns.append(clean_col)
        df.columns = new_columns # 新しいカラム名を適用

        # 2. 結合セルの処理（「年」が入っていない行を埋める）
        cleaned_rows = []
        current_year = None # 現在処理中の「年」を記憶する変数
        
        for idx, row in df.iterrows():
            try:
                col0 = str(row['年']).strip()
                col1 = str(row['月']).strip()
                
                year_part = ""
                month_part = ""
                
                # パターンA: 「年」の列に値がある場合（新しい年のブロック開始）
                if "年" in col0:
                    current_year = col0.replace('年', '')
                    year_part = current_year
                    # 「月」列に「月」が含まれていれば月次データ、なければ年平均
                    if "月" in col1:
                        month_part = col1.replace('月', '')
                    else:
                        month_part = "平均"
                
                # パターンB: 「年」が空だが、「月」が入っている場合（同じ年の続き）
                elif (col0 == 'nan' or col0 == '') and "月" in col1:
                    year_part = current_year
                    month_part = col1.replace('月', '')
                
                # 有効なデータ行でない場合はスキップ
                if not year_part: continue

                # 辞書形式で1行分のデータを作成
                row_data = {'年': year_part, '月': month_part}
                
                # 数値データの取得（3列目以降）
                for col_name in df.columns[2:]:
                    # カンマやスペースを除去して数値に変換できるか確認
                    val = str(row[col_name]).replace(',', '').replace(' ', '')
                    
                    # 小数点を含む数値チェック
                    if val.replace('.', '', 1).isdigit():
                        row_data[col_name] = float(val)
                    else:
                        row_data[col_name] = None # 数値以外はNone（欠損値）とする
                
                cleaned_rows.append(row_data)
                
            except Exception:
                continue

        # 整形したリストをDataFrameに戻して返します
        print(f"   クリーニング完了: {len(cleaned_rows)} 件のデータを抽出しました。")
        return pd.DataFrame(cleaned_rows)

if __name__ == "__main__":
    # メイン実行処理
    scraper = JilptScraper()
    df = scraper.scrape()
    
    # データが正常に取得できたらDBに保存
    if df is not None:
        db = JobDatabase()
        db.save_data(df)