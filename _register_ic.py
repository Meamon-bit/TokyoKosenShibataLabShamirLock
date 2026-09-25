import json
import os
from scan_ic import MyCardReader
from _scan_qrcode import scan_qrcode
from _read import Read

def main():
    """
    1. ユーザー名の入力
    2. ICカードの読み取り
    3. QRコードのスキャン
    4. QRコードのデータ解析
    5. JSONファイルへの保存
     - 既存のデータがあれば読み込んで追記、なければ新規作成
     - ICIDをキーにして保存
     - 保存する情報: ユーザー名、ICID、秘密復元の閾値、ramp、シェアの長さ、シェアの固有番号、そのシェアの重さ、key_id、シェアのデータ
     - 保存先ファイル: ./database/shares.json
     - 保存後、ユーザーに完了メッセージを表示
     - エラーが発生した場合は適切なエラーメッセージを表示して処理を中断
     - 成功した場合は保存した情報の概要を表示
     - 例: "ユーザー 'Alice' の情報を './database/shares.json' に保存しました。"
     - 例: "データの解析に失敗しました。フォーマットが正しくありません。"
     - 例: "ICカードの読みとりに失敗しました"
     - 例: "QRコードの読み取りに失敗、またはタイムアウトしました。"
     - 例: "ユーザー 'Bob' の情報を './database/shares.json' に保存しました。"
    """
    #user_nameに入れる値を取得します
    username = input("登録するユーザー名を入力してください：")
    
    #ICカードの読み取り(scan_ic.pyを使ってます)
    print("\n--- STEP 1: ICカードをタッチしてください ---")
    IC_reader = MyCardReader()
    icid = IC_reader.read_id()

    if not icid:
        print("ICカードの読みとりに失敗しました")
        return
    print(f"ICIDを取得しました: {icid}")

    #QRコードのスキャン(scan_qrcode.pyの活用)
    print("\n--- STEP 2: QRコードをカメラにかざしてください ---")
    qr_raw_data = scan_qrcode()

    if qr_raw_data == "Error" or not qr_raw_data:
        print("QRコードの読み取りに失敗、またはタイムアウトしました。")
        return
    print("QRコードのスキャンに成功しました。")

    # 4. QRデータの解析 (Read.py の活用)
    print("\n--- STEP 3: データを解析中 ---")
    share_storage = []
    qr_parser = Read(share_storage)
    
    # Read_QRの戻り値を受け取る (threshold, ramp, secret_length, share_index)
    # 同時に qr_parser.share_data に解析結果が格納される
    params = qr_parser.Read_QR(qr_raw_data)

    if not params:
        print("データの解析に失敗しました。フォーマットが正しくありません。")
        return
    
    
    # 5. JSONファイルに情報を保存
    save_data = {
        "user_name": username,
        "icid": icid,
        "threshold": params[0],#秘密復元の閾値
        "ramp": params[1],
        "length": params[2],#シェアの長さ
        "qr_id": params[3],#シェアの固有番号が入っている
        "strength": params[4],#そのシェアの重さ
        "key_id": 1,#復元元のファイルによって1から番号振る予定（今は複数作るつもりないので1で決め打ち）
        "share_data": qr_parser.share_data
    }

    # 保存処理 (既存のファイルがあれば追記、なければ新規作成)
    db_file = "./database/shares.json"
    database = {}
    
    if os.path.exists(db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            try:
                database = json.load(f)
            except json.JSONDecodeError:
                database = {}

    # ICIDをキーにして保存
    database[icid] = save_data

    with open(db_file, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=4, ensure_ascii=False)

    print(f"\n--- 完了 ---")
    print(f"ユーザー '{username}' の情報を '{db_file}' に保存しました。")

if __name__ == "__main__":
    main()