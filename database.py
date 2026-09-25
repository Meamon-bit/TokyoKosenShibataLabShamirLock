import json
import write_log
import os
import hashlib
import remove

def read_database(ic_id, share_data):
    """
    share.jsonからic_idに対応するデータを読み込み、解析してshare_dataに追加する関数。
    
    引数:
        ic_id (str or int): JSONファイルからデータを検索するためのID
        share_data (list): 解析したシェアデータを格納するためのリスト（参照渡しで更新される）
        
    戻り値:
        tuple: (閾値, ランプ値, 秘密データの長さ, 最後に処理したシェアのインデックス, key_id, user_name) もしくは None（エラー時）
               ※エラー時はNoneを返す
    """

    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, "database", "shares.json")

    # 1. JSONファイルからデータを読み込む
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        write_log.write_log("ERROR", action="Can't find out the share.json")
        return None
    except json.JSONDecodeError:
        write_log.write_log("ERROR", action="The JSON file format is incorrect")
        return None

    # 2. ic_idに対応する文字列データを取得する
    ic_id_str = str(ic_id) # JSONのキーは文字列として扱われるため変換
    if ic_id_str not in json_data:
        print(f"エラー: 指定された ic_id ({ic_id_str}) のデータが見つかりません。")
        write_log.write_log("ERROR", action="Can't find out the IC_ID")
        return None

    target_node = json_data[ic_id_str]

    # 3. ヘッダー情報の解析
    shares = list(target_node.get('share_data', []))
    share_data.extend(shares)
    strength = int(target_node.get('strength', 0))
    threshold = int(target_node.get('threshold', 0))
    ramp = int(target_node.get('ramp', 0))
    length = int(target_node.get('length', 0))
    
    last_share_index = int(shares[-1][0]) if shares else None

    key_id = target_node.get('key_id', '-')
    user_name = target_node.get('user_name', '-')

    return threshold, ramp, length, last_share_index, key_id, user_name



def check_key(key_id):
    """
    key.jsonからkey_idに対応するデータを読み込み、復元された文字列valueと一致するか確かめる
    
    引数:
        key_id (str or int): JSONファイルからデータを検索するためのID
        
    戻り値:
        true/false
    """
    
    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, "database", "keys.json")

    # 比較用のデータ（復元された鍵）読み込み
    file_path = "data_restored.txt"
    print("start database check")
    try:
        with open(file_path, "r", encoding='utf-8', errors="ignore") as f:
            value = f.read()
            print(value)
            hash_value = hashlib.sha256(value.encode('utf-8')).hexdigest()
            print(hash_value)
    except FileNotFoundError:
        write_log.write_log("ERROR",action="Can't open the data_restored.txt")
        return None
    
    remove.remove_file(file_path)
    
    # JSONファイルからデータを読み込む
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    except FileNotFoundError:
        write_log.write_log("ERROR", action="Can't find out the keys.json")
        return None
    except json.JSONDecodeError:
        write_log.write_log("ERROR", action="The JSON file format is incorrect")
        return None
    
    key_id_str = str(key_id)
    if key_id_str not in json_data:
        print(f"エラー: 指定された key_id ({key_id_str}) のデータが見つかりません。")
        write_log.write_log("ERROR", action="Can't find out the KEY_ID")
        return None
    
    target_node = json_data[key_id_str]
    json_value = target_node.get('value','')
    print(json_value)
    if json_value.strip() == hash_value.strip():
        return True
    else:
        return False
