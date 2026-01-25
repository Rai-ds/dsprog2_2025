import sqlite3
import pandas as pd

class JobDatabase:

    def __init__(self, db_name="data.db"):
        self.db_name = db_name

    def _get_connection(self):
        return sqlite3.connect(self.db_name)

    def save_data(self, df, table_name="job_offers_jp"):

        if df is None or df.empty:
            print("保存するデータがありません。")
            return

        conn = self._get_connection()
        try:
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"成功: {len(df)} 件のデータをテーブル '{table_name}' に保存しました。(DB名: {self.db_name})")
        except Exception as e:
            print(f"データベースエラー: {e}")
        finally:
            conn.close()

    def get_annual_data(self):
        
        conn = self._get_connection()
        query = "SELECT * FROM job_offers_jp WHERE 月 = '平均'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_monthly_data(self):
        conn = self._get_connection()
        
        query = "SELECT * FROM job_offers_jp WHERE 月 != '平均'"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

if __name__ == "__main__":
    db = JobDatabase()
    print("データベースクラスの初期化が完了しました。")