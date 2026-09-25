import json
import os
from scan_ic import MyCardReader

def main():
    print("=== ICカードで登録します ===")
    
    db_file = "./database/shares.json"
    
    # 1. データベースファイルの存在確認と読み込み
    if not os.path.exists(db_file):
        print(f"エラー: ベースとなるJSONファイル '{db_file}' が見つかりません。")
        return

    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            database_dict = json.load(f)
    except json.JSONDecodeError:
        print(f"エラー: JSONファイルの形式が正しくありません。")
        return

    if not isinstance(database_dict, dict):
        print("エラー: JSONのルートが辞書構造（{ }）になっていません。")
        return

    # 2. 上から順番に未判定のデータ（キーが 'unknown_ic_' で始まるもの）を探す
    target_key = None
    for key in database_dict.keys():
        if isinstance(key, str) and key.startswith("unknown_ic_"):
            target_key = key
            break

    if target_key is None:
        print("通知: Jsonファイルに使用されていないシェア情報がありません（すべて紐づけられています）")
        return

    print(f"\n💡 未登録の枠が見つかりました: {target_key}")

    # 3. ユーザー名の入力
    username = input("\n登録するユーザー名を入力してください：").strip()
    if not username:
        print("エラー: ユーザー名が入力されていません。処理を中断します。")
        return
        
    # 4. ICカードの読み取り
    print("\n--- ICカードをタッチしてください ---")
    IC_reader = MyCardReader()
    icid = IC_reader.read_id()

    if not icid:
        print("ICカードの読みとりに失敗しました。")
        return
        
    # データの重複チェック（すでに登録済みのICIDではないか）
    if icid in database_dict:
        print(f"エラー: このICカード（ID: {icid}）は既に別のデータに登録されています。")
        return
    for data in database_dict.values():
        if isinstance(data, dict) and data.get("icid") == icid:
            print(f"エラー: このICカード（ID: {icid}）は既に内部データに登録されています。")
            return

    print(f"ICIDを取得しました: {icid}")

    # 5. データの情報を更新（中身の書き換え ＋ キーの置き換え）
    # 対象データを一度取り出す
    target_data = database_dict[target_key]
    
    # 中身の更新（user_nameを上書きし、新しくicidを追加する）
    target_data["user_name"] = username
    target_data["icid"] = icid

    # 🌟 ここで外側の見出し（キー）を古いものから新しいICIDにすり替える
    database_dict[icid] = database_dict.pop(target_key)

    # 6. ファイルへの保存（上書き）
    try:
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(database_dict, f, indent=4, ensure_ascii=False)
        print(f"\n--- 完了 ---")
#        print(f"見出しを書き換えました: '{target_key}' ➔ '{icid}'")
        print(f"ユーザー名を変更しました: '{username}'")
    except IOError as e:
        print(f"エラー: ファイルの保存に失敗しました: {e}")

if __name__ == "__main__":
    main()