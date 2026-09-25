import os
import json
import datetime

class Read:
    def __init__(self, share_data):
        self.share_data = share_data

    def Read_QR(self, qr_data):
        """
        QRコードのデータを解析して、秘密復元に必要な情報を抽出する関数
        QRコードのデータ形式は以下の通りとする:
        1行目: 復元後のファイルのパス
        2行目: シェアの強度 (share_strength)
        3行目: 復元に必要なシェアの数 (threshold)
        4行目: Rampの数 (ramp)
        5行目: シェアの長さ (secret_length)
        6行目以降: 各シェアの情報 (share_index, data_length, data...)
        例:
        /path/to/secret.txt
        3
        2
        10
        1
        5
        12345...
        2
        5
        67890...
        3
        5
        54321...
        """
        share_block = []
        share_list = []
        
        # 修正箇所: 空行を除外してリスト化し、'' が混入するのを防ぐ
        data = [line for line in qr_data.split('\n') if line.strip() != '']

        file_path = data[0]
        share_strength = int(data[1])
        threshold = int(data[2])
        ramp = int(data[3])
        secret_length = int(data[4])
        data_index = 5

        for i in range(share_strength):
            if data_index >= len(data):
                break
            
            share_index = int(data[data_index])
            data_index += 1
            
            if data_index >= len(data):
                break
                
            data_length = int(data[data_index])
            data_index += 1
            share_list.append(share_index)

            for j in range(data_length):
                if data_index >= len(data):
                    break
                    
                # 修正箇所: ゴミデータ（...や空白）を除去してから数値に変換する
                val = data[data_index].replace('...', '').strip()
                share_block.append(int(val))
                data_index += 1

            share_list.append(share_block)
            share_block = []
            self.share_data.append(share_list)
            share_list = []

        return threshold, ramp, secret_length, share_index,share_strength

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(script_dir, "database", "shares.json")
    database = {}

    # ディレクトリが存在しない場合は作成（ファイル作成時のエラー防止）
    os.makedirs(os.path.dirname(db_file), exist_ok=True)

    share_file_name = input("シェアのファイル名を入力してください（例: test.txt）:")
    file_num = int(input("入力するシェアのファイルの数を入力してください:"))
    share_level = int(input("シェアの強度を入力してください（例: 3）:"))
    key_id = int(input("キーIDを入力してください（例: 1）:"))

    # 既存のデータベースがあれば読み込む
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            try:
                database = json.load(f)
            except json.JSONDecodeError:
                pass
    
    current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # シェアファイルをJSONに変換する
    for i in range(file_num):
        share_file_path = os.path.join(script_dir, "shares", f"{share_file_name}__lv{share_level}_{i+1}.shr")
        
        if not os.path.exists(share_file_path):
            print(f"エラー: {share_file_path} が見つかりません。")
            continue

        with open(share_file_path, 'r', encoding='utf-8') as f:
            share_data_text = f.read()
        
        print(f"シェアファイル '{share_file_path}' を読み込みました。")

        data = Read([])
        params = data.Read_QR("-\n" + share_data_text)
        
        user_name = f"unknown_user_{current_date}_{i+1}"
        icid = f"unknown_ic_{current_date}_{i+1}"

        # 修正箇所1: データベースにicidのエントリが存在しない場合は枠組みを作成
        if icid not in database:
            database[icid] = {
                "user_name": user_name,
                "threshold": params[0],
                "ramp": params[1],
                "length": params[2],
                "qr_id": params[3],
                "strength": params[4],
                "key_id": key_id,
                "share_data": data.share_data
            }

    # 全ファイルの処理が終わった後に一度だけJSONへ書き込む
    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=4, ensure_ascii=False)

    print("\n--- 完了 ---")