import pandas as pd
from sqlalchemy import create_engine, text
import write_log

# 引数 sharenum はリスト（配列）を受け取る
def check_database(sharenum):
    # 1. DB接続設定
    url = 'postgresql://user:pass@localhost:5432/Manegmentdb'
    engine = create_engine(url)
    
    # 2. 比較用のデータ（復元された鍵）読み込み
    file_path = "data_restored.txt"
    try:
        with open(file_path, "r") as f:
            my_values = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"エラー: {file_path} が見つかりません。")
        my_values = []

    if my_values:
        print(f"DEBUG: 受け取ったIDリスト = {sharenum}")
        # 3. SQL文
        query = text("""
            SELECT
                ut.username,
                ut.userid,
                ut.shareid,
                ut.keyid
            FROM
                usertable ut
            WHERE
                ut.keyid IN (
                    SELECT keyid 
                    FROM keytable 
                    WHERE keyvalue IN :values
                )
                AND ut.shareid IN :sharenum
        """)

        try:
            if isinstance(sharenum, (list, set, tuple)):
                sharenum_param = tuple(sharenum)
            else:
                sharenum_param = (sharenum,)

            with engine.connect() as connection:
                df_result = pd.read_sql(
                    query, 
                    connection, 
                    params={'values': tuple(my_values), 'sharenum': sharenum_param}
                )

            # 4. 結果の抽出とログ記録（★ここをシンプルに確定させました）
            if not df_result.empty:
                # 照合が成功したユーザー全員分を1人ずつログに記録
                for index, row in df_result.iterrows():
                    write_log.write_log("USER", row['keyid'], "-", row['userid'], row['username'], "-")

                # 全員の記録が終わったら最後にドア開錠ログ
                write_log.write_log(log_type="DOOR")

                print(f"--- 検索結果 (照合成功: {len(df_result)}名) ---")
                for index, row in df_result.iterrows():
                    print(f"一致: {row['username']} (ID: {row['userid']})")
                
                return True
            else:
                print(f"指定された shareid {sharenum_param} は、復元された鍵のグループに存在しません。")

        except Exception as e:
            print(f"DBエラー: {e}")
    else:
        print("比較するための鍵データ（data_restored.txt）がありません。")
    return False