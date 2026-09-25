import os
from datetime import datetime

def write_log(log_type, key_id="-", key_value="-", user_id="-", user_name="-", action="-"):
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
        text = f"[{timestamp}] <USER> key_id:{str(key_id):>2}, key_value:{str(key_value):>20}, user_id:{str(user_id):>2}, user_name:{user_name}"
        _save_to_file(text)

    elif log_type == "DOOR":
        text = f"[{timestamp}] <DOOR> key_id:{str(key_id):>2}, Action: {action:<10}  (Status Changed)"
        _save_to_file(text)

    elif log_type == "ERROR":
        text = f"[{timestamp}] <ERR!> Message: {action}"
        _save_to_file(text)
