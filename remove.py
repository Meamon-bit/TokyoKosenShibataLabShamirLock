import os

def remove_file(file_path):
    """
    指定されたファイルを削除する関数
    - file_path: 削除するファイルのパス
    """
    # ファイルが存在するか確認してから削除
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"ファイル '{file_path}' を削除しました。")
    else:
        print(f"ファイル '{file_path}' は存在しません。")