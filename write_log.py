import os
from datetime import datetime

def write_log(log_type, key_id="-", ic_id="-", user_name="-", action="-"):
    """
    log/(日付).logにログを保存する関数
    
    log_type: "USER", "DOOR", "ERROR", "RESET"
     - USER: ユーザの操作ログ (key_id, ic_id, user_name)
     - DOOR: ドアの状態変化ログ (key_id, action)
     - ERROR: エラーログ (actionにエラーメッセージを入れる)
     - RESET: リセットログ
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(base_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    filename = now.strftime('%Y-%m-%d') + ".log"
    file_path = os.path.join(log_dir, filename)
    
    def _save_to_file(content):
        with open(file_path, 'a', encoding='utf-8') as f:
            print(content, file=f)
    
    if log_type == "USER":
        text = f"[{timestamp}] <USER> key_id:{str(key_id):>2}, ic_id:{str(ic_id):>2}, user_name:{user_name}"
        _save_to_file(text)

    elif log_type == "DOOR":
        text = f"[{timestamp}] <DOOR> key_id:{str(key_id):>2}, Action: {action:<10}  (Status Changed)"
        _save_to_file(text)

    elif log_type == "ERROR":
        text = f"[{timestamp}] <ERR!> Message: {action}"
        _save_to_file(text)

    elif log_type == "RESET":
        text = f"[{timestamp}] <RESET>"