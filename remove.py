import os

def remove_file(file_path):
    # ファイルが存在するか確認してから削除
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"ファイル '{file_path}' を削除しました。")
    else:
        print(f"ファイル '{file_path}' は存在しません。")