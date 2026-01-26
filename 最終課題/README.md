最終課題（求人テーマ）
日本における求人減速の早期警戒シグナル（有効求人倍率・新規求人倍率）

1. 目的（何をした課題か）
本課題では、講義で学んだ Webスクレイピング / DB構築 / SQLクエリ / 可視化  を一連の流れとして実装し、求人市場（求人需給）の変化をデータから検証する。
 
JILPT（労働政策研究・研修機構）の統計ページから 有効求人倍率  と 新規求人倍率 （セグメント別）を取得し、SQLiteに保存したうえで、月次データ（年平均を除外）を用いて 求人減速の兆候（Early Warning）  を確認する。
 
2. 分析テーマ（求人）とデータソース
 テーマ：求人（労働市場の需給変化） 
 データソース：JILPT 労働統計 
   対象ページ：`https://www.jil.go.jp/kokunai/statistics/shuyo/0208.html`
 取得指標（セグメント別） 
   有効求人倍率（ストック）
   新規求人倍率（フロー）
   セグメント：  
     全体（新卒除き＋パート含む）  
     正規（新卒・パート除く）  
     パートタイム  
 
 
3. 仮説（検証したいこと）
 仮説1（セグメント感応度）   
  2024年10月～2025年11月にかけて求人需給は緩和し、特に パートタイム  で求人倍率（有効・新規）の低下が 正規（新卒・パート除く）  より大きい。
 
仮説2（採用流入の弱まり）   
  採用流入ギャップ（新規求人倍率 − 有効求人倍率）  が縮小し、新規採用の「流入（新規求人）」が弱まっている。
 
 

4. 実装の全体像（パイプライン）
    1. スクレイピング （`scrap.py`）  
        WebページからHTMLテーブルを取得し、対象データを抽出・前処理する。
    2. DB保存 （`db.py`）  
        SQLite DBを作成し、テーブルへ保存する。
    3. SQL抽出→分析→可視化 （`analysis.ipynb`）  
        SQLiteに対してSQLクエリを発行して月次データを取得し、仮説検証・可視化を行う。
 
 
 
5. ファイル構成（何がどこにあるか）
 `scrap.py`  
   JILPTページへアクセス（`requests.get`）  
   HTMLテーブル抽出（`pandas.read_html`）  
   対象テーブル判定（求人倍率を含む表を選択）  
   クリーニング（列名整形・数値化など）  
   DB保存処理を呼び出す
 
 `db.py`  
   SQLite接続・テーブル作成  
   DataFrameを `job_offers_jp` に保存  
   （必要に応じて）SELECTクエリでのデータ取得を支援する
 
 `analysis.ipynb`  
   SQLiteから `月 != '平均'` を条件に月次データを抽出  
   対象期間（開始/終了）を自動表示  
   仮説1：開始→終了の変化量・変化率を算出  
   仮説2：ギャップ（新規−有効）を算出して縮小を検証  
   図1～図3をPNGで保存（日本語タイトル・凡例）
 
 
 6. DB設計（保存先・テーブル）
 DBファイル ：`data.db`  
   ※DBファイルはローカル生成物として扱い、GitHubにはアップロードしない運用（`.gitignore`で除外）
 テーブル名 ：`job_offers_jp`
 主な列 
   `年`, `月`
   `有効求人倍率_...`（3セグメント）
   `新規求人倍率_...`（3セグメント）
 
 
 
7. 実行手順（再現方法）

    7.1 事前準備（仮想環境は任意）
    例：
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -U pip
    pip install requests pandas matplotlib

    7.2 スクレイピング→DB保存（scrap.py）
    bash
    Copy code
    python scrap.py
    実行後、SQLite DB（data.db）が作成され、job_offers_jp に保存される。
 
    7.3 分析・可視化（analysis.ipynb）
    Jupyterで analysis.ipynb を開き、上から順に実行する。
 
    Notebook内で使用するSQL（概念）：
    sql
    Copy code
    SELECT *
    FROM job_offers_jp
    WHERE 月 != '平均'
    ORDER BY CAST(年 AS INT), CAST(月 AS INT);


8. 出力（成果物：スライド貼り付け用）
    analysis.ipynb 実行により、以下の画像が生成される（PNG）。
 
    図1_有効求人倍率_月次_セグメント別推移.png
    図2_新規求人倍率_月次_セグメント別推移.png
    図3_採用流入ギャップ_新規-有効_推移.png
 
9. スクレイピング遵守事項（robots / 利用規約 / 負荷配慮）
    robots.txt の確認
 
    robots.txt：https://www.jil.go.jp/robots.txt
 
    対象URL：https://www.jil.go.jp/kokunai/statistics/shuyo/0208.html
 
    確認結果：対象URLは取得許可（Permission: GRANTED）であることを確認
 
    サーバ負荷への配慮
 
    time.sleep() を用いてアクセス間隔を確保し、過度な連続アクセスを避けた。
 
    利用規約の確認
 
    利用規約も確認し、短時間での大量アクセス・不要な再取得を避ける運用とした。

 
10. 備考（提出用）
GitHub提出ブランチ：最終課題
 
提出物（別途）：Google Slide
 

